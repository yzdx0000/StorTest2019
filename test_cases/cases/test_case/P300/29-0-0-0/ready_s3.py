# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean
import nas_common
import get_config

####################################################################################
#
# Author: chenjy
# date 2018-09-26
# @summary：
#    创建访问分区，enable_s3
# @steps:
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    nas_common.delete_all_nas_config()
    ids = nas_common.get_node_ids()
    pscli_info = nas_common.create_access_zone(ids, 's3test')
    az_id = pscli_info['result']

    rc, stdout = s3_common.enable_s3(az_id)
    common.judge_rc(rc, 0, 'failed')
    return


def main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    # prepare_clean.s3_test_prepare(FILE_NAME)
    case()
    #prepare_clean.s3_test_clean()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
