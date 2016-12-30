# Author: John Jiang
# Date  : 2016/7/6
# print('test travis')
import os

from src import User
from src.util import watch, WATCHING, CONTINUE_WATCHING

watch_thread = watch()


def main():
    u = User(os.getenv('XK_ID'), os.getenv('XK_PW'))
    b, msg = u.login()

    if not b:
        print(msg)

    print(u.major, u.grade)

    for i, c in enumerate(u.courses):
        print('[{}] {} {} {}'.format(i, c.course_num, c.name, c.type, c.course_model_id))

    while True:
        choices = input('courses to select>>>')

        choices = choices.split(' ')

        for choice in choices:
            try:
                c = u.courses[int(choice)]
            except ValueError:
                print('invalid choice', choice)

            for i, task in enumerate(c.tasks):
                print('[{}] {} {} {} {} {} {}/{}'.format(i, task.course_num, task.teacher_name,
                                                         '已选' if task.selected else '未选',
                                                         task.task_id, task.description,
                                                         task.selected_count, task.capacity))

            if len(c.tasks) == 1:
                t = c.tasks[0]
            else:
                select_task = input('task to select>>>')
                t = c.tasks[int(select_task)]

            print(t.schedules)

            if input('ADD TO WATCHING(Y/n)?').strip() == 'Y':
                WATCHING.append(t)


if __name__ == '__main__':
    try:
        main()
        watch_thread.join()
    except KeyboardInterrupt:
        CONTINUE_WATCHING = False

# 抢课登陆, 多线程是否有效? 是否有必要使用多线程发请求?  # requests.session 是否线程安全?
# 如果不安全是哪些变量不安全? 将cookie保存构造新的session是否有效?
# 使用多线程是否要使用代理?
