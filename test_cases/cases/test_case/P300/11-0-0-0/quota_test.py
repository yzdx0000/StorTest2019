#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：反复创建删除10条配额
#######################################################

import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import shell
import get_config
import json
import datetime

def quota_main():

    print datetime.datetime.now()
    print time.time()
    time.sleep(5)
    print time.time()
    return

class Quota_Class_quota_test():
    def quota_method_quota_test(self):
        common.case_main(quota_main)

if __name__ == '__main__':
#    print "__file__ = %s" %__file__
#    print "__name__ = %s" %__name__
    common.case_main(quota_main)