#!/usr/bin/python
# -*- encoding=utf8 -*-
"""
 author chenjy1
 date 2018-10-29
 @summary：
    自动离线升级系统
 @changelog：
"""
from multiprocessing import Process
import os
import re
import sys
import time
import json
import traceback
import subprocess
import xml.dom.minidom
from optparse import OptionParser
import xml.etree.ElementTree as Et

import utils_path
import get_config
import common
import prepare_clean
import common
import log
import shell

reload(sys)
# sys.setdefaultencoding('utf8')

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
######################################################################################################
ip_lst = get_config.get_allparastor_ips()                               # 集群节点ip
client_tmp_lst = get_config.get_allclient_ip()                              # 私有客户端节点ip
client_lst = []
for client in client_lst:
    if client not in ip_lst:
        client_lst.append(client)
UNINSTALL_CLIENT_CMD = '/cliparastor/uninstall.py'                      # 卸载私有客户端命令
PKG_PATH = get_config.get_client_install_path()                         # 安装包目录
PACKAGE_IP = get_config.get_new_pkg_position().split(':')[0]            # 每天放新包的ip
NEWPACKAGE_PATH = get_config.get_new_pkg_position().split(':')[1]       # 位置
######################################################################################################

upgrade_item_default = 'server'
package_node_ip = ip_lst[0]
"""****************************** common ******************************"""
WAIT_COPY = True


def run_command(cmd, node_ip=None):
    rc, stdout = common.run_command(node_ip, cmd, print_flag=True)
    return rc, stdout


def command(cmd):
    log.info(cmd)
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    while True:
        line = process.stdout.readline()
        if '' == line:
            break
        log.debug(line.rstrip())
    process.wait()
    if process.returncode == 0:
        return 0
    else:
        return -1


def json_loads(stdout):
    try:
        stdout_str = json.loads(stdout, strict=False)
        return stdout_str
    except Exception, e:
        log.error(stdout)
        raise Exception("Error msg is %s" % e)

"""****************************** func ******************************"""
def check_ssh(ip_lst):
    for ip in ip_lst:
        cmd = "pwd"
        rc, stdout = run_command(cmd, ip)
        if rc != 0:
            raise Exception("ssh failed ")


def save_state():
    cmd = "pscli --command=get_node_stat"  # 此命令返回值不为0
    rc, stdout = run_command(cmd, ip_lst[0])
    # if rc!=0:
    #     raise  Exception("get_node_stat failed")
    return


def shutdown():
    cmd = 'pscli --command=shutdown'
    rc, stdout = run_command(cmd, ip_lst[1])
    return rc


def shutdown_force():
    cmd = 'pscli --command=shutdown_force'
    rc, stdout = run_command(cmd, ip_lst[1])
    return rc


def startup():
    cmd = 'pscli --command=startup'
    rc, stdout = run_command(cmd, ip_lst[0])
    if rc != 0:
        raise Exception("startup failed")


def get_centos(ip):
    cmd = 'cat  /etc/redhat-release'
    rc, stdout = run_command(cmd, ip)
    if rc != 0:
        raise Exception('failed')
    str_lst = stdout.split('.')
    return str_lst[0][-1] + '.' + str_lst[1][0]


def get_system_version(ip):
    cmd = "pscli --command=get_system_version"
    rc, stdout = run_command(cmd, ip)
    result = json_loads(stdout)
    system_version = result["result"]["system_version"]
    return int(system_version)


def get_system_package_time(ip):
    cmd = 'pscli --command=get_package_time'
    rc, stdout = run_command(cmd, ip)
    if rc != 0:
        raise Exception('run_command failed\ncmd=%s\nstdout=%s' % (cmd, stdout))
    result = json_loads(stdout)
    system_package_time_str = result['result']['package_time']
    system_package_time = system_package_time_str.split('_')[0] + '_' + system_package_time_str.split('_')[1]
    return system_package_time


def set_system_package_time(ip, system_package_time='20170101_000000'):
    cmd = 'pscli --command=set_package_time --package_time=%s' % system_package_time
    rc, stdout = run_command(cmd, ip)
    if rc != 0:
        raise Exception("failed")
    return


