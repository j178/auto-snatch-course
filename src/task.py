# Author: John Jiang
# Date  : 2016/7/6
import os
import re
import logging
from .urls import *
from .schedule import Schedule
from .util import get, method_once, WATCHING_LIST


class Task:
    def __init__(self, **kwargs):
        self.course = kwargs.get('course')
        self.task_id = kwargs.get('task_id')
        self.teacher_name = kwargs.get('teacher_name')
        self.description = kwargs.get('description')

        self._schedules = []

        self._teacher_num = None
        self._capacity = None
        self._selected_count = None
        self._selected = None

    @method_once
    def _turn(self):
        """
        请求task的信息
        """
        logging.info('获取课程 %s-%s 的信息中', self.course.course_num, self.teacher_name)
        r = get(TASK_TURN_URL, params={'XKTaskID': self.task_id})

        match = re.search('<td.*?background="images/MenuBg.gif">.*?'
                          'TeacherNO=(\d+).*?'
                          '最大人数.*?(\d+).*?'
                          '已选人数.*?(\d+).*?'
                          '<font.*?>(.*?)</font>.*?'
                          '</td>',
                          r.text, re.DOTALL)
        if match:
            self._teacher_num = match.group(1)
            self._capacity = int(match.group(2))
            self._selected_count = int(match.group(3))
            self._selected = (match.group(4) == '已选')

        pattern = re.compile(r'<tr align="center" class="color-row[12]">.*?'
                             '<td height="20">(?P<weekday>.*?)</td>.*?'
                             '<td>(?P<section>.*?)</td>.*?'
                             '<td>(?P<span_of_weeks>.*?)</td>.*?'
                             '<td>(?P<week_type>.*?)</td>.*?'
                             '<td>(?P<teacher>.*?)</td>.*?'
                             '<td>(?P<classroom>.*?)</td>.*?'
                             '<td>(?P<building>.*?)</td>.*?'
                             '<td>(?P<campus>.*?)</td>.*?', re.DOTALL)

        for it in pattern.finditer(r.text):
            self._schedules.append(Schedule(**it.groupdict()))
        logging.info('获取成功')

    @property
    def teacher_num(self):
        self._turn()
        return self._teacher_num

    @property
    def capacity(self):
        self._turn()
        return self._capacity

    @property
    def selected_count(self):
        self._turn()
        return self._selected_count

    @property
    def selected(self):
        self._turn()
        return self._selected

    @property
    def teacher_info(self):
        r = get(TEACHER_INFO_URL, params={'TeacherNO': self.teacher_num})
        return r.ok

    @property
    def course_info(self):
        r = get(COURSE_INFO_URL, params={'CourseNO': self.course.course_num, 'TaskID': self.task_id})
        return r.ok

    @property
    def schedules(self):
        return '\n'.join(str(sche) for sche in self._schedules)

    @property
    def available(self):
        return self.selected_count < self.capacity

    # todo 多线程抢课,错误处理
    def select(self):
        """选择课程"""
        # 返回的是更新后的课表，填充在main frame中
        # todo
        logging.info('尝试选择任务 %s', str(self))
        r = get(SELECT_URL, params={'XKTaskID': self.task_id})

        match = re.search(r'iRetFlag=(\d+).*?CurTaskID', r.text, re.DOTALL)
        if match:
            code = match.group(1)
            if code == '1021':
                logging.info('选课成功 %s', str(self))
                WATCHING_LIST.remove(self)
                return True
            elif code == '1022':
                logging.error('已经选择此课程 %s', str(self))
                WATCHING_LIST.remove(self)
                return True
            elif code == '1023':
                logging.warning('课程冲突 %s', str(self))
                return False
            elif code == '1028':
                logging.error('课程人数达到上限 %s', str(self))
                return False
            else:
                logging.error('未知原因 %s', str(self))
                if not os.path.isfile('unknown.log'):
                    with open('unknown.log', 'w')as f:
                        f.write(r.text)
        return False

    def __str__(self):
        return '{}-{}-{}-{} {}/{}'.format(self.course,
                                          self.teacher_name,
                                          '已选' if self.selected else '未选',
                                          self.description,
                                          self.selected_count,
                                          self.capacity)

    def delete(self):
        """删除课程"""
        r = get(DELETE_URL, params={'XKTaskID': self.task_id})

        match = re.search(r'iRetFlag=null.*CurTaskID=\d+', r.text, re.DOTALL)
        return match
