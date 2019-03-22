# -*-coding:utf-8 -*
import os
import utils_path
import common
import get_config
import log
import prepare_clean
import snmp_common
import nas_common

####################################################################################
#
# author liyi
# date 2018-09-3
# @summary：
#           ctdb状态比较
# @steps:
#   准备：
#           1>部署集群环境
#           2>创建访问分区
#           3>启动nas的ctdb服务
#   执行：
#           1>通过snmp协议方式获取ctdb状态
#           2>通过p300系统发起请求获取到的ctdb状态
#           3>对两种方式获取到的ctdb状态进行比较

# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字
SYSTEM_IP_0 = get_config.get_parastor_ip(0)


def case():
    """

    :return:
    """

    '''准备'''
    '''1>部署集群环境'''
    '''2>创建访问分区'''
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    access_zone_name = FILE_NAME+"_Access_zone"
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=access_zone_name)
    if check_result["detail_err_msg"] != "":
        common.except_exit("create access zone failed!!")
    access_zone_id = check_result["result"]
    '''启动nas服务'''
    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("enable_nas failed!!")

    '''执行'''
    allparastor_ips = get_config.get_allparastor_ips()
    for node_ip in allparastor_ips:
        snmp_ctdb_status = snmp_common.get_one_node_service_ctdb_status(node_ip)
        ctdb_status = snmp_common.get_one_node_ctdb_status(node_ip)
        log.info("ctdb_status:%s" % ctdb_status)

        if snmp_ctdb_status != ctdb_status:
            common.except_exit("%s oapp_status compare is failed!!" % node_ip)
    log.info("oapp_status compare is succeed!!")


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