def cp_pkg(pkg_info):
    local_pkg = PKG_PATH
    common.rm_exe(pkg_info['cluster_pkg_ip'], os.path.join(PKG_PATH, "*"))
    cmd = "mkdir -p %s" % local_pkg
    rc, stdout = run_command(cmd, pkg_info['cluster_pkg_ip'])
    if rc != 0:
        raise Exception('failed')

    cmd = "scp %s root@%s:%s" % (pkg_info['sys_pkg'], pkg_info['cluster_pkg_ip'], local_pkg)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        raise Exception('failed')

    for ip in client_lst:
        common.rm_exe(ip, os.path.join(PKG_PATH, "*"))
        cmd = "mkdir -p %s" % local_pkg
        rc, stdout = run_command(cmd, ip)
        if rc != 0:
            raise Exception('failed')
        cmd = "scp %s root@%s:%s" % (pkg_info['client_pkg'], ip, local_pkg)
        rc, stdout = common.run_command_shot_time(cmd)
        if rc != 0:
            raise Exception('failed')
        cmd = "tar xvf %s -C %s" % (os.path.join(local_pkg, pkg_info['client_pkg_name']), local_pkg)
        rc, stdout = run_command(cmd, ip)
        if rc != 0:
            raise Exception('failed')


def distribute_package(package_ip, package_path):
    upgade_version = int(package_path[-10])
    cmd = 'pscli --command=distribute_package --host_ips=%s --path=%s --upgrade_version=%s' % (package_ip,
                                                                                               package_path,
                                                                                               upgade_version)
    rc, stdout = run_command(cmd, package_ip)
    if rc != 0:
        raise Exception('run command failed, cmd=%s, stdout is %s' % (cmd, stdout))
    return


def get_upgrade_info(node_ip):
    cmd = 'pscli --command=get_upgrade_info'
    rc, stdout = run_command(cmd, node_ip)
    result = {}
    if rc != 0:
        log.info('run_command failed\ncmd=%s\nstdout=%s' % (cmd, stdout))
    else:
        result = json.loads(stdout)
    return result


def ext_offline_upgrade(node_ip, package_name, package_time, upgrade_item=upgrade_item_default):
    """
        :author:  liujx
        :date:  2018.08.13
        :description: 执行离线升级命令
        :param node_ip:   执行命令的节点
        :param package_name:   升级包的名字
        :param package_time:   升级包的时间
        :param upgrade_item:   升级项
        :return:
        """
    version = package_name[-10]
    min_version = package_name[-8]
    cmd = 'pscli --command=offline_upgrade ' \
          '--version=%s --min_version=%s --package_time=%s --upgrade_item=%s' \
          % (version, min_version, package_time, upgrade_item)
    rc, stdout = run_command(cmd, node_ip)
    result = json_loads(stdout)
    return rc, result


