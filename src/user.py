# Author: John Jiang
# Date  : 2016/7/5
import logging
import re

from .urls import *
from .course import Course
from .util import get, post, method_once


class User:
    def __init__(self, student_num, password):
        # 所谓继承，其实非常简单，就是你有了父类的一些方法
        # 比如说这里，子类覆盖了父类的__init__方法，所以需要用super().__init__这样来调用，这样调用的话就会把self传给这个函数，
        # 让这个函数去给self设置上一些属性，于是也就是**有了父类的属性**，这就是属性的继承。
        # 父类中以__两个下划线开始的属性由于会命名重整，所以就算被设置了，在子类里面也是和父类不一样的名字。
        # 那类变量是怎么初始化的呢？
        # super()这个函数还是很复杂，他向__init__传的self到底是谁的呢？
        # super().__init__()
        self.num = student_num
        self.password = password
        self.name = None
        self.major = None
        self.grade = None
        self.class_ = None
        # 如果直接用self.courses，则会调用property的set方法，为了区分property和属性，就必须把这个设为私有的
        self._courses = []

    # todo 多线程同时抢滩登陆
    @method_once
    def login(self):
        """登录选课网站"""
        data = {
            'strStudentNO': self.num,
            'strPassword' : self.password
        }

        logging.info('登录中: %s', self.num)
        r = post(LOGIN_URL, data)

        pattern = re.compile(r'id="StudentName" value="(?P<name>.*?)".*?'
                             r'id="StudentNO" readonly value="(?P<num>.*?)".*?'
                             r'id="MajorName" readonly value="(?P<major>.*?)".*?'
                             r'id="GradeName" readonly value="(?P<grade>.*?)".*?'
                             r'id="ClassName" readonly value="(?P<class_>.*?)".*?', re.DOTALL)

        match = pattern.search(r.text)
        if match:
            d = match.groupdict()
            for key in d:
                setattr(self, key, d[key])

            logging.info('登录成功: %s', str(self))
            return True, ''
        else:
            match = re.search(r'<font color="#FF0000" size="2"><strong>(.*?)</strong></font>',
                              r.text)
            msg = match.group(1) if match  else 'Unknown Error'
            logging.error('登录失败 %s', msg)
            return False, msg

    def logout(self):
        get(EXIT_URL)
        logging.info('退出成功')

    def change_pwd(self, old, new):
        param = {
            'OldPassword'    : old,
            'NewPassword'    : new,
            'ConfirmPassword': new
        }
        # todo
        post(CHANGE_PWD_URL, param)

    @method_once
    def _get_courses(self, if_need='-1', course_kind4='-1', course_name='', course_mode_id=None):
        """
        根据查询条件获取可选课程

        :param str if_need: 课程的性质
            -1 全部性质
            1 公共基础课
            2 专业基础课
            3 全校性任选课
            4 专业任选课
            5 专业限选课
            6 人文选修课
            7 公共基础课(体育)
            8 暑期国际课
        :param course_kind4: 类别
            -1 全部类别
            1 必修课学分
            2 限选课学分
            3 外语毕业学分
            4 全校人文素质选修课
            5 暂不参与审核
            6 空任务
        :param str course_name: 课程名称
        :param course_mode_id: 默认不发送此参数
            1 必修
            2 限选
            3 任选
        :return: 返回Course对象的 Generator
        """

        Course.init_course_attrs()

        if if_need != '-1':
            Course.if_need = if_need

        data = {
            'GradeYear'  : Course.grade_year,
            'MajorNO'    : Course.major_num,
            'IfNeed'     : if_need,
            'CourseKind1': '-1',
            'CourseKind2': '-1',
            'CourseKind3': '-1',
            'CourseKind4': course_kind4,
            'CourseName' : course_name,
            'WeekdayID'  : '',
            'Section'    : ''
        }
        # 默认获取所有可选课程
        logging.info('获取课程列表中')
        r = post(QUERY_COURSE_URL, data=data)
        pattern = re.compile(r'<tr id="ID\d+".*?QueryTaskInfo\(\'(?P<course_num>.+?)\',\'\d+\','
                             r'\'(?P<course_model_id>\d+)\'.*?'
                             r'title="(?P<name>.+?)".*?'
                             r'nowrap.*?>(?P<type>.+?)</td>', re.DOTALL)

        for p in pattern.finditer(r.text):
            c = Course(**p.groupdict())
            self._courses.append(c)
        logging.info('课程列表获取成功')

    @property
    def courses(self, if_need='-1', course_kind4='-1', course_name='', course_mode_id=None):
        # 第一次体会到了封装的真正含义，内部接口负责获取数据，外部接口决定如何向外部提供数据
        self._get_courses(if_need, course_kind4, course_name, course_mode_id)
        return self._courses

    @property
    def result(self):
        return get(RESULT_URL).text

    @property
    def statistic(self):
        return get(STAT_URL).text

    def secure_password(self):
        """每5分钟改一次密码"""

    def __str__(self):
        return '{} {} {} {} {}'.format(self.name, self.num, self.major, self.grade, self.class_)
