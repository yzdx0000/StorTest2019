#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-x-x 共享路径长度极限测试
#######################################################

import os

import utils_path
import log
import nas_common
import common
import prepare_clean
import get_config

# 当前脚本名称
VOLUME_NAME = get_config.get_one_volume_name()
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字
NAS_PATH = get_config.get_one_nas_test_path()                            # /mnt/volume/nas_test_dir
NAS_TRUE_PATH = os.path.join(nas_common.NAS_PATH, FILE_NAME)             # /mnt/volume/nas_test_dir/nas_16_6_0_16
BASE_NAS_PATH = os.path.dirname(NAS_PATH)                                # /mnt/volume
NAS_PATH_BASENAME = os.path.basename(NAS_PATH)                           # nas_test_dir
SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    """
        1、创建一个共享路径长度为1024的smb共享；
        2、创建一个共享路径长度为1023的smb共享；
    :return:
    """
    log.info("（2）executing_case")

    '''1> 创建3节点访问分区az1，启动nas服务'''
    """同步NTP"""
    cmd = 'pscli --command=set_ntp --is_enabled=true --ntp_servers=%s' % nas_common.AD_DNS_ADDRESSES
    rc, stdout = common.run_command(SYSTEM_IP_0, cmd)
    common.judge_rc(rc, 0, 'set ntp failed !!!')

    """创建AD认证"""
    log.info("\t[ 2.add_auth_provider_ad ]")
    ad_server_name = 'ad_server_' + FILE_NAME
    exe_info = nas_common.add_auth_provider_ad(ad_server_name, nas_common.AD_DOMAIN_NAME, nas_common.AD_DNS_ADDRESSES,
                                               nas_common.AD_USER_NAME, nas_common.AD_PASSWORD,
                                               services_for_unix="NONE")
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('add auth provider ad %s failed !!!' % ad_server_name)
        raise Exception('add auth provider ad %s failed !!!' % ad_server_name)
    ad_server_id = exe_info['result']

    """get_auth_providers_ad"""
    log.info("\t[ 3.get_auth_provider_ad ]")
    exe_info = nas_common.get_auth_providers_ad(ad_server_id)
    ad_server = exe_info['result']['auth_providers'][0]
    if ad_server['name'] == ad_server_name and ad_server['domain_name'] == nas_common.AD_DOMAIN_NAME and \
            ad_server['id'] == ad_server_id and ad_server['name'] == ad_server_name:
        log.info('params of auth provider are correct !')
    else:
        log.error('params of auth provider are wrong !!!')
        raise Exception('params of auth provider are wrong !!!')

    """check_auth_provider"""
    nas_common.check_auth_provider(ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('check auth provider failed !!!')
        raise Exception('check auth provider failed !!!')

    """创建访问分区"""
    obj_node = common.Node()
    nodes_id_list = obj_node.get_nodes_id()
    nodes_id_str = ','.join(str(p) for p in nodes_id_list)
    access_zone_name = 'az_' + FILE_NAME
    exe_info = nas_common.create_access_zone(nodes_id_str, access_zone_name, ad_server_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('create access zone %s failed !!!' % access_zone_name)
        raise Exception('create access zone %s failed !!!' % access_zone_name)
    access_zone_id = exe_info['result']

    """启动nas服务"""
    exe_info = nas_common.enable_nas(access_zone_id)
    if exe_info["err_msg"] != "" or exe_info["detail_err_msg"] != "":
        log.error('enable nas failed !!!')
        raise Exception('enable nas failed !!!')

    # 测试路径最大长度1024
    # 按/mnt/volume/dir...计算路径长度
    # 路径总长度 = 5 + len("nas_common.VOLUME_NAME") + 1 + 待构造的路径长度

    dir_name = ""
    get_file_list_path = ""
    dir_name_list = ["nas_16-0-4-32_dir"]
    file_path_base = '/mnt/' + nas_common.VOLUME_NAME + NAS_PATH_BASENAME
    get_file_list_path_list = [nas_common.ROOT_DIR]
    create_file_path = nas_common.ROOT_DIR + "nas_16-0-4-32_dir"
    create_file_path_list = [create_file_path]

    for i in range(17): # 构造create_file_path_list 16次：前15次是256*15，最后一次是bbb和ccc；循环创建、查询17次
        print "count = %s" % (i + 1)
        if i < 15:      # 循环前15次
            # 前15次是256*15
            dir_name = "a" * 60
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path + "/" + dir_name
            create_file_path_list.append(create_file_path)

            check_result1 = nas_common.create_file(path=create_file_path_list[i])
            if check_result1["detail_err_msg"] != "":
                log.info("%s" % check_result1["detail_err_msg"])

            check_result2 = nas_common.get_file_list(path=get_file_list_path_list[i])
            if check_result2["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result2["result"]["files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if cmp(file, {
                        "auth_provider_id": 0,
                        "name": "%s" % dir_name_list[i],
                        "path": "%s" % create_file_path_list[i],
                        "type": "DIR"
                    }) != 0:
                        log.error(("%s Failed") % FILE_NAME)
                        raise Exception(("%s Failed") % FILE_NAME)
        elif i == 15:   # 循环第16次
            # 构造供第17次使用的create_file_path_list，先构造bbb，再构造ccc
            # 先构造bbb：4096 - 5 - len(nas_common.VOLUME_NAME) - 1，预期创建失败
            dir_name = "b" * (1019 - len(file_path_base) - 60*15 - len("/"))
            dir_name_list.append(dir_name)

            create_file_path_old = create_file_path
            get_file_list_path = create_file_path_old
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path_old + "/" + dir_name
            create_file_path_list.append(create_file_path)

            # 创建、查询第16次
            check_result3 = nas_common.create_file(path=create_file_path_list[i])
            if check_result3["detail_err_msg"] != "":
                log.info("%s" % check_result3["detail_err_msg"])

            check_result4 = nas_common.get_file_list(path=get_file_list_path_list[i])
            if check_result4["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result4["result"]["files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if cmp(file, {
                        "auth_provider_id": 0,
                        "name": "%s" % dir_name_list[i],
                        "path": "%s" % create_file_path_list[i],
                        "type": "DIR"
                    }) != 0:
                        log.error(("%s Failed") % FILE_NAME)
                        raise Exception(("%s Failed") % FILE_NAME)

        else:   # 循环第17次，只创建、查询，不构造dir_name_list[],get_file_list_path_list[],create_file_path_list[]
            check_result5 = nas_common.create_file(path=create_file_path_list[i])
            if check_result5["detail_err_msg"].find("exceed the max length:1019") == -1:
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)

            # 构造完删除dir_name_list[],get_file_list_path_list[],create_file_path_list[]最后一个元素
            dir_name_list.remove(dir_name)
            get_file_list_path_list.remove(get_file_list_path)
            create_file_path_list.remove(create_file_path)

            # 再构造ccc：4095 - 5 - len(nas_common.VOLUME_NAME) - 1，预期创建成功
            dir_name = "c" * (1018 - len(NAS_PATH_BASENAME) - 60*16 - len("/"))
            dir_name_list.append(dir_name)

            get_file_list_path = create_file_path_old
            get_file_list_path_list.append(get_file_list_path)

            create_file_path = create_file_path_old + "/" + dir_name
            create_file_path_list.append(create_file_path)

            check_result4 = nas_common.create_file(path=create_file_path_list[-1])
            if check_result4["detail_err_msg"] != "":
                log.info("%s" % check_result4["detail_err_msg"])

            check_result5 = nas_common.get_file_list(path=get_file_list_path_list[-1])
            if check_result5["detail_err_msg"] != "":
                log.error(("%s Failed") % FILE_NAME)
                raise Exception(("%s Failed") % FILE_NAME)
            files = check_result5["result"]["files"]
            for file in files:
                if file["path"] == create_file_path_list[i]:
                    if cmp(file, {
                        "auth_provider_id": 0,
                        "name": "%s" % dir_name_list[i],
                        "path": "%s" % create_file_path_list[i],
                        "type": "DIR"
                    }) != 0:
                        log.error(("%s Failed") % FILE_NAME)
                        raise Exception(("%s Failed") % FILE_NAME)

    print len(create_file_path)
    check_result = nas_common.create_smb_export(access_zone_id=access_zone_id,
                                                 export_name="nas_16_0_4_32_smb_export_name",
                                                 export_path=create_file_path)
    if check_result["detail_err_msg"] != "":
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
