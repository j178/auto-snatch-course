# Author: John Jiang
# Date  : 2016/7/6

import os
import sys

from src import User
from src.util import Watcher


def main():
    if len(sys.argv) >= 3:
        id = sys.argv[1]
        pw = sys.argv[2]
    else:
        id = os.getenv('XK_ID')
        pw = os.getenv('XK_PW')

    user = User(id, pw)
    print('{} 登录中...'.format(id))

    while True:
        b, msg = user.login()

        if not b:
            print(msg)
            continue
        else:
            break

    print(user.major, user.grade)

    for i, course in enumerate(user.courses):
        print('[{}] {} '.format(i, course))

    watcher = Watcher()
    while True:
        choice = input('要选择的课程的序号(q 退出)>>>').strip()

        if choice == 'q':
            break

        try:
            course = user.courses[int(choice)]
        except (ValueError, IndexError):
            print('此课程不存在: ', choice)
            continue

        if len(course.tasks) == 1:
            task = course.tasks[0]
        elif len(course.tasks) == 0:
            print('你选择的课程 [{}] 没有可选老师'.format(course.name))
            continue
        else:
            print('你选择的课程 [{}] 有以下老师可选:'.format(course.name))
            for i, task in enumerate(course.tasks):
                print('[{}] {} '.format(i, task))
            select_task = input('要选择的老师的序号>>>')
            task = course.tasks[int(select_task)]

        watcher.add_task(task)
        print('添加成功, 正在抢课中')


if __name__ == '__main__':
    main()

# 抢课登陆, 多线程是否有效? 是否有必要使用多线程发请求?  # requests.session 是否线程安全?
# 如果不安全是哪些变量不安全? 将cookie保存构造新的session是否有效?
# 使用多线程是否要使用代理?
