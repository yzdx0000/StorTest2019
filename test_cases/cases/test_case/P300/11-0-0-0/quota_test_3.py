# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：拷贝passwd和group文件到指定节点
#   yes是拷贝带指定用户的，no是拷贝不带指定用户的
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

def quota_main():

    quota_common.scp_saved_passwd_and_group_to_all_other_nodes(quota_common.NOTE_IP_1, "no")

    return

class Quota_Class_quota_test_3():
    def quota_method_quota_test_3(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    #    print "__file__ = %s" %__file__
    #    print "__name__ = %s" %__name__
    common.case_main(quota_main)
    #quota_common.delete_all_quota_config()