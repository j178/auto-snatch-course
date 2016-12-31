# Author: John Jiang
# Date  : 2016/7/7


class Schedule:
    def __init__(self, **kwargs):
        self.weekday = kwargs.get('weekday')
        self.section = kwargs.get('section')
        self.span_of_weeks = kwargs.get('span_of_weeks')
        self.week_type = kwargs.get('week_type')
        self.teacher = kwargs.get('teacher')
        self.classroom = kwargs.get('classroom')
        self.building = kwargs.get('building')
        self.campus = kwargs.get('campus')

    def __str__(self):
        return (self.weekday + '|' + self.section + '|' + self.span_of_weeks + '|' + self.week_type + '|' +
                self.teacher + '|' + self.classroom + '|' + self.building + '|' + self.campus)
