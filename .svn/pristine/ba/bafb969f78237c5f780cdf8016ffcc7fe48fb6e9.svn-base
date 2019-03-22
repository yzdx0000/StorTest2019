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
import random
import nas_common
import json
"""
Author:liangxy
date 2018-08-31
@summary：
     缺陷自动化：disable_nas执行成功后立刻执行enable_nas
@steps:
    1、创建访问区
    2、检查nas状态，若没启动nas则先enable_nas；
    3、enable_nas
    4、检查环境，返回结果

@changelog：todo_

           添加的访问区，在nas完全交付后删除；

           disable nas 后最少需要6分钟（经验值）才可完全生效

"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
MAX_WAIT_TIME = 6000


def random_choose_node(ob_node):
    '''
        name  :      delete_disk_random_beta
        parameter:   common库中的node类
        author:      LiangXiaoyu
        date  :      2018.07.13
        Description: 返回一个随机得到的node_id和IP
        @changelog：
        '''
    nodeid_list = ob_node.get_nodes_id()
    '''随机选一个节点'''
    fault_node_id = random.choice(nodeid_list)
    return fault_node_id


def case():
    log.info("case begin")
    '''随机节点'''
    ob_node = common.Node()
    case_node_id = random_choose_node(ob_node)
    case_ip = ob_node.get_node_ip_by_id(case_node_id)

    msg_get_az = nas_common.get_access_zones(None)
    az_total_num_org = msg_get_az["result"]["total"]
    if 0 != int(az_total_num_org):
        for left_azs in msg_get_az["result"]["access_zones"]:
            log.error("nas_cleaning failed,left access zone:%s to delete" % left_azs["id"])
            msg_clean_az = nas_common.delete_access_zone(left_azs["id"])
            common.judge_rc(msg_clean_az, 0, "clean access zone:%s after nas_cleaning() failed" % left_azs["id"])
    msg_add_az = nas_common.create_access_zone(case_node_id, FILE_NAME + "_az")
    common.judge_rc(msg_add_az["err_no"], 0, "add az info:" + msg_add_az["detail_err_msg"])
    id_az = msg_add_az["result"]

    '''确定nas状态,若是disable状态则先enable'''
    msg_get_az = nas_common.get_access_zones(id_az)
    nas_status_org = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
    cmp_nas_status = cmp(False, nas_status_org)
    time_count = 0
    if 0 == cmp_nas_status:

        while True:
            msg_enable_nas = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
            enable_nas_rst = msg_enable_nas["err_no"]
            if 0 != int(enable_nas_rst):

                log.error("enable_nas_rst failed and exit:\n%s" % enable_nas_rst)
                raise Exception("case failed!!!")
            log.info("wait for enable_nas active:")
            time.sleep(20)
            time_count += 20
            log.info("%d s" % time_count)
            msg_get_az = nas_common.get_access_zones(None)
            nas_status_enable = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
            cmp_nas_status_en = cmp(True, nas_status_enable)
            if 0 != int(cmp_nas_status_en):

                if MAX_WAIT_TIME < time_count:
                    log.error("wait for nas enable active too long:%d s" % time_count)
                    raise Exception("case failed!!!")
            else:

                log.info("enable_nas succeed:\n%s " % (msg_get_az["result"]["access_zones"][0]))
                break

    '''核心操作，disable成功拿到后立刻enable'''
    msg_get_az = nas_common.get_access_zones(None)
    msg_disable_nas = nas_common.disable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    disable_nas_rst = msg_disable_nas["err_no"]
    if 0 != disable_nas_rst:

        log.error("disable_nas_rst failed and exit:\n%s" % disable_nas_rst)
        raise Exception("case failed!!!")
    else:

        log.info("disable_nas succeed;It's time to enable_nas")
    msg_enable_rst = nas_common.enable_nas(msg_get_az["result"]["access_zones"][0]["id"])
    enable_final_rst = msg_enable_rst["err_no"]
    if 0 != int(enable_final_rst):

        log.error("immediately enable nas failed failed and exit")
        raise Exception("case failed!!!")
    else:

        msg_get_az = nas_common.get_access_zones(None)
        nas_status_final = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
        cmp_nas_status_final = cmp(True, nas_status_final)
        if 0 != int(cmp_nas_status_final):
            log.info("enable nas not active yet ")
            time_count = 0
            while True:
                msg_get_az = nas_common.get_access_zones(None)
                nas_status_enable = msg_get_az["result"]["access_zones"][0]["nas_service_enabled"]
                cmp_nas_status_en = cmp(True, nas_status_enable)

                if 0 != int(cmp_nas_status_en):

                    if MAX_WAIT_TIME < time_count:

                        log.error("wait for nas enable active too long:%d s" % time_count)
                        raise Exception("case failed!!!")

                    log.info("wait for enable_nas active:")
                    time.sleep(20)
                    time_count += 20
                    log.info("%d s" % time_count)
                else:

                    log.info("After disable_nas, immediately enable_nas succeed")
                    break
        else:

            log.info("enable nas active(wait 0 s)")
    return


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
