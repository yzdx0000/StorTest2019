# -*-coding:utf-8 -*
import os

import utils_path
import common
import nas_common
import log
import get_config
import prepare_clean


####################################################################################
#
# author 李一
# date 2018-08-1
# @summary：
#      创建共享目录失败的情况下，查看共享路径的获取情况
# @steps:
#     1、创建目录(使用命令pscli --command=create_file)；
#     2、为目录创建共享路径并获取该共享路径(使用命令pscli --command=create_nfs_export)；
#     3、清理目录以及共享路径信息
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
SYSTEM_IP = get_config.get_parastor_ip(0)


def case():
    # 准备工作：创建访问分区
    obj_node = common.Node()
    node_id_list = obj_node.get_nodes_id()
    node_ids = ','.join(str(i) for i in node_id_list)
    access_zone_name = FILE_NAME
    check_result = nas_common.create_access_zone(node_ids=node_ids,
                                                 name=access_zone_name)
    if check_result["detail_err_msg"] != "":
        raise Exception("create_access_zone is failed!!")
    access_zone_id = check_result["result"]
    check_result = nas_common.enable_nas(access_zone_id)
    if check_result["detail_err_msg"] != "":
        raise Exception("enable_nas is failed!!")

    # 1> 创建共享目录
    nfs_path = nas_common.ROOT_DIR + FILE_NAME
    check_result = nas_common.create_file(nfs_path)  # 创建/mnt/parastor/nas/filename
    if check_result["detail_err_msg"] != "":
        common.except_exit("create %s Failed" % nfs_path)

    # 2> 为目录创建共享路径
    export_name = FILE_NAME  # 共享名称
    export_path = nas_common.ROOT_DIR + FILE_NAME  # parastor:/nas/filename
    check_result = nas_common.create_nfs_export(access_zone_id, export_name, export_path)
    nfs_export_id = check_result["result"]
    if check_result["err_no"] == 21003:            # 创建共享路径失败时,错误码是21003
        check_result = nas_common.get_nfs_exports(nfs_export_id)
        export_info = check_result["result"]["export"]
        for export in export_info:
            if export["export_path"] == export_path:  # 创建失败，依然能获取到共享路径信息时，此系统有bug
                log.info("NOTE!!The Parastor system has bug!!!!!")


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
