# Author: John Jiang
# Date  : 2016/7/6
# print('test travis')
import os

from src import User
from src.util import watch, WATCHING

watch_thread = watch()


def main():
    u = User(os.getenv('XK_ID'), os.getenv('XK_PW'))
    b, msg = u.login()

    if not b:
        print(msg)

    print(u.major, u.grade)

    for i, c in enumerate(u.courses):
        print('[{}] {} {} {}'.format(i, c.course_num, c.name, c.type, c.course_model_id))

    choices = input('要选择的课程的序号(以空格分隔)>>>')

    choices = choices.split(' ')

    for choice in choices:
        try:
            c = u.courses[int(choice)]
        except ValueError:
            print('invalid choice', choice)

        for i, task in enumerate(c.tasks):
            print('[{}] {} '.format(i, task))

        if len(c.tasks) == 1:
            t = c.tasks[0]
        else:
            select_task = input('要选择的任务的序号>>>')
            t = c.tasks[int(select_task)]

        print(t.schedules)

        if input('是否监视此课(有退课时自动选择)(Y/n)?').strip() == 'Y':
            WATCHING.append(t)

    watch_thread.start()
    watch_thread.join()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        watch.watching = False


# 抢课登陆, 多线程是否有效? 是否有必要使用多线程发请求?  # requests.session 是否线程安全?
# 如果不安全是哪些变量不安全? 将cookie保存构造新的session是否有效?
# 使用多线程是否要使用代理?
