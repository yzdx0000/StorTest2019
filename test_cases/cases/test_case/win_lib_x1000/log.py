"""Implement some simple interface for logging in ParaStor."""

import logging
import logging.handlers
import datetime
import os
import inspect
import time

print2console = False
my_logger = None

class Log_file:
    def setName(self, name):
        self.name = name

    def getName(self):
        return self.name

current_log = Log_file()

def init(log_file=None, _print2console=True):
    global my_logger
    global print2console
    print2console = _print2console
    # if my_logger is None:
    if log_file is not None:
        current_log.setName(log_file)
        my_logger = logging.getLogger(os.path.basename(log_file))
        my_logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(log_file,
                                                       maxBytes=1024*1024*100,
                                                       backupCount=1)
        my_logger.addHandler(handler)
        return handler.stream

def debug(msg):
    if my_logger is None:
        return
    if print2console:
        print(msg)
    my_logger.debug(msg)

def info(msg):
    if my_logger is None:
        return
    if print2console:
        print(msg)
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[INFO][%s]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.info(msg)


def error(msg, exc_info=None):
    if my_logger is None:
        return
    if print2console:
        print(msg)
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[ERROR][%s]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.error(msg, exc_info=exc_info)

def warn(msg):
    if my_logger is None:
        return
    if print2console:
        print(msg)
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[WARN][%s]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.warn(msg)

def get_log_path():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_log_path = current_dir + '\\test_log'
    if not os.path.exists(test_log_path):
        os.mkdir(test_log_path)
    log_name = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_path = test_log_path + ("\\%s" %(log_name))
    return log_file_path

