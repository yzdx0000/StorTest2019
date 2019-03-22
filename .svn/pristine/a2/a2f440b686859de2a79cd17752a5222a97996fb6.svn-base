"""Implement some simple interface for logging in ParaStor."""

import logging
import logging.handlers
import datetime
import os
import inspect
import time
import get_config

print2console = False
my_logger = None
log_file_dir = None


def init(log_file=None, _print2console=True):
    global my_logger
    global print2console
    print2console = _print2console
    # if my_logger is None:
    if log_file is not None:
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
        print msg
    my_logger.debug(msg)


def info(msg):
    if my_logger is None:
        return
    current_time = datetime.datetime.now()
    currenttime = current_time.strftime('%y-%m-%d %H:%M:%S')
    if print2console:
        log_msg = '[%s] %s' % (currenttime, msg)
        print log_msg

    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[INFO][%s]%s:%d:%s()' % \
                 (currenttime,
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.info(msg)


def error(msg, exc_info=None):
    if my_logger is None:
        return
    current_time = datetime.datetime.now()
    currenttime = current_time.strftime('%y-%m-%d %H:%M:%S')
    if print2console:
        log_msg = '[%s] %s' % (currenttime, msg)
        print log_msg

    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[ERROR][%s]%s:%d:%s()' % \
                 (currenttime,
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.error(msg, exc_info=exc_info)


def warn(msg):
    if my_logger is None:
        return
    current_time = datetime.datetime.now()
    currenttime = current_time.strftime('%y-%m-%d %H:%M:%S')
    if print2console:
        log_msg = '[%s] %s' % (currenttime, msg)
        print log_msg

    caller_frame = inspect.stack()[1]
    frame = caller_frame[0]
    info = inspect.getframeinfo(frame)
    prefix_str = '[WARN][%s]%s:%d:%s()' % \
                 (currenttime,
                  os.path.basename(info.filename),
                  info.lineno,
                  info.function)
    msg = '%-70s%s' % (prefix_str, msg)
    my_logger.warn(msg)


##############################################################################
# ##name  :      get_log_path
# ##parameter:   log_name:log name
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: get log path
##############################################################################
def get_log_path(log_name):
    global log_file_dir
    test_log_path = get_config.get_testlog_path()
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_dir = os.path.join(test_log_path, ("%s_%s" % (now_time, log_name)))
    try:
        os.mkdir(log_file_dir)
    except Exception,e:
        error("file exit %s" % e)
    log_file_path = os.path.join(log_file_dir, '%s.log' % log_name)
    return log_file_path