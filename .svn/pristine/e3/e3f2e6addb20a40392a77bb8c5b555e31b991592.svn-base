# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import prepare_clean
import random
####################################################################################
#
# author 梁晓昱
# date 2018-07-24
# @summary：
#     缺陷自动化：对set_ntp进行格式校验
# @steps:
#    1、确定不符合规则的配置内容
#    2、set_ntp
#    3、set_ntp失败则返回正确结果；否则，检测不通过
# @changelog：
#
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字


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
    format_err_str = "sadfgfhhghj"

    rc, stdout = common.set_ntp(is_enabled="true", ntp_servers=format_err_str, sync_period=5)
    msg_set_ntp = common.json_loads(stdout)
    set_ntp_rst = msg_set_ntp["err_no"]

    if 0 != int(rc):
        if 0 != set_ntp_rst:
            log.info("set_ntp format check is ok")
        else:
            log.info("some problem in msg_set_ntp:%d" % set_ntp_rst)
    else:
        log.error("set_ntp format check failed with string:%s\n)" % format_err_str)
        raise Exception("case failed!!!")


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
