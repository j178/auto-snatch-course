# Auto-snatch-course

A simple sdk for auto snatching courses of NEU  

[![Build Status](https://travis-ci.org/j178/auto-snatch-course.svg?branch=master)](https://travis-ci.org/j178/auto-snatch-course)

## Requirements

* Python 3.5
* requests

## Usage
````python
from src import User

u = User(username,password)
u.login()
for course in u.courses:
    for task in course.tasks:
        print(task)
````
## TODO
- [ ] 监视退课 
- [ ] add **multiple thread** login simultaneously
- [ ] utilize more flexible design pattern
- [ ] more simple and beautiful code
- [ ] GUI 


## Statement
If you use this script to do things bad, it's nothing to do with me.

## License
WTFPL