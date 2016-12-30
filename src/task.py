# Author: John Jiang
# Date  : 2016/7/6
import re

from .urls import *
from .schedule import Schedule
from .util import get, method_once


class Task:
    def __init__(self, **kwargs):
        self.course_num = kwargs.get('course_num')
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
        r = get(COURSE_INFO_URL, params={'CourseNO': self.course_num, 'TaskID': self.task_id})
        return r.ok

    @property
    def schedules(self):
        return '\n'.join(str(sche) for sche in self._schedules)

    @property
    def available(self):
        return self.selected_count < self.capacity

    # todo 多线程抢课,错误处理
    def select(self):
        """
        选择课程
        """
        # 返回的是更新后的课表，填充在main frame中
        # todo
        r = get(SELECT_URL, params={'XKTaskID': self.task_id})

        match = re.search(r'iRetFlag=(\d+).*?CurTaskID', r.text, re.DOTALL)
        if match:
            if match.group(1) == '1021':
                print('选课成功')
            elif match.group(1) == '1023':
                print('课程冲突')
            elif match.group(1) == '1028':
                print('课程人数达到上限', self.task_id)
        return r.text

    def delete(self):
        """
        删除课程
        """
        r = get(DELETE_URL, params={'XKTaskID': self.task_id})
        return r.ok
