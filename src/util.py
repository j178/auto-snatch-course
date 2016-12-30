# Author: John Jiang
# Date  : 2016/7/6
# auto retry
import functools
import threading
import time

import requests
import requests.adapters

ADAPTER_WITH_RETRY = requests.adapters.HTTPAdapter(
        max_retries=requests.adapters.Retry(total=10, status_forcelist=[400, 403, 404, 408, 500, 502]))

_session = requests.session()
_session.mount('http://', ADAPTER_WITH_RETRY)

WATCHING = []
CONTINUE_WATCHING = True


def watch():
    """监视要抢的课，一旦有退课立马选上"""

    def _():
        while CONTINUE_WATCHING:
            for task in WATCHING:
                task.select()
                time.sleep(1)
            time.sleep(1)

    t = threading.Thread(target=_)
    t.start()
    return t


def get(url, max_retries=float('inf'), timeout=0.1, **kwargs):
    tried = 0
    while True:
        try:
            r = _session.get(url, timeout=timeout, **kwargs)
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            tried += 1
            if tried >= max_retries:
                raise
            time.sleep(0.5)
        else:
            return r


def post(url, data=None, json=None, max_retries=float('inf'), timeout=0.1, **kwargs):
    tried = 0
    while True:
        try:
            r = _session.post(url, data, json, timeout=timeout, **kwargs)
            r.raise_for_status()
        except requests.RequestException as e:
            print(e)
            tried += 1
            if tried >= max_retries:
                raise
            time.sleep(0.5)
        else:
            return r


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


def func_once(func):
    "A decorator that runs a function only once."

    @functools.wraps(func)
    def decorated(*args, **kwargs):
        try:
            return decorated._once_result
        except AttributeError:
            decorated._once_result = func(*args, **kwargs)
            return decorated._once_result

    return decorated


def method_once(method):
    "A decorator that runs a method only once."
    attrname = "_%s_once_result" % id(method)

    @functools.wraps(method)
    def decorated(self, *args, **kwargs):
        try:
            return getattr(self, attrname)
        except AttributeError:
            setattr(self, attrname, method(self, *args, **kwargs))
            return getattr(self, attrname)

    return decorated