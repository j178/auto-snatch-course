# Auto-snatch-course

A simple sdk for auto snatching courses of NEU  

[![Build Status](https://travis-ci.org/j178/auto-snatch-course.svg?branch=master)](https://travis-ci.org/j178/auto-snatch-course)

## Requirements

* Python 3.5
* requests

## Usage
Set environment variables `XK_ID` and `XK_PW` then run the `main.py` script.  

Or change the line `u = User(os.getenv('XK_ID'), os.getenv('XK_PW'))` line of `main.py` with your id and password 
explicity.

## TODO
- [x] monitor courses 
- [ ] add **multiple thread** login simultaneously
- [ ] GUI 


## Statement
If you use this script to do things bad, it's nothing to do with me.

## License
WTFPL