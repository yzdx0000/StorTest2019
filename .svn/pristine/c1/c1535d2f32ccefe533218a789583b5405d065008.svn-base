# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random

import utils_path
import common
import log
import shell
import get_config
import prepare_clean
import tool_use
import commands
import snap_common
import nas_common

#################################################################
#
# Author: chenjy1
# Date: 2018-08-08
# @summary：
#        快照回滚后目录无法访问
# @steps:
#       1、/mnt/a/snap_parent/snap_child/dir/  touch file
#       2、对snao_parent做快照a1,
#       3、进入目录 dir 创建10个文件 且echo 222>file
#       4、对snap_parent做快照a2，
#       5、进入目录snap_parent，执行chmod 777 snap_child chown u1 snap_child chgrp g1 snap_child
#       6、对snap_parent做快照a3
#       7、进入目录snap_parent，执行mv snap_child  snap_child_rename
#       8、snap_child_rename做快照a4
#       9、进入目录snap_parent,执行 rm -rf snap_child_rename
#       10、对snap_parent做快照a5
#       11、快照回滚，发现dir目录不存在了
#  @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                       # 本脚本名字
# /mnt/parastor/defect_case/P300_115/snap_parent
SNAP_PARENT = os.path.join(prepare_clean.DEFECT_PATH, FILE_NAME, "snap_parent")
# /mnt/parastor/defect_case/P300_115/snap_parent/snap_child
SNAP_CHILD = os.path.join(SNAP_PARENT, "snap_child")
# /mnt/parastor/defect_case/P300_115/snap_parent/snap_child/snap_dir
SNAP_DIR = os.path.join(SNAP_CHILD, "snap_dir")


