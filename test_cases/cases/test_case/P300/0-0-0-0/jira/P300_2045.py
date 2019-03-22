# -*-coding:utf-8 -*
import os

import utils_path
import common
import snap_common
import log
import prepare_clean
import random
import json
"""
author@liangxy
date: 2018-08-04
@summary：
     缺陷自动化：命令get_snapshot中的--path参数无效
@steps:
    1、测试路径下创建子目录path1和path2，
    2、分别创建快照，返回名称
    3、使用--path参数，值为path2，若返回结果中不存在path1下的快照且存在path2下的快照，
    用例成功；否则，失败
    4、清理环境，删除创建的各文件
@changelog：
    
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
SNAP_TRUE_PATH = os.path.join(snap_common.SNAP_PATH, FILE_NAME)
CREATE_SNAP_PATH = os.path.join(snap_common.SNAP_PATH_BASENAME, FILE_NAME)
PATH_NUM = 3


def get_snapshot_ids_base():
    """
    author:LiangXiaoyu
    date:2018-08-04
    description:获得集群内的快照，无任何附加参数
    :return:
    changelog:
    """
    snapshot_id_lst = []
    stdout = snap_common.get_all_snapshot()
    if stdout['result']['total'] == 0:
        return -1, []
    else:
        snapshots = stdout['result']['snapshots']
        for snapshot in snapshots:
            if snapshot['state'] != 'SNAPSHOT_DELETING':
                snapshot_id_lst.append(snapshot['id'])
        return 0, snapshot_id_lst


def create_snaps(case_ip, index):
    """
    author:LiangXiaoyu
    date:2018-08-04
    description:在脚本目录下创建以index为名的快照
    :param case_ip:执行mkdir命令的ip
    :param index:快照名
    :return:创建命令的rc，创建快照的path参数
    changelog:
    """
    name = "%s%s%d" % (FILE_NAME, "_snapshot", index)
    create_path = os.path.join(SNAP_TRUE_PATH, str(index))
    cmd_mk = ("mkdir %s" % (create_path))
    rc_mk, std_mk = common.run_command(case_ip, cmd_mk)
    path = snap_common.VOLUME_NAME + ':/' + CREATE_SNAP_PATH + '/' + str(index)
    rc, stdout = snap_common.create_snapshot(name, path)
    stdout = json.loads(stdout)
    rc_get, snapshot_id_lst = get_snapshot_ids_base()
    if 0 != len(snapshot_id_lst):
        log.info("Maybe the snapshot already exsit")
        return rc, len(snapshot_id_lst)
    return rc, path


def case():
    log.info("case begin")
    """随机客户端节点"""
    ob_node = common.Node()
    case_ip_lst = ob_node.get_external_client_ips()
    case_ip = random.choice(case_ip_lst)
    path_lst = []
    """使用iozone创建1个文件"""
    test_file = os.path.join(SNAP_TRUE_PATH, "aaa")
    cmd = ("iozone -s 1m -i 0 -f %s -w" % test_file)
    rc, stdout = common.run_command(case_ip, cmd)
    if rc != 0:
        raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s " % (cmd, stdout))
    """在2个路径(PATH_NUM - 1)下创建快照,返回快照id和path的值"""
    for z in range(1, PATH_NUM):
        rc_create, std_create = create_snaps(case_ip, z)
        if rc_create == 0:
            path_lst.append(std_create)
        else:
            raise Exception('create_snapshot failed:%d!!!' % rc_create)

    """
    path参数值形如：volume1:/snap/P300_2045/1
    返回的id值为list
    """
    rc_get, snap_get = get_snapshot_ids_base()
    if 0 != rc_get:
        raise Exception("case file:get_snapshot failed")
    rc_get_by, snap_get_by = snap_common.get_snapshot_ids_by_path(path_lst[0])
    if 0 != rc_get_by:
        raise Exception("case file:get_snapshot by path failed:%s" % path_lst[0])

    """是否生效:list内部无重复的元素，可转为set；两个set取交集检查是否符合预期"""
    rst = set(snap_get) & set(snap_get_by)
    if list(rst) != snap_get_by:
        log.error("by path:%s is same as None:%s" % (snap_get_by, snap_get))
        raise Exception("case file!")
    log.info("case succeed")

    return


def main():
    prepare_clean.snap_test_prepare(FILE_NAME)
    case()
    prepare_clean.snap_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
