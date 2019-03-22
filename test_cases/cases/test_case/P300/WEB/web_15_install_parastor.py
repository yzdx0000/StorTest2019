# -*-coding:utf-8 -*

import os

import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----1、检查节点运维界面带宽和iops是否为N/A
# 脚本作者：duyuli
# 日期：2018-12-17
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
control_ip_list = get_config.get_allparastor_ips()
parastor_name = "duyuli"

def get_data_ip_dict():
    data_ip_dict = {}
    for node_ip in control_ip_list:
        data_ip_20 = '20.' + '.'.join(node_ip.split('.')[1:])
        data_ip_30 = '30.' + '.'.join(node_ip.split('.')[1:])
        data_ip_dict[node_ip] = [data_ip_20, data_ip_30]

    return data_ip_dict

def get_tar_path():
    web_ip = get_config.get_web_ip()
    dir_path = "/home/deploy"
    cmd1 = "ls %s | grep ParaStor-3.0.0-centos7.5 | grep -v .tar" % dir_path
    rc, stdout1 = common.run_command(web_ip, cmd1)
    stdout1 = stdout1.strip()
    cmd2 = "ls %s | grep parastor-3.0.0-centos7.5 | grep .tar" % (dir_path + "/" + stdout1)
    rc, stdout2 = common.run_command(web_ip, cmd2)
    stdout2 = stdout2.strip()
    path = os.path.join(dir_path, stdout1, stdout2)
    return path

def case():
    driver = web_common.init_web_driver(auto_connect=False)

    # 安装parastor系统
    obj_web_system_install = web_common.System_Install(driver)
    obj_web_system_install.install_parastor(tar_path=get_tar_path(), parastor_name=parastor_name,
                                            control_ip_list=control_ip_list,
                                            data_ip_dict=get_data_ip_dict())

    # web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
