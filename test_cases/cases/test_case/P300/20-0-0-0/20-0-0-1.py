# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import re

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common
import make_fault
import snap_common
import tool_use
import nas_common_new
import ad_less_code

"""
 Author: liangxy
 date 2019-03-20
 @summary：
    20-0-1-1 主参数为“DNS 地址：主”的AD认证合法测试
 @steps:
   

 @changelog：
 
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字


def case():
    nasobj = nas_common_new.NAS()
    log.info("1.添加AD认证服务器")
    adobj = nas_common_new.AuthProviderAD(services_for_unix='NONE')
    msgad = adobj.add_auth_provider_ad()
    common.judge_rc(msgad['err_no'], 0, msgad['detail_err_msg'])
    ad_less_code.ad_less_code(p_id=adobj.p_id)

    return


def nas_main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info("用例20-0-1-1 主参数为“DNS 地址：主”的AD认证合法测试 finished!")


if __name__ == '__main__':
    nas_main()