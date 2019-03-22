#-*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import shell
import get_config
import prepare_clean
import random
import nas_common
import json
"""
author@liangxy
date 2018-08-02
@summary：
     缺陷自动化：没有配置子网ip，多个访问区使用同一个访问区的本地认证，check成功（预期失败）
@steps:
    1、在第一个点上创建访问区FILE_NAME_1，获取访问区FILE_NAME_1的本地认证服务器idx4
    2、在第二个点上创建访问区FILE_NAME_2，指定其认证服务器为idx4
    3、check idx4，检查结果，若成功或为空则返回case failed
    4、删除创建的访问区（添加新建访问区时要保存azid进列表以待删除）
@changelog：
    最后修改时间：2018-0804
    修改内容：根据nas交付进度，更新删除函数
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
LEAST_NODES = 2


def case():
    log.info("case begin")
    """节点列表"""

    ob_node = common.Node()
    node_num = ob_node.get_nodes_num()
    if LEAST_NODES > node_num:
        raise Exception("nodes total number less than 2:%d" % node_num)
    case_node_id_lst = ob_node.get_nodes_id()
    """id_az_lst为添加后要删除的访问区列表"""
    id_az_lst = []
    '''
    添加第一个节点上访问分区作为本地认证的来源
    '''
    msg_add_az1 = nas_common.create_access_zone(case_node_id_lst[0], FILE_NAME + "az1")
    if "" != msg_add_az1["detail_err_msg"]:
        raise Exception("create az in node %s failed" % case_node_id_lst[0])
    msg_get_az1 = nas_common.get_access_zones(ids=msg_add_az1["result"])
    local_id_in_az = msg_get_az1["result"]["access_zones"][0]["auth_provider"]["id"]
    log.info("choose local provider id is %d" % local_id_in_az)
    id_az_lst.append(msg_add_az1["result"])

    """添加第二个点上的访问区，指定认证服务器为local_id_in_az"""
    msg_add_az2 = nas_common.create_access_zone(case_node_id_lst[1], FILE_NAME + "az2", local_id_in_az)
    if "" != msg_add_az2["detail_err_msg"]:
        raise Exception("create az in node %s failed" % case_node_id_lst[1])
    id_az_lst.append(msg_add_az2["result"])
    """check provider local"""
    msg_check_provider = nas_common.check_auth_provider(local_id_in_az)
    err_info = msg_check_provider["detail_err_msg"]

    """检查check结果"""
    if "" == err_info:
        raise Exception("case failed!!!check provider should failed")
    rst_str_find = err_info.find("please configure the SVIP")
    if -1 == rst_str_find:
        raise Exception("case failed!!!\n"
                        "error info of check is wrong(should include \"please configure the SVIP\")")
    else:
        log.info("case succeed!")
    """删除添加的访问区"""
    for id_az in id_az_lst:
        msg_delete_azs = nas_common.delete_access_zone(id_az)
        if "" != msg_delete_azs["detail_err_msg"]:
            raise Exception("delete az in node %s failed" % id_az)
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
