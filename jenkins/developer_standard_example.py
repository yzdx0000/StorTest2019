# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import get_config

##########################################
#
# Author: duyuli
# date 2019-03-13
# @summary：
# 开发用例编写模板
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
PARASTOR_IP_LIST = get_config.get_allparastor_ips()
log_path = get_config.get_testlog_path()
SYSTEM_IP_0 = PARASTOR_IP_LIST[0]                                          # 集群ip
SYSTEM_IP_1 = PARASTOR_IP_LIST[1]
SYSTEM_IP_2 = PARASTOR_IP_LIST[2]
develop_dir_name = "develop_jenkins_test"
path = ""

def case():
    log.info("----------develop case begin----------")
    exe = ""
    if path.endswith(".sh"):
        exe = "sh"
    if path.endswith(".py"):
        exe = "python -u"
    cmd = "ssh %s \"%s %s\"" % (SYSTEM_IP_0, exe, path)
    rc = common.command(cmd)
    if 0 != rc:
        cmd = "scp -r %s:/home/%s %s" % (SYSTEM_IP_0, develop_dir_name, log_path)
        rc, stdout = common.command(cmd)
        common.judge_rc(rc, 0, "scp develop log error")
        log.info("exe error")
    return


def main():
    case()
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    file_name = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    common.case_main(main)