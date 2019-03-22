#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 修改用户/用户组管理员权限
#######################################################

import os

import utils_path
import log
import nas_common
import common
import prepare_clean

# 当前脚本名称
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、连接NIS认证服务器；
        pscli --command=add_auth_provider_nis --name=name1 --domain_name=nistest --ip_addresses=10.2.41.247
        2、添加NIS用户/用户组到NAS客户端的smb用户/用户组；
        pscli --command=add_smb_export_auth_clients --name=u1 --export_id=x --type=USER --run_as_root=true
        pscli --command=add_smb_export_auth_clients --name=g1 --export_id=x --type=GROUP --run_as_root=true
        3、修改NAS客户端的smb用户/用户组；
        pscli --command=update_smb_export_auth_client --id=x run_as_root=true
        pscli --command=update_smb_export_auth_client --id=x run_as_root=false --permission_level=ro
    :return:
    """
    log.info("（2）executing_case")

    # add_auth_provider_nis
    nis_auth_provider_name = "nas_16_0_4_81_nis_auth_name"
    # create_access_zone
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    name = "nas_16_0_4_81_access_zone_name"
    # create_file
    create_file_path = nas_common.ROOT_DIR + "nas_16-0-4-81_dir"
    # create_smb_export
    export_name = "nas_16_0_4_81_smb_export_name"
    # add_smb_export_auth_clients
    smb_export_auth_clients_name_1 = "nas_16-0-4-81_user_1"
    smb_export_auth_clients_name_2 = "nas_16-0-4-81_group"

    check_result1 = nas_common.add_auth_provider_nis(name=nis_auth_provider_name,
                                                     domain_name=nas_common.NIS_DOMAIN_NAME,
                                                     ip_addresses=nas_common.NIS_IP_ADDRESSES)
    if check_result1["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result1 = check_result1["result"]

    check_result2 = nas_common.check_auth_provider(provider_id=result1)
    if check_result2["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result3 = nas_common.create_access_zone(node_ids=nodes_id_str,
                                                  name=name,
                                                  auth_provider_id=result1)
    if check_result3["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result2 = check_result3["result"]

    check_result4 = nas_common.create_file(path=create_file_path)
    if check_result4["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result5 = nas_common.create_smb_export(access_zone_id=result2,
                                                 export_name=export_name,
                                                 export_path=create_file_path)
    if check_result5["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result3 = check_result5["result"]

    check_result6 = nas_common.add_smb_export_auth_clients(export_id=result3,
                                                           name=smb_export_auth_clients_name_1,
                                                           user_type="USER",
                                                           run_as_root="true")
    if check_result6["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result4 = check_result6["result"][0]

    check_result7 = nas_common.add_smb_export_auth_clients(export_id=result3,
                                                           name=smb_export_auth_clients_name_2,
                                                           user_type="GROUP",
                                                           run_as_root="true")
    if check_result7["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    result5 = check_result7["result"][0]

    check_result8 = nas_common.update_smb_export_auth_client(auth_client_id=result4,
                                                             run_as_root="false",
                                                             permission_level="rw")
    if check_result8["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result9 = nas_common.update_smb_export_auth_client(auth_client_id=result5,
                                                             run_as_root="false",
                                                             permission_level="ro")
    if check_result9["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)

    check_result10 = nas_common.get_smb_export_auth_clients(export_ids=result3)
    if check_result10["detail_err_msg"] != "":
        log.error(("%s Failed") % FILE_NAME)
        raise Exception(("%s Failed") % FILE_NAME)
    smb_export_auth_clients = check_result10["result"]["smb_export_auth_clients"]

    for smb_export_auth_client in smb_export_auth_clients:
        if smb_export_auth_client["type"] == "GROUP":
            if smb_export_auth_client != {
                "export_id": int(result3),
                "id": int(result5),
                "key": int(result5),
                "name": "%s" % smb_export_auth_clients_name_2,
                "permission_level": "ro",
                "run_as_root": False,
                "type": "GROUP",
                "version": 0
            }:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
        elif smb_export_auth_client["type"] == "USER":
            if smb_export_auth_client != {
                "export_id": int(result3),
                "id": int(result4),
                "key": int(result4),
                "name": "%s" % smb_export_auth_clients_name_1,
                "permission_level": "rw",
                "run_as_root": False,
                "type": "USER",
                "version": 0
            }:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

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

    prepare_clean.nas_test_prepare(FILE_NAME)
    preparing_environment()
    executing_case()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()

    return

class Nas_Class_16_0_x_x():
    def nas_method_16_0_x_x(self):
        nas_main()

if __name__ == '__main__':
    nas_main()
