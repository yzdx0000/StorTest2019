#-*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：16-0-0-73 名称的特殊字符测试
# 2018.11.03， zhangcy, 1.修改清理环境为prepare_clean的内容
#######################################################

import os

import utils_path
import commands
import common
import log
import nas_common
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
        1、集群添加nis认证服务器，名称输入特殊字符；
        pscli --command=add_auth_provider_nis --name=nis_test --domain_name=xxx --ip_addresses=x.x.x.x
    """
    log.info("（2）executing_case")

    # name非法性检查，包括特殊字符
    illegal_name_1 = "1_nas_16_0_0_73_nis_auth_name"
    illegal_name_2 = "_nas_16_0_0_73_nis_auth_name"
    illegal_name_3 = "nas_16_0_0_73_nis-auth_name"
    illegal_name_4 = "nas_16_0_0_73_nis!_auth_name"
    illegal_name_5 = "nas_16_0_0_73_nis@_auth_name"
    illegal_name_6 = "nas_16_0_0_73_nis#_auth_name"
    illegal_name_7 = "nas_16_0_0_73_nis\$_auth_name"
    illegal_name_8 = "nas_16_0_0_73_nis%_auth_name"
    illegal_name_9 = "nas_16_0_0_73_nis^_auth_name"
    illegal_name_10 = "nas_16_0_0_73_nis\&_auth_name"
    illegal_name_11 = "nas_16_0_0_73_nis*_auth_name"
    illegal_name_12 = "nas_16_0_0_73_nis\(_auth_name"
    illegal_name_13 = "nas_16_0_0_73_nis\)_auth_name"
    illegal_name_14 = "nas_16_0_0_73_nis\+_auth_name"
    illegal_name_15 = "nas_16_0_0_73_nis\=_auth_name"
    illegal_name_16 = "nas_16_0_0_73_nis\/_auth_name"
    illegal_name_list = [illegal_name_1, illegal_name_2, illegal_name_3, illegal_name_4, illegal_name_5,
                         illegal_name_6, illegal_name_7, illegal_name_8, illegal_name_9, illegal_name_10,
                         illegal_name_11, illegal_name_12, illegal_name_13, illegal_name_14, illegal_name_15,
                         illegal_name_16]

    # can only consist of letters, numbers and underlines, begin with a letter.
    for illegal_name in illegal_name_list:
        log.info("illegal_name = %s" % illegal_name)
        check_result1 = nas_common.add_auth_provider_nis(name=illegal_name,
                                                         domain_name=nas_common.NIS_DOMAIN_NAME,
                                                         ip_addresses=nas_common.NIS_IP_ADDRESSES)
        if check_result1["detail_err_msg"].find("can only consist of letters, numbers and underlines") == -1:
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
    preparing_environment()
    prepare_clean.nas_test_prepare(FILE_NAME)
    executing_case()
    if nas_common.DEBUG != "on":
        prepare_clean.nas_test_clean()

    return


if __name__ == '__main__':
    common.case_main(nas_main)