def case():
    log.info("case begin")
    file_name = 'file'
    snap_common.delete_snapshot_by_name(FILE_NAME)
    snap_common.wait_snap_del_by_name(FILE_NAME)

    log.info("1> 创建目录")
    cmd = "mkdir -p %s " % SNAP_DIR

    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    """创建文件file"""
    cmd = "cd %s ; touch %s" % (SNAP_DIR, file_name)
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    create_snap_path = snap_common.VOLUME_NAME + ':/' + os.path.join(os.path.basename(prepare_clean.DEFECT_PATH),
                                                                     FILE_NAME, "snap_parent")
    log.info("2> 对snap_parent做快照1")
    snap_name1 = FILE_NAME + '_snapshot1'
    rc, stdout = snap_common.create_snapshot(snap_name1, create_snap_path)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("3> 进入目录 dir 创建10个文件 且echo 222>file")
    cmd = ("cd %s && for i in {1..10}; do dd if=/dev/zero of=ddfile$i bs=1M count=1024; done") % SNAP_DIR
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    cmd = ("cd %s && echo 222 > %s") % (SNAP_DIR, file_name)
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    log.info("4> 对snap_parent做快照2")
    snap_name2 = FILE_NAME + '_snapshot2'
    rc, stdout = snap_common.create_snapshot(snap_name2, create_snap_path)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("5> 进入目录snap_parent，执行chmod 777 snap_child chown u1 snap_child chgrp g1 snap_child")
    """先创建访问区"""
    ob_node = common.Node()
    node_ids = ob_node.get_node_id_by_ip(common.SYSTEM_IP)  # 创建的访问区的ip
    pscli_info = nas_common.create_access_zone(node_ids, FILE_NAME)
    if pscli_info['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % pscli_info['detail_err_msg'])
    access_zone_id = pscli_info['result']
    pscli_info = nas_common.get_access_zones(ids=access_zone_id)
    auth_provider_id = pscli_info['result']['access_zones'][0]['auth_provider_id']

    """enable_nas"""
    pscli_info = nas_common.enable_nas(access_zone_id)  # 访问区的Id
    if pscli_info['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % pscli_info['detail_err_msg'])

    """创建用户组和用户"""
    username = FILE_NAME + 'u'
    groupname = FILE_NAME + 'g'
    pscli_info = nas_common.create_auth_group(auth_provider_id, groupname)
    if pscli_info['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % pscli_info['detail_err_msg'])
    primary_group_id = pscli_info['result']

    pscli_info = nas_common.create_auth_user(auth_provider_id, username, '111111', primary_group_id)
    if pscli_info['err_no'] != 0:
        common.except_exit(info="detail_err_msg:%s" % pscli_info['detail_err_msg'])
    user_id = pscli_info['result']

    log.info("check user within 40s")
    for i in range(40):
        time.sleep(1)
        cmd = "su %s -c 'pwd'" % username
        rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
        log.info("wait %s s" % i)
        if rc == 0:
            break
    cmd = "su %s -c 'pwd'" % username
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "su %s failed. But liyanga said 40 seconds is enough. " % username)

    cmd = ("cd %s; chmod 777 %s ;chown %s %s ;chgrp %s %s") % (SNAP_PARENT, 'snap_child',
                                                               username, 'snap_child', groupname, 'snap_child')
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    log.info("6> 对snap_parent做快照3")
    snap_name3 = FILE_NAME + '_snapshot3'
    rc, stdout = snap_common.create_snapshot(snap_name3, create_snap_path)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("7> 进入目录snap_parent，执行mv snap_child  snap_child_rename")
    cmd = ("cd %s; mv %s %s") % (SNAP_PARENT, 'snap_child', 'snap_child_rename')
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    log.info("8> snap_child_rename做快照4")
    snap_name4 = FILE_NAME + '_snapshot4'
    rc, stdout = snap_common.create_snapshot(snap_name4, create_snap_path)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("9> 进入目录snap_parent,执行 rm -rf snap_child_rename")
    common.rm_exe(common.SYSTEM_IP, os.path.join(SNAP_PARENT, 'snap_child_rename'))
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    log.info("10> 对snap_parent做快照5")
    snap_name5 = FILE_NAME + '_snapshot5'
    rc, stdout = snap_common.create_snapshot(snap_name5, create_snap_path)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))

    log.info("11>快照回滚，发现dir目录不存在了")
    snap_info = snap_common.get_snapshot_by_name(snap_name4)
    snap_id = snap_info['id']
    rc, stdout = snap_common.revert_snapshot_by_id(snap_id)
    common.judge_rc(rc, 0, "revert snapshot %s failed!!!" % snap_name5)
    snap_common.check_revert_finished(snap_id)

    """检查dir目录"""
    cmd = ("cd %s && ls %s") % (os.path.join(SNAP_PARENT, 'snap_child_rename'), 'snap_dir')
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, "IP: %s execute command: \"%s\" failed. \nstdout: %s" % (common.SYSTEM_IP, cmd, stdout))

    """清除快照 """
    for i in range(1, 6):
        snap_name = FILE_NAME + '_snapshot%s' % i
        snap_info = snap_common.get_snapshot_by_name(snap_name)
        snap_id = snap_info['id']
        rc, stdout = snap_common.delete_snapshot_by_ids(snap_id)
        common.judge_rc(rc, 0, 'delete_snapshot %s failed!!!' % snap_name)
        snap_common.wait_snap_del_by_name(snap_name)

    """清除用户和用户组"""
    pscli_info = nas_common.delete_auth_users(user_id)
    if pscli_info['err_no'] != 0:
        common.except_exit(info='delete_auth_users failed')
    pscli_info = nas_common.delete_auth_groups(primary_group_id)
    if pscli_info['err_no'] != 0:
        common.except_exit(info='delete_auth_groups failed')
    """disable_nas"""
    pscli_info = nas_common.disable_nas(access_zone_id)
    if pscli_info['err_no'] != 0:
        common.except_exit(info='disable_nas failed')

    """清除访问区"""
    pscli_info = nas_common.delete_access_zone(access_zone_id)
    if pscli_info['err_no'] != 0:
        common.except_exit(info='delete_access_zone failed')

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    prepare_clean.nas_test_clean()
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    prepare_clean.nas_test_clean()
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