def wait_new_pkg():
    """拷贝新包"""
    """获取当前版本"""
    rc, stdout = common.get_package_time()
    cur_pkg_time_str = ''
    if rc == 0:
        json_info = common.json_loads(stdout)
        cur_pkg_time_str = json_info['result']['package_time']
    else:
        common.judge_rc(rc, 0, 'get_package_time failed')

    """获取最新版本"""
    package_lst = []
    cmd = 'ls -Ft %s | grep "/$"' % NEWPACKAGE_PATH
    rc, stdout = common.run_command(PACKAGE_IP, cmd, print_flag=False)
    for line in stdout.splitlines():
        line = line.strip().strip('/')
        if re.match('\d{8}', line):
            package_lst.append(line)
    package_lst.sort(reverse=True)
    new_package = ''
    new_package_time = ''
    for package in package_lst:
        path = os.path.join(NEWPACKAGE_PATH, package)
        pkg_match_name = 'ParaStor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_*-2-1.tar'
        cmd = "ls -lt %s | sed -n 1p | awk '{print $NF}'" % os.path.join(path, pkg_match_name)
        rc, stdout = common.run_command(PACKAGE_IP, cmd)
        if rc != 0:
            continue
        new_package = stdout.split()[-1]
        new_package_time = re.findall('\d{8}_\d{6}', new_package)[0]
        break
    else:
        common.except_exit('cannot find pkg')

    if cur_pkg_time_str >= new_package_time:
        common.except_exit('no new pkg')

    """获取拷包的目的路径"""
    scripts_path = os.path.dirname(os.path.abspath(__file__))
    stortest_path = os.path.dirname(scripts_path)
    dest_pkg_path = os.path.join(stortest_path, 'src_code', 'P300')

    """清空目录"""
    cmd = "rm -rf %s" % os.path.join(dest_pkg_path, '*')
    common.run_command_shot_time(cmd)

    """拷包"""
    cmd = "scp -r root@%s:%s %s" % (PACKAGE_IP, new_package, dest_pkg_path)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        raise Exception('scp pkg failed')

    """解压"""
    total_tar_pkg_path = os.path.join(dest_pkg_path, os.path.basename(new_package))
    cmd = "tar xvf %s -C %s" % (total_tar_pkg_path, dest_pkg_path)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        raise Exception('tar xvf failed')

    total_pkg_path = os.path.splitext(total_tar_pkg_path)[0]
    sys_pkg_path = ''
    client_pkg_path = ''
    for pkg in os.listdir(total_pkg_path):
        'parastor-3.0.0-centos7.5-feature_ofs3.0_lastdebug_ac1222f_20190119_192417-2-1.tar.xz'
        if re.match('parastor-3\.0\.0-centos7\.5-feature_ofs3\.0_lastdebug_\w*_\d{8}_\d{6}-2-1\.tar\.xz', pkg):
            sys_pkg_path = pkg
        elif re.match('parastor-3\.0\.0-client-centos7\.5-feature_ofs3\.0_lastdebug_\w*_\d{8}_\d{6}\.tar\.xz', pkg):
            client_pkg_path = pkg

    sys_pkg_abspath = os.path.join(total_pkg_path, sys_pkg_path)
    client_pkg_abspath = os.path.join(total_pkg_path, client_pkg_path)

    pkg_info = {}
    pkg_info['sys_pkg'] = sys_pkg_abspath
    pkg_info['client_pkg'] = client_pkg_abspath
    pkg_info['sys_pkg_name'] = sys_pkg_path  # ok
    pkg_info['client_pkg_name'] = client_pkg_path  # ok
    pkg_info['cluster_pkg_ip'] = ip_lst[0]  # 10.2.40.8
    pkg_info['cluster_pkg_dir'] = os.path.join(PKG_PATH, pkg_info['sys_pkg_name'])

    for i in pkg_info:
        log.info("%s is %s" % (i, pkg_info[i]))
    return pkg_info


def get_volume_id(volume_name):
    cmd = "pscli --command=get_volumes"
    rc, stdout = run_command(cmd, ip_lst[0])
    if rc != 0:
        raise Exception("get_volumes failed")

    volumes = json_loads(stdout)
    volumes = volumes['result']['volumes']
    for volume in volumes:
        if volume['name'] == volume_name:
            volumeid = volume['id']
            return volumeid
    return None


def get_volume_name_on_client(client_ip):
    cmd = "pscli --command=get_cluster_overview"
    rc, stdout = run_command(cmd, ip_lst[0])
    if rc != 0:
        raise Exception("get_cluster_overview failed")
    cluster_name = json_loads(stdout)['result']['name']

    cmd = "mount |grep %s" % cluster_name
    rc, stdout = run_command(cmd, client_ip)
    # if rc !=0:
    #    raise Exception("failed")
    stdout_lst = stdout.split('\n')[:-1]
    volume_name_lst = []
    if stdout_lst != []:
        for line in stdout_lst:
            volume_name_lst.append(line.split()[0].replace(cluster_name + '_', ''))
    print volume_name_lst
    return volume_name_lst


def cmd_with_timeout(command, timeout=60):
    """
        :author:              chenjinyu
        :date  :              2018.07.27
        :description:         执行某个命令，如超时，则return '', ''
        :param command:      要执行的命令
        :param timeout=60:   超时时间
        :return:             如超时，则return -1, '', ''
                              没超时，则返回0, stdout, stderr
        """
    proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    poll_seconds = 1
    deadline = time.time() + timeout
    while time.time() < deadline and proc.poll() is None:
        time.sleep(poll_seconds)
    if proc.poll() is None:
        proc.kill()
        return -1, '', ''
    stdout, stderr = proc.communicate()
    return 0, stdout, stderr


