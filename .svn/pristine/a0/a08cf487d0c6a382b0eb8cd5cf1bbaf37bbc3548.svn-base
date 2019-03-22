# -*-coding:utf-8 -*
import os
import ConfigParser

import utils_path
import common
import log
import get_config
import prepare_clean

#################################################################
#
# Author: baorb
# date 2017-08-21
# @summary：
#    本测试主要测试dlm。
# @steps:
#    1，执行开发的dlm测试，主要是用mpirun工具运行
#
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 #本脚本名字
MOUNT_PATH = get_config.get_one_mount_path()
DLM_PATH = os.path.join(MOUNT_PATH, 'dlm')

SLOTS = 5


def setup_machines(machine_path):
    """获取所有客户端"""
    client_ip_lst = get_config.get_allclient_ip()
    machine_info = ''
    for client_ip in client_ip_lst:
        tem_str = '%s slots=%d\n' % (client_ip, SLOTS)
        machine_info += tem_str
    with open(machine_path, 'w') as f:
        f.write(machine_info)
    return


def setup_config(config_path):
    cf = ConfigParser.ConfigParser()
    try:
        cf.read(config_path)
    except:
        log.error('read %s failed!!!' % config_path)
        raise Exception('read %s failed!!!' % config_path)
    """获取mgrip"""
    mgrip = common.SYSTEM_IP
    """获取挂载路径"""
    client_dir = DLM_PATH
    """修改配置文件"""
    cf.set('parastor', 'mgrip', mgrip)
    cf.set('parastor', 'mpinp', str(SLOTS))
    cf.set('parastor', 'client_dir', client_dir)
    with open(config_path, 'w') as fw:
        cf.write(fw)


def case():
    """创建路径"""
    client_ip_lst = get_config.get_allclient_ip()
    cmd = 'ls %s' % DLM_PATH
    rc, stdout = common.run_command(client_ip_lst[0], cmd)
    if 0 != rc:
        cmd = 'mkdir %s' % DLM_PATH
        rc, stdout = common.run_command(client_ip_lst[0], cmd)
        if rc != 0:
            raise Exception('%s mkdir faild!!!' % DLM_PATH)
    """清理路径"""
    common.rm_exe(client_ip_lst[0], os.path.join(DLM_PATH, '*'))

    """获取dlm配置文件和可执行文件的路径"""
    tool_path = get_config.get_tools_path()
    dlm_path = os.path.join(tool_path, 'dlm')
    config_path = os.path.join(dlm_path, 'bin', 'st_config')
    machine_path = os.path.join(dlm_path, 'bin', 'machines')

    """修改machines文件"""
    setup_machines(machine_path)
    """修改st_config文件"""
    setup_config(config_path)

    cmd = 'scp -r %s root@%s:%s' % (dlm_path, client_ip_lst[0], DLM_PATH)
    common.command(cmd)

    """执行dlm"""
    rum_dlm_path = os.path.join(DLM_PATH, 'dlm', 'dlm_consist_run.py')
    cmd = 'ssh %s "python %s"' % (client_ip_lst[0], rum_dlm_path)
    rc = common.command(cmd)
    if 0 != rc:
        log.error('dlm is failed!!!')
        raise Exception('dlm is failed!!!')

    """删除路径"""
    common.rm_exe(client_ip_lst[0], DLM_PATH)
    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(fault=True)
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)