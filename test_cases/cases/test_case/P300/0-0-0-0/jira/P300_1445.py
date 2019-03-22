# -*-coding:utf-8 -*
import os
import time
import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean

####################################################################################
#
# author liyi
# date 2018-07-24
# @summary：
#    对一个中文目录创建快照，查看是否可以正确获取快照信息
# @steps:
#    1、对目录创建快照a1(使用命令pscli --command=create_snapshot  expire_time为0)；
#    2、查询快照(使用pscli --command=get_snapshot)；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                # 本脚本名字
SYSTEM_IP = get_config.get_parastor_ip()
SNAP_PATH = snap_common.SNAP_PATH_ABSPATH                                  # /mnt/parastor/snap/
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)            # /mnt/volume1/snap/P300_1445
CREATE_SNAP_PATH = os.path.join(SNAP_TRUE_PATH, '中文测试路径')            # /mnt/parastor/snap/P300_1445/中文测试路径


def case():
    # 1> 对中文目录创建快照
    cmd_snap_path = 'mkdir %s' % SNAP_PATH
    common.run_command(SYSTEM_IP, cmd_snap_path)                    # 创建目录/mnt/parastor/snap/
    cmd_true_path = 'mkdir %s' % SNAP_TRUE_PATH
    common.run_command(SYSTEM_IP, cmd_true_path)                    # 创建目录/mnt/parastor/snap/P300_1445/
    cmd = 'mkdir %s' % CREATE_SNAP_PATH
    '''创建中文目录/mnt/parastor/snap/P300_1445/中文测试路径'''
    common.run_command(SYSTEM_IP, cmd)
    name_snap = FILE_NAME + '_snapshot1'
    path_snap = snap_common.VOLUME_NAME + ':/' + snap_common.SNAP_PATH_BASENAME+'/'+FILE_NAME+'/'+'中文测试路径'
    rc, stdout = snap_common.create_snapshot(name_snap, path_snap)         # 在中文目录下创建快照
    common.judge_rc(rc, 0, "create_snapshot %s failed!!" % name_snap)

    # 2> 查询快照信息
    log.info("\t[ get_snapshot ]")
    stdout = snap_common.get_snapshot_by_name(name_snap)
    common.judge_rc_unequal(stdout, -1, "get snapshot %s failed!!!" % name_snap)


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