def check_client_state(ip, volume_name, timeout=300):
    """
        :author:              chenjinyu
        :date  :              2018.07.27
        :description:         检查客户端是否卡住，是否掉了
        :param ip_list:      要检查的节点
        :param volume_name:  要检查的挂载卷名
        :return:             0:正常
                              -1:ssh 失败，需要检查节点
                              -2:客户端卡住
                              -3:挂载的卷丢失
        """
    rc, stdout = run_command('pwd', ip)
    if rc != 0:
        log.info("IP:%s ssh failed. \nstdout: %s" % (ip, stdout))
        return -1
    cmd = 'ssh %s df %s' % (ip, '/mnt/' + volume_name)
    rc, stdout, stderr = cmd_with_timeout(cmd, timeout)
    if rc:
        log.info('IP:%s df : client is blockup!!! \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
        return -2
    if rc == 0 and (volume_name not in stdout):
        log.info('IP:%s df : not found volume !!!  \nstdout: %s \nstderr: %s' % (ip, stdout, stderr))
        return -3
    return 0


def wait_client_find_volume(client_ip, volume_lst, timeout_blockup, timeout_wait):
    """
        :Author:                  chenjy1
        :Date:                    2018.09.03
        :param client_lst:       (str)要检查的节点管理网ip
        :param volume_name:      (str)要检查的卷名
        :param timeout_blockup:  (int)认为卡住的超时时间 秒
        :param timeout_wait:     (int)等待发现卷的时间（不包含卡住的时间）秒
        :return: ret_lst:        (list)元素个数和lient_lst一样，对应的值含义为:
                                    0:正常
                                   -1:执行脚本的节点ssh到该节点不通
                                   -2:该节点客户端卡住
                                   -3:该节点等了timeout_wait时间仍未发现卷
                                   None:未查到？此函数有问题
        """
    ret_lst = {}
    # for i in range(len(volume_lst)):
    #    ret_lst.append(None)
    tmp_timeout_wait = 0  # 临时timeout_wait,用于在timeout_wait中去掉timeout_blockup的时间
    flag_ip_volume = 1
    for i in range(len(volume_lst)):
        flag_ip_volume = (flag_ip_volume << 1)
    flag_ip_volume = flag_ip_volume >> 1
    res_ip_volume = flag_ip_volume

    start_time = time.time()
    while True:
        for i, volume_name in enumerate(volume_lst):
            if (flag_ip_volume & (1 << i)) != 0:
                res = check_client_state(client_ip, volume_name, timeout=timeout_blockup)
                ret_lst[volume_name] = res
                if (0 == res) or (-1 == res):
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))  # 将i对应的标志位置位
                elif -2 == res:
                    flag_ip_volume &= (res_ip_volume ^ (1 << i))
                    tmp_timeout_wait += timeout_blockup
                elif -3 == res:
                    log.info('still waiting %s' % volume_name)
        if flag_ip_volume & res_ip_volume == 0:  # 全0则获取到了全部状态
            break
        time.sleep(10)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('not found volume exist %dh:%dm:%ds' % (h, m, s))
        if exist_time >= timeout_wait + tmp_timeout_wait:
            log.info('have wait %s s' % timeout_wait)
            break
    return ret_lst


def install_client(volume_state):
    local_pkg = PKG_PATH
    install_clinet_cmd = '%s/client/install.py --ips=%s' % (local_pkg, ip_lst[0])
    for ip in client_lst:
        rc, stdout = run_command(install_clinet_cmd, ip)
        if rc != 0:
            log.info("bug:install client failed ip :%s" % ip)
    log.info("wait 60s")
    #   time.sleep(60)
    client_flag = False
    for clientip in client_lst:
        print volume_state
        if volume_state[clientip] != []:
            ret_lst = wait_client_find_volume(clientip, volume_state[clientip], 300, 1800)
            for ret in ret_lst:
                if ret_lst[ret] != 0:
                    log.info("ip : %s  cannot find volume:%s" % (clientip, ret))
                    client_flag = True
    if client_flag:
        raise Exception('some client cannot find all volume')


def uninstall_client():
    cmd = UNINSTALL_CLIENT_CMD
    for clientip in client_lst:
        rc, stdout = run_command(cmd, clientip)
        if rc != 0:
            raise Exception('failed')


