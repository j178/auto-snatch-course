# Author: John Jiang
# Date  : 2016/7/6
# auto retry
import functools
import logging
import threading
import time

import requests
import requests.adapters

ADAPTER_WITH_RETRY = requests.adapters.HTTPAdapter(
    max_retries=requests.adapters.Retry(total=10, status_forcelist=[400, 403, 404, 408, 500, 502]))

_session = requests.session()
_session.mount('http://', ADAPTER_WITH_RETRY)

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] %(message)s',
                    datefmt='%H:%M:%S')
logging.root.disabled = True


def enable_logging():
    logging.root.disabled = False


class Watcher(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        self.daemon = False
        self._stop_event = threading.Event()
        self._task_list = []
        self._task_list_lock = threading.RLock()
        self.start()

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def run(self):
        while not self.stopped():
            with self._task_list_lock:
                tasks = self._task_list[:]

            for task in tasks:
                try:
                    if task.select():
                        self.remove_task(task)
                except Exception:
                    pass
                time.sleep(0.1)

            time.sleep(0.5)

    def add_task(self, task):
        with self._task_list_lock:
            self._task_list.append(task)

        if not self.is_alive():
            self.start()

    def remove_task(self, task):
        with self._task_list_lock:
            self._task_list.remove(task)


def get(url, max_retries=float('inf'), timeout=0.1, **kwargs):
    tried = 0
    while True:
        try:
            r = _session.get(url, timeout=timeout, **kwargs)
            r.raise_for_status()
        except requests.RequestException as e:
            logging.error(e)
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
            logging.error(e)
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
