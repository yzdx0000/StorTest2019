# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time

import common
import log
import get_config
import prepare_clean
import upgrade_common
import json

####################################################################################
#
# author 刘俊鑫
# date 2018-07-23
# @summary：
#   执行在线升级操作
#   执行该脚本前需要将升级包放到要升级的集群上，并把路径写到p300_test_config.xml
#   e.g.10.2.42.155:/root/ofs3.0/ParaStor3.0.0_20180801_2/parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
# @steps:
#   step1: 检查是否符合升级
#   step2: 执行升级前检查
#   step3：分发安装包
#   step4: 执行在线升级
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                       # 本脚本名字
nodes = get_config.get_allparastor_ips()                                          # 获取集群ip
package_ip = get_config.get_upgrade_package_ip()                                  # 升级包所在ip
package_path = get_config.get_upgrade_package_path()
# 升级包路径 e.g./root/ofs3.0/ParaStor3.0.0_20180801_2/
#              parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
package_name = os.path.basename(package_path)
# 升级包名称 e.g.parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_96d473b_20180801_174109-2-1.tar.xz
version, min_version = upgrade_common.get_version_baseon_package_name(package_name)
# 根据升级包获取version以及最小兼容版本minversion
system_version = int(upgrade_common.get_system_version())                         # 获取系统运行包的版本
upgrade_package_time = get_config.get_upgrade_package_time()                      # 升级包时间 e.g.20180801174109
system_package_time = upgrade_common.get_system_package_time()                    # 系统运行包日期版本 e.g.20180801768


def delete_upgrade():
    nodes = get_config.get_allparastor_ips()                                      # 删除/home/parastor/upgrade/目录
    cmd = 'rm -rf /home/parastor/upgrade/'
    for node in nodes:
        rc, stdout = common.run_command(node, cmd)
        if rc != 0:
            raise Exception('run_command failed\ncmd=%s\nstdout=%s' % (cmd, stdout))


def case():
    """

    :return:
    """
    """
    先检查升级包版本是否新与当前版本
    若包的日期小于系统包日期，则不进行升级
    若两者一致，则修改当前系统版本号进行同包更新
    若包的日期大于系统包日期，则判断是否兼容
    """
    if upgrade_package_time < system_package_time:
        log.info("#########版本过低，请检查升级包版本##########")
        return
    elif upgrade_package_time == system_package_time:
        log.info("##########修改系统包日期，即将升级##########")
        upgrade_common.set_system_package_time()
    elif upgrade_package_time > system_package_time:
        if system_version < min_version:
            log.info("system version:%d is lowwer than the package's min compatible version of package: %d"
                     % (system_version, min_version))
            return
        elif system_version >= min_version and system_version > version:
            log.info("this package's capatible version is %s, but you system version is %s" % (version,
                                                                                               system_version))
            return
        elif system_version >= min_version and system_version <= version:
            log.info("###############系统即将升级###############")

    """升级前检查"""
    log.info("################升级前检查#################")
    stdout = upgrade_common.check_before_upgrade()
    # check_result = common.json_loads(stdout)
    error_info = []
    for item in stdout['result']['service_items']:
        if item['items'][0]['suggestion'] != "":
            info = json.dumps(item)
            error_info.append(info)
    if error_info != []:
        log.info("###there is some problems in the system###")
        for item in error_info:
            log.info(item)

    """分发安装包"""
    log.info("################分发安装包#################")
    upgrade_common.distribute_package(package_ip, package_path)

    """执行升级"""
    log.info("################执行在线升级###############")
    # upgrade_common.online_upgrade(package_ip, package_name, upgrade_package_time)
    process_upgrade_online = Process(target=upgrade_common.online_upgrade, args=(package_ip, package_name,
                                                                                 upgrade_package_time))
    process_upgrade_online.start()
    time.sleep(10)

    """检查升级状态"""
    log.info("################检查升级状态###############")
    upgrade_time = 10
    while process_upgrade_online.is_alive():
        time_begin = time.time()
        upgrade_info = upgrade_common.get_upgrade_info()
        if upgrade_info['result']['upgrade_state'] == 'UPGRADE_STATE_UPGRADING':
            log.info("################系统正在升级中###############")
            log.info("#############升级进度：%s percent############" % upgrade_info['result']['upgraded_percent'])
            log.info("################升级用时：%ds###############" % upgrade_time)
        elif upgrade_info['result']['upgrade_state'] == 'UPGRADE_STATE_PREPARE':
            log.info("################升级结束################")
            break
        time.sleep(60)
        upgrade_time += time.time() - time_begin

    process_upgrade_online.join()


def main():
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
