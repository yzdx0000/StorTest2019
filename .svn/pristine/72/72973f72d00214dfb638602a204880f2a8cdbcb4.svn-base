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

def init(log_file=None, _print2console=False):
    global my_logger
    global print2console
    print2console = _print2console
    #if my_logger is None:
    if log_file is not None:
        current_log.setName(log_file)
        my_logger = logging.getLogger(os.path.basename(log_file))
        my_logger.setLevel(logging.DEBUG)
        handler= logging.handlers.RotatingFileHandler(log_file,
                                                      maxBytes=1024*1024*100,
                                                      backupCount=1)
        my_logger.addHandler(handler)
        return handler.stream

def debug(msg):
    global my_logger
    if my_logger is None:
        return
    global print2console
    if print2console:
        print msg
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    filename, line_number, func_name = my_logger.findCaller()
    my_logger.debug(msg)


def info(msg):
    global my_logger
    if my_logger is None:
        return
    global print2console
    if print2console:
        print msg
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    filename, line_number, func_name = my_logger.findCaller()
    prefix_str = '[INFO][%s][%d]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                    os.getpid(),
                    os.path.basename(info.filename),
                    info.lineno,
                    info.function)
    msg = '%-80s%s' % (prefix_str, msg)
    my_logger.info(msg)


def error(msg):
    global my_logger
    if my_logger is None:
        return
    global print2console
    if print2console:
        print msg
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    filename, line_number, func_name = my_logger.findCaller()
    prefix_str = '[ERROR][%s][%d]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                  os.getpid(),
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-80s%s' % (prefix_str, msg)
    my_logger.error(msg)


def warn(msg):
    global my_logger
    if my_logger is None:
        return
    global print2console
    if print2console:
        print msg
    current_time = datetime.datetime.now()
    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    filename, line_number, func_name = my_logger.findCaller()
    prefix_str = '[WARN][%s][%d]%s:%d:%s()' % \
                 (current_time.strftime('%y-%m-%d %H:%M:%S'),
                  os.getpid(),
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-80s%s' % (prefix_str, msg)
    my_logger.warn(msg)

##############################################################################
###name  :      get_log_path
###parameter:   log_name:log name
###author:      baoruobing
###date  :      2017.07.12
###Description: get log path
##############################################################################
def get_log_path(log_name):
    test_log_path = get_config.get_testlog_path()
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_path = test_log_path + ("/%s_%s.log" %(now_time, log_name))
    return log_file_path

##############################################################################
###name  :      get_log_name
###parameter:
###author:      baoruobing
###date  :      2017.07.12
###Description: get log name
##############################################################################
#def get_log_name():
#    return current_log.getName()
