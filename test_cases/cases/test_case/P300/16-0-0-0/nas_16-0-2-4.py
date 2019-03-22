#-*-coding:utf-8 -*
#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-2-4 10节点创建访问分区
#######################################################

import os

import utils_path
import log
import nas_common

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、创建10节点访问区；
        pscli --command=create_access_zone --node_ids=1,2,3,4,5,6,7,8,9,10 --name=access_zone_name --auth_provider_id=x
        注：--auth_provider_id参数中x代表认证服务器id；
        2、查询创建的访问区是否正确；
    :return:
    """
    log.info("（2）executing_case")

    node_ids = "1,2,3,4,5,6,7,8,9,10"
    node_id_list = [int(x) for x in node_ids.split(",")]    # 把"1,2,3"转换成[1,2,3]
    node_name_list = nas_common.get_node_name_list(node_id_list)
    access_name = "nas_16_0_2_4_access_zone_name"

    check_result1 = nas_common.create_access_zone(node_ids=node_ids,
                                                  name=access_name)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result = check_result1["result"]

    check_result2 = nas_common.get_access_zones(ids=result)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    access_zone = check_result2["result"]["access_zones"][0]
    if cmp(access_zone,{
                "access_zone_state": "ACCESSZONE_READY",
                "auth_provider": {
                    "id": 4,
                    "key": 4,
                    "name": access_name,
                    "type": "LOCAL",
                    "version": 0
                },
                "auth_provider_id": 4,
                "enable_ftp": True,
                "enable_http": False,
                "enable_nfs": True,
                "enable_san": False,
                "enable_smb": True,
                "id": int("%s" % result),
                "key": int("%s" % result),
                "local_auth_provider_id": 4,
                "max_node_number": 0,
                "name": access_name,
                "node_ids": node_id_list,
                "nodes": [
                    {
                        "managerNode": False,
                        "node_id": node_id_list[0],
                        "node_name": node_name_list[0]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[1],
                        "node_name": node_name_list[1]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[2],
                        "node_name": node_name_list[2]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[3],
                        "node_name": node_name_list[3]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[4],
                        "node_name": node_name_list[4]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[5],
                        "node_name": node_name_list[5]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[6],
                        "node_name": node_name_list[6]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[7],
                        "node_name": node_name_list[7]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[8],
                        "node_name": node_name_list[8]
                    },
                    {
                        "managerNode": False,
                        "node_id": node_id_list[9],
                        "node_name": node_name_list[9]
                    }
                ],
                "san_protocol_state": "ISCSI_UNKNOWN",
                "version": 1
            }):
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    else:
        log.info(("%s Succeed") % FILE_NAME)

    return

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")

    '''
    1、下发nas相关的配置
    2、创建nas测试相关的目录和文件
    '''

    return

#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def nas_main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)

    nas_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        nas_common.cleaning_environment()

    return

class Nas_Class_16_0_2_4():
    def nas_method_16_0_2_4(self):
        nas_main()

if __name__ == '__main__':
    nas_main()