def get_old_volume_state_client():
    volume_state = {}
    for ip in client_lst:
        volume_name_lst = get_volume_name_on_client(ip)
        volume_state[ip] = volume_name_lst
    return volume_state


def offline_upgrade(pkg_info):
    """准备参数"""
    package_ip = pkg_info['cluster_pkg_ip']
    package_path = pkg_info['cluster_pkg_dir']
    package_name = pkg_info['sys_pkg_name']
    print package_name
    print type(package_name)
    version = int(package_name[-10])
    min_version = int(package_name[-8])
    system_version = get_system_version(ip_lst[0])
    middle = pkg_info['sys_pkg_name'].split('-')[-3]
    upgrade_package_time = middle.split('_')[-2] + '_' + middle.split('_')[-1]
    system_package_time = get_system_package_time(ip_lst[0])
    if upgrade_package_time < system_package_time:
        log.info("#########版本过低，请检查升级包版本##########")
        return -2
    elif upgrade_package_time == system_package_time:
        log.info("##########修改系统包日期，即将升级##########")
        set_system_package_time(ip_lst[0])
    elif upgrade_package_time > system_package_time:
        if system_version < min_version:
            log.info("system version:%d is lowwer than the package's min compatible version of package: %d"
                         % (system_version, min_version))
            return -2
        elif system_version >= min_version and system_version > version:
            log.info("this package's capatible version is %s, but you system version is %s" % (version, system_version))
            return -2
        elif system_version >= min_version and system_version <= version:
            log.info("###############系统即将升级###############")

    log.info("################分发安装包#################")
    package_ip = ip_lst[0]  # 升级包所在ip
    distribute_package(package_ip, package_path)

    """离线升级系统"""
    process_upgrade_offline = Process(target=ext_offline_upgrade, args=(package_ip, package_name,
                                                                        upgrade_package_time))
    process_upgrade_offline.start()

    """检查升级状态"""
    time.sleep(120)
    log.info("################检查升级状态###############")
    upgrade_time = 10
    time_begin = time.time()
    while process_upgrade_offline.is_alive():
        upgrade_info = get_upgrade_info(ip_lst[0])
        if upgrade_info != {}:
            if upgrade_info['result']['upgrade_stage'] == 'UPGRADE_STAGE_UPGRADING':
                log.info("################系统正在离线升级中###############")
                log.info("################升级用时：%ds###############" % upgrade_time)
            elif upgrade_info['result']['upgrade_stage'] == 'UPGRADE_STATE_PREPARE':
                break
        time.sleep(60)
        upgrade_time = time.time() - time_begin

    process_upgrade_offline.join()
    if process_upgrade_offline.exitcode != 0:
        raise Exception('online_upgrade failed')
    log.info("################升级结束################")


def run_test(cmd_info):
    process_lst = []
    for cmd in cmd_info:
        process = Process(target=command, args=(cmd,))
        process_lst.append(process)
    for process in process_lst:
        process.start()
    for process in process_lst:
        process.join()


def shutdown_retry():
    rc = shutdown()
    if rc != 0:
        log.info('关闭系统失败')
        raise Exception('failed')


def case():
    if WAIT_COPY is True:
        log.info('wait copy pkg finish')
        time.sleep(200)
    check_ssh(ip_lst)
    check_ssh(client_lst)
    log.info('run le')
    log.info("1>先查看是否有新的安装包")
    pkg_info = wait_new_pkg()

    log.info('2> 收集当前环境信息')
    save_state()

    log.info('3> 卸载客户端')
    volume_state = get_old_volume_state_client()
    if client_lst:
        uninstall_client()

    log.info("4>复制两个压缩包到各个节点")
    cp_pkg(pkg_info)

    log.info('5> 关闭系统')
    shutdown_retry()

    log.info('6> 开始离线升级')
    offline_upgrade(pkg_info)

    log.info("7> 启动系统")
    startup()

    log.info('wait 60s')
    time.sleep(60)

    log.info("8> 开始安装客户端")
    if client_lst:
        install_client(volume_state)


def main():
    log_file_path = log.get_log_path(FILE_NAME)
    log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)
    return


if __name__ == '__main__':
    common.case_main(main)
