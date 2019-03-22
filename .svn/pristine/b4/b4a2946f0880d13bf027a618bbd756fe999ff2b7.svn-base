# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean
import nas_common

####################################################################################
#
# Author: chenjy
# date 2018-09-26
# @summary：
#    disabe_s3 、删除子网、删除访问分区
# @steps:
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    s3_access_zone_lst = []
    pscli_info = nas_common.get_access_zones()
    for access_zone in pscli_info['result']['access_zones']:
        if access_zone['s3_service_enabled'] is True:
            s3_access_zone_lst.append(access_zone['id'])

    for id in s3_access_zone_lst:
        rc, stdout = common.disable_s3(id)
        common.judge_rc(rc, 0, "disable_s3 failed")

    nas_common.delete_all_nas_config()

    return


def main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
