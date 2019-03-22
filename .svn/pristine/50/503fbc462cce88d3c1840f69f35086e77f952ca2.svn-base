# -*-coding:utf-8 -*
import os
import random

import utils_path
import common
import snap_common
import log
import prepare_clean
import get_config
import tool_use

####################################################################################
#
# Author: liyao
# date 2018-06-22
# @summary：
#    快照修改、删除与校验
# @steps:
#    1、部署3个客户端；
#    2、客户端1在目录/mnt/volume1/snap/snap_repetitive_test/data_dir/下执行vdbench 00脚本（创建文件）；
#    3、对目录/mnt/volume1/snap/snap_repetitive_test/data_dir/创建快照a1；
#    4、客户端1对目录/mnt/volume1/snap/snap_repetitive_test/data_dir/执行vdbench 01脚本修改数据；
#    5、对目录/mnt/volume1/snap/snap_repetitive_test/data_dir/创建快照a2；
#    6、执行vdbench 02脚本对目录/mnt/volume1/.snapshot/下的某个快照（随机选择）进行校验；
#    7、再次对目录/mnt/volume1/snap/snap_repetitive_test/data_dir/执行vdbench 01脚本修改数据；
#    8、对目录/mnt/volume1/snap/snap_repetitive_test/data_dir/创建快照a3；
#    9、执行vdbench 02脚本对目录/mnt/volume1/.snapshot/下的a2快照进行校验；
#    10、反复执行修改数据、创建快照、校验数据的过程；
#    11、当快照数量n大于10，修改数据、创建快照（n+1），之后随机删除一个快照并随机选择一个现存快照进行校验；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)              # /mnt/volume1/snap/snap_repetitive_test
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)   # /snap/snap_repetitive_test
SNAP_PATH = get_config.get_one_snap_test_path()
BASE_SNAP_PATH = os.path.dirname(SNAP_PATH)                                  # BASE_QUOTA_PATH = "/mnt/volume1"
SNAPSHOT_PAHT = os.path.join(BASE_SNAP_PATH, '.snapshot')                    # SNAPSHOT_PAHT = "/mnt/volume1/.snapshot"
DATA_DIR = os.path.join(SNAP_TRUE_PATH, 'data_dir')                 # /mnt/volume1/snap/snap_repetitive_test/data_dir/

obj_vdbench = tool_use.Vdbenchrun(size='(1m,30,4m,35,16g,30,64g,5)')


def loop_data_snap(snap_name, snap_delete_flag=False):
    # 在相同目录下修改数据
    jnl_name = 'jnl_' + snap_name.split('_')[-1]
    jnl_path = os.path.join(SNAP_TRUE_PATH, jnl_name)

    obj_vdbench.run_write_jn(DATA_DIR, jnl_path, common.SYSTEM_IP)

    # 对数据存放目录创建快照
    snap_path = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'data_dir')
    rc, stdout = snap_common.create_snapshot(snap_name, snap_path)
    common.judge_rc(rc, 0, 'create_snapshot %s failed!!!' % snap_name)

    snap_name_set = []
    # 判断快照数目是否达到删除阈值
    if snap_delete_flag:
        stdout = snap_common.get_all_snapshot()
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            exist_snap_name = snapshot['name']
            snap_name_set.append(exist_snap_name)

            # 随机选择一个快照并删除
        snap_delete_name = random.choice(snap_name_set)
        snap_common.delete_snapshot_by_name(snap_delete_name)
        snap_common.wait_snap_del_by_name(snap_delete_name)

    # 若快照数目未达到删除阈值，则直接随机选择快照并校验

    snap_name_set = []
    stdout = snap_common.get_all_snapshot()
    snapshots = stdout['result']['snapshots']
    for snapshot in snapshots:
        exist_snap_name = snapshot['name']
        snap_name_set.append(exist_snap_name)

        # 随机选择一个快照并进行校验
    check_snap_name = random.choice(snap_name_set)
    check_jnl_name = 'jnl_' + check_snap_name.split('_')[-1]
    check_jnl_path = os.path.join(SNAP_TRUE_PATH, check_jnl_name)
    check_snap_path = os.path.join(SNAPSHOT_PAHT, check_snap_name)

    # 在隐藏目录下校验快照内容
    obj_vdbench.run_check(check_snap_path, check_jnl_path, snap_common.CLIENT_IP_1)
    return


def case():
    # 在固定目录下创建数据
    common.rm_exe(snap_common.CLIENT_IP_1, os.path.join(SNAP_TRUE_PATH, '*'))
    cmd = 'mkdir %s' % DATA_DIR
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    # 执行00脚本创建数据，并循环修改数据、创建快照、（删除快照）、数据校验的过程
    snap_count = 10
    for i in range(snap_count):
        snap_name = FILE_NAME + '_' + str(i)
        jnl_init_name = 'jnl_' + snap_name.split('_')[-1]
        jnl_init_path = os.path.join(SNAP_TRUE_PATH, jnl_init_name)
        cmd = 'mkdir %s' % jnl_init_path
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        if i == 0:
            obj_vdbench.run_create(DATA_DIR, jnl_init_path, snap_common.SYSTEM_IP)
        elif i <= snap_count/2:
            loop_data_snap(snap_name)
        else:
            loop_data_snap(snap_name, snap_delete_flag=True)

    # 删除已创建的数据
    common.rm_exe(snap_common.CLIENT_IP_1, DATA_DIR)
    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME, fault=True)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)