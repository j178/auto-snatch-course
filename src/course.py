# Author: John Jiang
# Date  : 2016/7/6
import re

import logging

from .task import Task
from .urls import *
from .util import get, method_once


class Course:
    # 用户不变的一些信息
    major_level = None
    grade_year = None
    major_num = None
    if_need = None

    def __init__(self, **kwargs):
        self.name = kwargs.get('name')
        self.type = kwargs.get('type')
        self.course_num = kwargs.get('course_num')
        self.course_model_id = kwargs.get('course_model_id')
        self._tasks = []

    @classmethod
    def init_course_attrs(cls):
        """
        获取当前用户默认的一些属性，在后面获取Task时使用
        """
        # todo 分类查找课程, 分页显示

        if cls.major_level:
            return

        # 查询条件设置页，初始由服务器设置好了与账户匹配的信息，需要这里的信息和CourseID才能确定一个Task
        # 如果自定义了查询，后面请求Task的时候需要相应改变参数
        r = get(COURSE_COMMON_INFO_URL)
        match = re.search(r'<select name="MajorLevel".*? value="(?P<major_level>\d+)" selected.*?</select>.*?'
                          r'<input name="GradeYear" type="text" size="6" value="(?P<grade_year>.*?)">.*?'
                          r'<select name="MajorNO".* <option value="(?P<major_num>.*?)" selected>.*?'
                          r'<select name="IfNeed" .*?<option value="(?P<if_need>.*?)" selected>',
                          r.text, re.DOTALL)

        if match:
            data = match.groupdict()
            for key in data:
                setattr(cls, key, data[key])
        else:
            # retry
            pass

    @method_once
    def _get_tasks(self):
        """
        获取课程对应的老师列表

        :return: generate Task对象
        :rtype generator of Task
        """
        params = {
            'CourseNO'     : self.course_num,
            'CourseModelID': self.course_model_id,
            'MajorLevel'   : self.major_level,
            'GradeYear'    : self.grade_year,
            'MajorNO'      : self.major_num,
            'IfNeed'       : self.if_need
        }

        # todo 缓存
        logging.info('获取课程 %s(%s) 的所有任务中', self.name, self.course_num)
        r = get(TASK_INFO_URL, params=params)

        pattern = re.compile(r'<td nowrap.*?\'(?P<task_id>.*?)\'.*?'
                             r'<td align="center".*?>\s+(?P<teacher_name>.*?)\s+</td>.*?'
                             r'<span.*?>(?P<description>.*?)&nbsp', re.DOTALL)

        for match in pattern.finditer(r.text):
            self._tasks.append(Task(**match.groupdict(), course=self))
        logging.info('获取课程任务成功')

    @property
    def tasks(self):
        self._get_tasks()
        return self._tasks

    def __str__(self):
        return '[{}]-{}-{}'.format(self.course_num, self.name, self.type)
