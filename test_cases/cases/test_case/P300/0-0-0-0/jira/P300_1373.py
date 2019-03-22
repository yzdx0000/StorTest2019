# -*-coding:utf-8 -*
import os
import time
import random
import utils_path

import common
import nas_common
import log
import get_config
import re
import prepare_clean


####################################################################################
#
# author 李一
# date 2018-07-31
# @summary：
#      查看是否能正确显示AD服务器端的中文用户组信息
# @steps:
#     1、添加AD认证(使用命令pscli --command=add_auth_provider_ad)；
#     2、查看认证配置信息是否能够正确的连接ad认证服务器(使用命令pscli --command=check_auth_provider)；
#     3、检测ad端是否有中文用户组
#     4、如果存在中文用户组，显示用户组信息(使用命令pscli --command=get_auth_user)；
# @changelog：
####################################################################################
system_ip = get_config.get_parastor_ip(0)
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')


def case():
    # 1> 添加AD认证
    check_result = nas_common.add_auth_provider_ad(name=FILE_NAME+"_ad_provider",
                                                   domain_name=nas_common.AD_DOMAIN_NAME,
                                                   dns_addresses=nas_common.AD_DNS_ADDRESSES,
                                                   username=nas_common.AD_USER_NAME,
                                                   password=nas_common.AD_PASSWORD,
                                                   services_for_unix="RFC2307")
    if check_result["detail_err_msg"] != "":
        common.except_exit("add_auth_provider_ad failed!")
    ad_id = check_result["result"]

    # 2> 查看认证配置信息是否能够正确的连接ad认证服务器
    wait_time = random.randint(2, 5)
    time.sleep(wait_time)
    check_result = nas_common.check_auth_provider(ad_id)
    if check_result["detail_err_msg"] != "":
        common.except_exit("check_auth_provider failed!")

    # 3> 检测在ad端用户组中是否有中文用户组
    log.info("\t[case:Check whether there is a Chinese user ]")
    check_result = nas_common.get_auth_groups(auth_provider_id=ad_id)
    auth_groups = check_result["result"]["auth_groups"]
    auth_groups_list = []
    for auth_group in auth_groups:
        auth_groups_list.append(auth_group['name'])  # 生成用户组名字列表
    index = 0
    for ch_name in auth_groups_list:
        ch_name = ch_name.encode('utf-8')
        if contain_zh(ch_name):                    # 对auth_user_name_list中元素检查，是否有中文用户组
            break                                  # 只要检测到中文用户组，显示用户组信息
        else:
            index = index+1

    # 4> 查看ad端创建的中文用户是否可以正常显示
    if len(auth_groups_list) == index:             # 遍历列表，没找到中文用户时，输出没有中文用户的信息
        print("No Chinese User")
    else:
        log.info("\t[case:get_chinese_auth_user ]")
        check_result = nas_common.get_auth_groups(ad_id)
        if check_result["detail_err_msg"] != "":
            common.except_exit("%s Failed" % FILE_NAME)
    


def contain_zh(word):
    """
    :authon:     liyi
    :date:       2018.07.30
    :description:判断传入字符串是否包含中文
    :param word:待判断字符串
    :return:    True:包含中文  False:不包含中文
    """
    word = word.decode()
    global zh_pattern
    match = zh_pattern.search(word)
    return match


def main():
    prepare_clean.nas_test_prepare(FILE_NAME)
    log.info("case begin")
    case()
    prepare_clean.nas_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)



if __name__ == '__main__':
    common.case_main(main)
