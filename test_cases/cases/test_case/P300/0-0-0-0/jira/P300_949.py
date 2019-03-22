# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# Date: 2018-01-19
# @summary：
#    更新授权，发生死锁。
# @steps:
#    1、获取集群中卷的id；
#    2、创建一个新的授权；
#    3、更新授权信息；
#    4、删除授权；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


def case():
    log.info("获取所有卷的id")
    obj_volume = common.Volume()
    volume_ids = obj_volume.get_all_volumes_id()
    common.judge_rc_unequal(len(volume_ids), 0, "do not have volume this case can't run")

    log.info("选取一个卷,创建授权")
    volume_id = volume_ids[0]
    obj_client_auth = common.Clientauth()
    rc, stdout = obj_client_auth.create_client_auth('1.1.1.1', volume_id)
    common.judge_rc(rc, 0, 'create client auth')

    stdout = common.json_loads(stdout)
    client_auth_id = stdout['result']['ids'][0]

    log.info("更新授权信息")
    rc = obj_client_auth.update_client_auth(client_auth_id, '1.1.1.2', volume_id)
    common.judge_rc(rc, 0, 'update client auth')

    log.info("删除授权信息")
    rc = obj_client_auth.delete_client_auth(client_auth_id)
    common.judge_rc(rc, 0, 'del client auth')


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)