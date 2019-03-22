#-*-coding:utf-8 -*
#!/usr/bin/python

import os
import time

import utils_path
import common
import snap_common
import log
import prepare_clean

#=================================================================================
#  latest update:2018-04-23                                                      =
#  author:wangguanglin                                                           =
#=================================================================================
# 2018-04-23:
# 修改者：wangguanglin
#summary:
#    乱序删除快照后,校验数据正确
#@steps:
#    1、对目录/mnt/wangguanglin/snap创建10个快照，每个快照之间修改目录下的内容
#    2、乱序删除奇数快照，检验偶数快照数据的正确性
#
#changelog:
######################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)             #/mnt/wangguanglin/snap/snap_13_0_2_38
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)  #/snap/snap_13_0_2_38


##############################################################################
# ##name  :      get_snapshot_ids_by_name1
# ##parameter:   name:快照名字
# ##return:      -1:没有找到快照 snapshot_id_lst:名字包含name的所有快照id
# ##author:      wangguanglin
# ##date  :      2018.04.24
# ##Description: 通过名字只获取一个快照id
##############################################################################
def get_snapshot_ids_by_name1(name, ext_node_ip=None):
    snapshot_id_lst = []
    cmd = 'get_snapshot'
    rc, stdout = common.get_snapshot('name', name)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
        raise Exception("Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    else:
        stdout =common.json_loads(stdout)
        if stdout['result']['total'] == 0:
            return -1, []
        else:
            snapshots = stdout['result']['snapshots']
            for snapshot in snapshots:
                if snapshot['name'] == name:
                    snapshot_id_lst.append(snapshot['id'])
            return 0, snapshot_id_lst


##############################################################################
# ##name  :      delete_snapshot_by_name1
# ##parameter:   name:快照名字
# ##return:
# ##author:      wangguanglin
# ##date  :      2018.04.24
# ##Description: 根据名字只删除一个快照
##############################################################################
def delete_snapshot_by_name1(name, ext_node_ip=None):
    if None == ext_node_ip:
        rc, snapshot_id_lst = get_snapshot_ids_by_name1(name)
        if -1 == rc:
            return 0, None
        snapshot_id_str = ','.join(str(i) for i in snapshot_id_lst)
        rc, stdout = snap_common.delete_snapshot_by_ids(snapshot_id_str)
        return rc, stdout
    else:
        rc, snapshot_id_lst = get_snapshot_ids_by_name1(name, ext_node_ip)
        if -1 == rc:
            return 0, None
        snapshot_id_str = ','.join(str(i) for i in snapshot_id_lst)
        rc, stdout = snap_common.delete_snapshot_by_ids(snapshot_id_str, ext_node_ip)
        return rc, stdout


def case():
    """创建子目录/mnt/wangguanglin/snap/snap_13_0_2_38/test_dir"""
    test_dir=os.path.join(SNAP_TRUE_PATH,'test_dir')
    cmd='mkdir %s'% test_dir
    common.run_command(snap_common.CLIENT_IP_1, cmd)

    """                                                                                                                                                                                                               
    创建文件/mnt/wangguanglin/snap/snap_13_0_2_38/test_dir/test_file1
    对目录 /mnt/wangguanglin/snap创建个快照，每个快照之间修改目录下的内容
    """
    test_file1 = os.path.join(test_dir, 'test_file1')
    for num in range(1,11):
        cmd = "echo '%d'>> %s"% (num, test_file1)
        common.run_command(snap_common.CLIENT_IP_1, cmd)
        """创建快照"""
        snap_name1 = FILE_NAME + '_snapshot%d'% num
        path1 = snap_common.VOLUME_NAME + ':/' + os.path.join(CREATE_SNAP_PATH, 'test_dir')
        rc, stdout = snap_common.create_snapshot(snap_name1, path1)
        if 0 != rc:
           log.error('create_snapshot %s failed!!!' % snap_name1)
           raise Exception('create_snapshot %s failed!!!' % snap_name1)

    """乱序删除奇数快照，检验偶数快照数据的正确性"""
    list=[3,1,7,5,9]
    for num1 in list:
        snap_name2 = FILE_NAME + '_snapshot%d' % num1
        """删除指定的快照"""
        rc, stdout = delete_snapshot_by_name1(snap_name2)
        if 0 != rc:
            log.error('%s delete failed!!!' % (snap_name2))
            raise Exception('%s delete failed!!!' % (snap_name2))

    """检查第二个快照的正确性"""
    snap_name3 = FILE_NAME + '_snapshot2'
    snap_path2 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name3)
    cmd = 'cat %s' % os.path.join(snap_path2, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2' != stdout.strip():
        log.error('%s is not right!!!' % snap_name3)
        raise Exception('%s is not right!!!' % snap_name3)

    """检查第四个快照的正确性"""
    snap_name4 = FILE_NAME + '_snapshot4'
    snap_path3 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name4)
    cmd = 'cat %s' % os.path.join(snap_path3, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2\n3\n4' != stdout.strip():
        log.error('%s is not right!!!' % snap_name4)
        raise Exception('%s is not right!!!' % snap_name4)

    """检查第六个快照的正确性"""
    snap_name5 = FILE_NAME + '_snapshot6'
    snap_path4 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name5)
    cmd = 'cat %s' % os.path.join(snap_path4, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2\n3\n4\n5\n6' != stdout.strip():
        log.error('%s is not right!!!' % snap_name5)
        raise Exception('%s is not right!!!' % snap_name5)

    """检查第八个快照的正确性"""
    snap_name6 = FILE_NAME + '_snapshot8'
    snap_path5 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name6)
    cmd = 'cat %s' % os.path.join(snap_path5, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2\n3\n4\n5\n6\n7\n8' != stdout.strip():
        log.error('%s is not right!!!' % snap_name6)
        raise Exception('%s is not right!!!' % snap_name6)

    """检查第十个快照内容的正确性"""
    snap_name7 = FILE_NAME + '_snapshot10'
    snap_path6 = os.path.join(snap_common.SNAPSHOT_PAHT, snap_name7)
    cmd = 'cat %s' % os.path.join(snap_path6, 'test_file1')
    rc, stdout = common.run_command(snap_common.CLIENT_IP_1, cmd)
    if '1\n2\n3\n4\n5\n6\n7\n8\n9\n10' != stdout.strip():
        log.error('%s is not right!!!' % snap_name7)
        raise Exception('%s is not right!!!' % snap_name7)
    time.sleep(10)

    """ 删除快照"""
    rc, stdout = snap_common.delete_snapshot_by_name(FILE_NAME)
    if 0 != rc:
        log.error('%s delete failed!!!' % (FILE_NAME))
        raise Exception('%s delete failed!!!' % (FILE_NAME))

    return 

def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)

if __name__ == '__main__':
    common.case_main(main)
