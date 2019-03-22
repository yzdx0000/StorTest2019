#!/usr/bin/python
# -*-coding:utf-8 -*


import os
import random
import ConfigParser
import commands
import xml.dom.minidom

# /home/StorTest/Test_cases/Libs
current_path = os.path.dirname(os.path.abspath(__file__))
# /home/StorTest/Test_cases
test_case_path = os.path.dirname(current_path)
# /home/StorTest
stortest_path = os.path.dirname(test_case_path)
# /home/StorTest/conf
config_path = os.path.join(stortest_path, 'conf')
# /home/StorTest/conf/p300_test_config.xml

if 'config_file' in os.environ.keys():
    config_file_name = os.environ['config_file']
    CONFIG_FILE = os.path.join(config_path, config_file_name)
else:
    CONFIG_FILE = os.path.join(config_path, 'unistor_test_config.xml')

if 'nas_config_file' in os.environ.keys():
    config_file_name = os.environ['nas_config_file']
    NAS_CONFIG_FILE = os.path.join(config_path, config_file_name)
else:
    NAS_CONFIG_FILE = os.path.join(config_path, 'p300_nas_config.xml')

if 's3_config_file' in os.environ.keys():
    config_file_name = os.environ['s3_config_file']
    S3_CONFIG_FILE = os.path.join(config_path, config_file_name)
else:
    S3_CONFIG_FILE = os.path.join(config_path, 'p300_s3_config.xml')


##############################################################################
# ##name  :      get_processd_single_line
# ##parameter:   line:文件的单行内容
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 将单行内容去除掉#注释掉的内容和空格之后的内容
##############################################################################
def get_processd_single_line(line):
    # 先去除两头的空格
    line = line.replace('\r', '').replace('\n', '').replace('\t', '')
    line = line.strip()
    # 如果是空行直接返回
    if 0 == len(line):
        return line
    # 去除#注释掉的内容
    new_line = line.split('#')
    # 如果第一个成员为空则直接返回
    if 0 == len(new_line[0]):
        return new_line[0]
    # 去除空格之后的内容
    new_line1 = new_line[0].split()
    return new_line1[0]


##############################################################################
# ##name  :      get_case_list
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 从用例配置文件中获取用例列表
##############################################################################
def get_case_list(case_list_file):
    notes_flag = False
    case_list = []

    # 检查文件是否存在
    cmd = 'ls %s' % case_list_file
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        print '%s is not exist!!!' % case_list_file
        return

    case_list_path = os.path.dirname(case_list_file)

    with open(case_list_file, 'r') as f:
        for (num, line) in enumerate(f, 1):
            if line == '\r\n':
                continue
            # 先出去#注释的内容和空格后的内容
            new_line = get_processd_single_line(line)
            # 如果是空行直接跳过
            if 0 == len(new_line):
                continue
            # 先检查是否处于多行测试中
            if notes_flag is True:
                # 如果前两个字符是*/，将多行标志改成False
                if new_line.startswith('*/', 0) is True:
                    notes_flag = False
                    continue
                # 如果前两个字符不是*/，则直接跳过
                else:
                    continue
            # 如果没有在多行注释中
            else:
                # 检查前两个字符是否/*
                if new_line.startswith('/*', 0) is True:
                    notes_flag = True
                    continue
                else:
                    if new_line.split('_')[-1] == 'list':
                        case_file = os.path.join(case_list_path, new_line)
                        case_list1 = get_case_list(case_file)
                        case_list.extend(case_list1)
                    else:
                        meb = [os.path.basename(case_list_file), num, new_line]
                        case_list.append(meb)
    return case_list


##############################################################################
# ##name  :      get_caselist_file
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.04.11
# ##Description: 获取用例列表的完整路径
##############################################################################
def get_caselist_file():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    case_list_file = config_info.getElementsByTagName('caselist')[0].firstChild.nodeValue
    return case_list_file


##############################################################################
# ##name  :      get_env_ip_info
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.04.12
# ##Description: 获取Jenkins节点IP
##############################################################################
def get_jenkins_ip(config_path):
    config_info = xml.dom.minidom.parse(config_path)
    nodes_info = config_info.getElementsByTagName('jenkins')[0]
    ip_info = nodes_info.getElementsByTagName('ip')[0].firstChild.nodeValue
    return ip_info


##############################################################################
# ##name  :      get_env_ip_info
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.04.12
# ##Description: 获取Jenkins共享路径
##############################################################################
def get_jenkins_path(config_path):
    config_info = xml.dom.minidom.parse(config_path)
    nodes_info = config_info.getElementsByTagName('jenkins')[0]
    path_info = nodes_info.getElementsByTagName('path')[0].firstChild.nodeValue
    return path_info


##############################################################################
# ##name  :      get_env_ip_info
# ##parameter:   config_path:配置文件的存放路径
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取集群节点的ip数组
##############################################################################
def get_env_ip_info(config_path):
    config_info = xml.dom.minidom.parse(config_path)
    nodes_info = config_info.getElementsByTagName('nodes')[0]
    nodes_info = nodes_info.getElementsByTagName('node')
    ip_list = []
    for node in nodes_info:
        ip = node.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    return ip_list


##############################################################################
# ##name  :      get_allparastor_ips
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取所有集群ip
##############################################################################
def get_allparastor_ips():
    node_list = get_env_ip_info(CONFIG_FILE)
    return node_list


##############################################################################
# ##name  :      get_parastor_ip
# ##parameter:   num:第几个节点
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取具体集群节点ip
##############################################################################
def get_parastor_ip(num=0):
    ip_list = get_allparastor_ips()
    if num >= len(ip_list):
        num = len(ip_list) - 1
    return ip_list[num]


##############################################################################
# ##name  :      get_allclient_ip
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取所有客户端ip
##############################################################################
def get_allclient_ip():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    client_info = config_info.getElementsByTagName('clients')[0]
    client_infos = client_info.getElementsByTagName('client')
    ip_list = []
    for client in client_infos:
        ip = client.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    ip_list2 = list(set(ip_list))
    ip_list2.sort(key=ip_list.index)
    return ip_list

def get_windows_host_ip():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    client_info = config_info.getElementsByTagName('windows_hosts')[0]
    client_infos = client_info.getElementsByTagName('windows_host')
    ip = client_infos[0].getElementsByTagName('ip')[0].firstChild.nodeValue
    return ip

def get_windows_host_port():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    client_info = config_info.getElementsByTagName('windows_hosts')[0]
    client_infos = client_info.getElementsByTagName('windows_host')
    port = client_infos[0].getElementsByTagName('port')[0].firstChild.nodeValue
    return port

def get_windows_host_conf():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    client_info = config_info.getElementsByTagName('windows_hosts')[0]
    client_infos = client_info.getElementsByTagName('windows_host')
    conf = client_infos[0].getElementsByTagName('switch')[0].firstChild.nodeValue
    return conf

##############################################################################
# ##name  :      get_client_ip
# ##parameter:   num:第几个客户端
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取具体客户端节点ip
##############################################################################
def get_client_ip(num=0):
    ip_list = get_allclient_ip()
    if num >= len(ip_list):
        num = len(ip_list) - 1
    return ip_list[num]


##############################################################################
# ##name  :      get_mount_path
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取所有挂载路径
##############################################################################
def get_mount_paths():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    mnt_paths = config_info.getElementsByTagName('mount_paths')[0]
    mnt_paths = mnt_paths.getElementsByTagName('mount_path')
    mnt_path_list = []
    for mem in mnt_paths:
        mnt_path = mem.firstChild.nodeValue
        mnt_path_list.append(mnt_path)
    return mnt_path_list


##############################################################################
# ##name  :      get_one_mount_path
# ##parameter:   num=0:第几条路径，默认是第一条
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取一条挂载路径，默认是第一条
##############################################################################
def get_one_mount_path(num=0):
    mnt_path_list = get_mount_paths()
    if num >= len(mnt_path_list):
        num = len(mnt_path_list) - 1
    return mnt_path_list[num]


##############################################################################
# ##name  :      get_volume_names
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取所有快照卷的名字
##############################################################################
def get_volume_names():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    volumes = config_info.getElementsByTagName('volumes')[0]
    volumes = volumes.getElementsByTagName('volume')
    volume_list = []
    for mem in volumes:
        volume = mem.firstChild.nodeValue
        volume_list.append(volume)
    return volume_list


##############################################################################
# ##name  :      get_one_volume_name
# ##parameter:   num=0:第几个卷，默认是第一条
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取一个快照卷，默认是第一条
##############################################################################
def get_one_volume_name(num=0):
    volume_list = get_volume_names()
    if num >= len(volume_list):
        num = len(volume_list) - 1
    return volume_list[num]


##############################################################################
# ##name  :      get_one_snap_test_path
# ##parameter:   num=0:第几个快照测试路径，默认是第一条
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取一个快照测试路径，默认是第一条
##############################################################################
def get_one_snap_test_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    snap_test_path = config_info.getElementsByTagName('snap_test_path')[0].firstChild.nodeValue
    return snap_test_path


def get_event_test_base_path():
    '''
    author: liyao
    date: 2018-8-11
    description：获取告警/事件数据存放的基础路径
    :return:
    '''
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    event_test_base_path = config_info.getElementsByTagName('mount_path')[0].firstChild.nodeValue
    return event_test_base_path


##############################################################################
# ##name  :      get_one_quota_test_path
# ##parameter:   num=0:第几个配额测试路径，默认是第一条
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取一个配额测试路径，默认是第一条
##############################################################################
def get_one_quota_test_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    quota_test_path = config_info.getElementsByTagName('quota_test_path')[0].firstChild.nodeValue
    return quota_test_path


def get_one_defect_test_path():
    """
    author:         baoruobing
    date  :         2018.04.17
    Description:    从配置文件中获取缺陷脚本运行的目录
    :return:        缺陷脚本运行的目录
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    defect_test_path = config_info.getElementsByTagName('defect_test_path')[0].firstChild.nodeValue
    return defect_test_path


def get_s3_access_ips():
    """
    author:         baoruobing
    date  :         2018.04.17
    Description:    从配置文件中获取S3的访问分区对外ip
    :return:
    """
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    s3_access_ips = config_info.getElementsByTagName('S3_access_ips')[0]
    s3_access_ips = s3_access_ips.getElementsByTagName('S3_access_ip')
    s3_access_ips_list = []
    for mem in s3_access_ips:
        volume = mem.firstChild.nodeValue
        s3_access_ips_list.append(volume)
    return s3_access_ips_list



##############################################################################
# ##name  :      get_testlog_path
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.04.11
# ##Description: 获取用例日志存放路径
##############################################################################
def get_testlog_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    test_log_path = config_info.getElementsByTagName('test_log_path')[0].firstChild.nodeValue
    return test_log_path


##############################################################################
# ##name  :      get_testresult_path
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.04.11
# ##Description: 获取用例执行结果存放路径
##############################################################################
def get_testresult_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    test_result_path = config_info.getElementsByTagName('test_result_path')[0].firstChild.nodeValue
    return test_result_path


##############################################################################
# ##name  :      get_tools_path
# ##parameter:
# ##author:      baoruobing
# ##date  :      2018.04.11
# ##Description: 获取工具放置的路径
##############################################################################
def get_tools_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    tools_path = config_info.getElementsByTagName('tools_path')[0].firstChild.nodeValue
    return tools_path


##############################################################################
# ##name  :      get_vdbench_path
# ##parameter:
# ##author:      baoruobing
# ##date  :      2017.07.12
# ##Description: 获取客户端vdbench路径
##############################################################################
def get_vdbench_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    vdbench_path = config_info.getElementsByTagName('vdbench_path')[0].firstChild.nodeValue
    return vdbench_path


def get_snap_vdbench_path():
    '''
    get_config-NULL-get_snap_vdbench_path
    作用:从配置文件获取快照vdbench工具的路径
    作者:baoruobing
    修改时间:2018.04.23
    参数含义:
    返回值:快照vdbench工具路径
    '''
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    snap_vdbench_path = config_info.getElementsByTagName('snap_vdbench_path')[0].firstChild.nodeValue
    return snap_vdbench_path


##############################################################################
# ##name  :      get_upgrade_package_ip
# ##parameter:
# ##author:      liujx
# ##date  :      2017.07.26
# ##Description: 获取升级包所在的节点ip
##############################################################################


def get_upgrade_package_ip():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    upgrade_package = config_info.getElementsByTagName('package_position')[0].firstChild.nodeValue
    package_ip = upgrade_package.split(':')[0]
    return package_ip


##############################################################################
# ##name  :      get_upgrade_package_path
# ##parameter:
# ##author:      liujx
# ##date  :      2017.07.26
# ##Description: 获取升级包所在的路径
##############################################################################


def get_upgrade_package_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    upgrade_package = config_info.getElementsByTagName('package_position')[0].firstChild.nodeValue
    package_path = upgrade_package.split(':')[1]
    return package_path


##############################################################################
# ##name  :      get_upgrade_package_time
# ##parameter:
# ##author:      liujx
# ##date  :      2017.07.27
# ##Description: 获取升级包的package_time, e.g. 20180801_174109
##############################################################################


def get_upgrade_package_time():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    upgrade_package = config_info.getElementsByTagName('package_position')[0].firstChild.nodeValue
    middle = upgrade_package.split('-')[-3]
    package_time = middle.split('_')[-2] + '_' + middle.split('_')[-1]
    return package_time


##############################################################################
# ##name  :      get_svip
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.06.22
# ##Description: 获取svip
##############################################################################
def get_svip(config_file):
    config_info = xml.dom.minidom.parse(config_file)
    svips_info = config_info.getElementsByTagName('svips')[0]
    svips_infos = svips_info.getElementsByTagName('svip')
    svips_list = []
    for svip in svips_infos:
        ip = svip.getElementsByTagName('ip')[0].firstChild.nodeValue
        svips_list.append(ip)
    return svips_list


##############################################################################
# ##name  :      get_vip
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.06.22
# ##Description: 获取vip
##############################################################################
def get_vip(config_file):
    config_info = xml.dom.minidom.parse(config_file)
    vips_info = config_info.getElementsByTagName('vips')[0]
    vips_infos = vips_info.getElementsByTagName('vip')
    vips_list = []
    for vip in vips_infos:
        ip = vip.getElementsByTagName('ip')[0].firstChild.nodeValue
        vips_list.append(ip)
    return vips_list


##############################################################################
# ##name  :      get_esxi
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.07.05
# ##Description: 获取esxi主机信息
##############################################################################
def get_esxi(config_file):
    config_info = xml.dom.minidom.parse(config_file)
    esxi_info = config_info.getElementsByTagName('esxis')[0]
    esxi_infos = esxi_info.getElementsByTagName('esxi')
    ips_list = []
    for ips in esxi_infos:
        ip = ips.getElementsByTagName('ip')[0].firstChild.nodeValue
        ips_list.append(ip)
    uns_list = []
    for uns in esxi_infos:
        un = uns.getElementsByTagName('name')[0].firstChild.nodeValue
        uns_list.append(un)
    pws_list = []
    for pws in esxi_infos:
        pw = pws.getElementsByTagName('pwd')[0].firstChild.nodeValue
        pws_list.append(pw)
    return (ips_list, uns_list, pws_list)


##############################################################################
# ##name  :      get_machine_type
# ##parameter:   config_path:配置文件的存放路径
# ##author:      DiWeisong
# ##date  :      2018.07.04
# ##Description: 获取测试机类型
##############################################################################
def get_machine_type(config_file):
    config_info = xml.dom.minidom.parse(config_file)
    type_info = config_info.getElementsByTagName('machinetype')[0].firstChild.nodeValue
    return type_info


def get_stripwidth():
    """
    :author:   baoruobing
    :function: 获取条带宽度
    :date:     2018-12-11
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    stripwidth = config_info.getElementsByTagName('stripwidth')[0].firstChild.nodeValue
    return stripwidth


def get_disk_parity_num():
    """
    :author:   baoruobing
    :function: 获取磁盘冗余
    :date:     2018-12-11
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    disk_parity_num = config_info.getElementsByTagName('disk_parity_num')[0].firstChild.nodeValue
    return disk_parity_num


def get_node_parity_num():
    """
    :author:   baoruobing
    :function: 获取节点冗余
    :date:     2018-12-11
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    node_parity_num = config_info.getElementsByTagName('node_parity_num')[0].firstChild.nodeValue
    return node_parity_num


def get_replica():
    """
    :author:   baoruobing
    :function: 获取副本数
    :date:     2018-12-11
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    replica = config_info.getElementsByTagName('replica')[0].firstChild.nodeValue
    return replica


def config_parser(*args, **kwargs):
    """

    :param args: args[0]为x1000.conf的section, arg[1]为x1000.conf的option
    :param kwargs:
    :return: config.get(section=args[0],option=args[1])
    """
    # /home/StorTest/Test_cases/Libs
    current_path = os.path.dirname(os.path.abspath(__file__))
    # /home/StorTest/Test_cases
    test_case_path = os.path.dirname(current_path)
    # /home/StorTest
    stortest_path = os.path.dirname(test_case_path)
    # /home/StorTest/conf
    config_path = os.path.join(stortest_path, 'test_cases/cases/test_case/X1000/lun_manager')
    config_file = config_path + r"/x1000.conf"
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    # config.get(section=args[0],option=args[1])
    return config.get(section=args[0], option=args[1])


##############################################################################
# ##name  :      get_client_install_path
# ##parameter:
# ##author:      chenjy
# ##date  :      2018.08.07
# ##Description: 获取客户端中每个节点的install.py和uninstall.py所在位置
##############################################################################
def get_client_install_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    client_install_path = config_info.getElementsByTagName('client_install_path')[0].firstChild.nodeValue
    return client_install_path


##############################################################################
# ##name  :      get_nas_test_paths
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.04.23
# ##Description: 获取所有nas测试路径的名字
##############################################################################
def get_nas_test_paths():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    nas_test_paths = config_info.getElementsByTagName('nas_test_paths')[0]
    nas_test_paths = nas_test_paths.getElementsByTagName('nas_test_path')
    nas_test_path_list = []
    for mem in nas_test_paths:
        nas_test_path = mem.firstChild.nodeValue
        nas_test_path_list.append(nas_test_path)
    return nas_test_path_list


##############################################################################
# ##name  :      get_one_nas_test_path
# ##parameter:   num=0:第几个nas测试路径，默认是第一条
# ##author:      jiangxiaoguang
# ##date  :      2018.04.23
# ##Description: 获取一个nas测试路径，默认是第一条
##############################################################################
def get_one_nas_test_path(num=0):
    nas_test_path_list = get_nas_test_paths()
    if num >= len(nas_test_path_list):
        num = len(nas_test_path_list) - 1
    return nas_test_path_list[num]


##############################################################################
# ##name  :      get_ip_family
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网ip类型
##############################################################################
def get_ip_family():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('subnet_info')[0]
    ip_families = vip_address_pool_info.getElementsByTagName('ip_families')
    ip_family_list = []
    for families in ip_families:
        for family in families.getElementsByTagName('ip_family'):
            ip_family = family.firstChild.nodeValue
            ip_family_list.append(ip_family)
    return ip_family_list


##############################################################################
# ##name  :      get_subnet_svip
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网svip
##############################################################################
def get_subnet_svip():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    subnet_info = config_info.getElementsByTagName('subnet_info')[0]
    svips = subnet_info.getElementsByTagName('svips')
    svip_list = []
    for mem in svips:
        svip = mem.getElementsByTagName('svip')[0].firstChild.nodeValue
        svip_list.append(svip)
    return svip_list


##############################################################################
# ##name  :      get_subnet_mask
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网掩码
##############################################################################
def get_subnet_mask():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    subnet_info = config_info.getElementsByTagName('subnet_info')[0]
    subnet_masks = subnet_info.getElementsByTagName('subnet_masks')
    subnet_mask_list = []
    for mem in subnet_masks:
        subnet_mask = mem.getElementsByTagName('subnet_mask')[0].firstChild.nodeValue
        subnet_mask_list.append(subnet_mask)
    return subnet_mask_list


##############################################################################
# ##name  :      get_subnet_gateway
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网网关
##############################################################################
def get_subnet_gateway():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    subnet_info = config_info.getElementsByTagName('subnet_info')[0]
    subnet_gateways = subnet_info.getElementsByTagName('subnet_gateways')
    subnet_gateway_list = []
    for mem in subnet_gateways:
        subnet_gateway = mem.getElementsByTagName('subnet_gateway')[0].firstChild.nodeValue
        subnet_gateway_list.append(subnet_gateway)
    return subnet_gateway_list


##############################################################################
# ##name  :      get_subnet_network_interface
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网网卡
##############################################################################
def get_subnet_network_interface():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    subnet_info = config_info.getElementsByTagName('subnet_info')[0]
    network_interfaces = subnet_info.getElementsByTagName('network_interfaces')
    subnet_network_interface_list = []
    for mem in network_interfaces:
        network_interface = mem.getElementsByTagName('network_interface')[0].firstChild.nodeValue
        subnet_network_interface_list.append(network_interface)
    return subnet_network_interface_list


##############################################################################
# ##name  :      get_subnet_mtu
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取子网mtu
##############################################################################
def get_subnet_mtu():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    subnet_info = config_info.getElementsByTagName('subnet_info')[0]
    mtus = subnet_info.getElementsByTagName('mtus')
    subnet_mtu_list = []
    for mem in mtus:
        mtu = mem.getElementsByTagName('mtu')[0].firstChild.nodeValue
        subnet_mtu_list.append(mtu)
    return subnet_mtu_list


##############################################################################
# ##name  :      get_vip_domain_name
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池域名参数
##############################################################################
def get_vip_domain_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    domain_names = vip_address_pool_info.getElementsByTagName('domain_names')
    vip_domain_name_list = []
    for domain_name in domain_names:
        domain_name = domain_name.getElementsByTagName('domain_name')[0].firstChild.nodeValue
        vip_domain_name_list.append(domain_name)
    return vip_domain_name_list


##############################################################################
# ##name  :      get_vip_addresses
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池ip参数
##############################################################################
def get_vip_addresses():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    vip_addresses = vip_address_pool_info.getElementsByTagName('vip_addresses')
    vip_addresses_list = []
    for domain_name in vip_addresses:
        vip_addresse = domain_name.getElementsByTagName('vip_addresse')[0].firstChild.nodeValue
        vip_addresses_list.append(vip_addresse)
    return vip_addresses_list


##############################################################################
# ##name  :      get_vip_supported_protocol
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池支持的协议
##############################################################################
def get_vip_supported_protocol():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    supported_protocols = vip_address_pool_info.getElementsByTagName('supported_protocols')
    supported_protocol_list = []
    for protocols in supported_protocols:
        for protocol in protocols.getElementsByTagName('supported_protocol'):
            supported_protocol = protocol.firstChild.nodeValue
            supported_protocol_list.append(supported_protocol)
    return supported_protocol_list


##############################################################################
# ##name  :      get_vip_allocation_methods
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池支持的地址分配方法
##############################################################################
def get_vip_allocation_methods():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    allocation_methods = vip_address_pool_info.getElementsByTagName('allocation_methods')
    allocation_method_list = []
    for methods in allocation_methods:
        for method in methods.getElementsByTagName('allocation_method'):
            allocation_method = method.firstChild.nodeValue
            allocation_method_list.append(allocation_method)
    return allocation_method_list


##############################################################################
# ##name  :      get_vip_load_balance_policy
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池负载均衡策略
##############################################################################
def get_vip_load_balance_policy():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    load_balance_policies = vip_address_pool_info.getElementsByTagName('load_balance_policies')
    load_balance_policy_list = []
    for policies in load_balance_policies:
        for policy in policies.getElementsByTagName('load_balance_policy'):
            load_balance_policy = policy.firstChild.nodeValue
            load_balance_policy_list.append(load_balance_policy)
    return load_balance_policy_list


##############################################################################
# ##name  :      get_ip_failover_policy
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池故障ip转移策略
##############################################################################
def get_ip_failover_policy():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    ip_failover_policies = vip_address_pool_info.getElementsByTagName('ip_failover_policies')
    ip_failover_policy_list = []
    for policies in ip_failover_policies:
        for policy in policies.getElementsByTagName('ip_failover_policy'):
            ip_failover_policy = policy.firstChild.nodeValue
            ip_failover_policy_list.append(ip_failover_policy)
    return ip_failover_policy_list


##############################################################################
# ##name  :      get_ip_failover_policy
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.15
# ##Description: 获取vip地址池rebalance_policy
##############################################################################
def get_rebalance_policy():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    vip_address_pool_info = config_info.getElementsByTagName('vip_address_pool_info')[0]
    rebalance_policies = vip_address_pool_info.getElementsByTagName('rebalance_policies')
    rebalance_policy_list = []
    for policies in rebalance_policies:
        for policy in policies.getElementsByTagName('rebalance_policy'):
            rebalance_policy = policy.firstChild.nodeValue
            rebalance_policy_list.append(rebalance_policy)
    return rebalance_policy_list


##############################################################################
# ##name  :      get_nfs_client_ip
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取NFS客户端的ip地址
##############################################################################
def get_nfs_client_ip():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nfs_client_info = config_info.getElementsByTagName('nfs_client_info')[0]
    nfs_client_ip = nfs_client_info.getElementsByTagName('nfs_client_ip')
    nfs_client_ip_list = []
    for policies in nfs_client_ip:
        for policy in policies.getElementsByTagName('nfs_client_ip'):
            nfs_client_ip_i = policy.firstChild.nodeValue
            nfs_client_ip_list.append(nfs_client_ip_i)
    return nfs_client_ip_list


##############################################################################
# ##name  :      get_nfs_mount_path
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.11.09
# ##Description: 获取NFS客户端的挂载目录
##############################################################################
def get_nfs_mount_path():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nfs_client_info = config_info.getElementsByTagName('nfs_client_info')[0]
    nfs_mount_path = nfs_client_info.getElementsByTagName('nfs_mount_path')
    nfs_mount_path_list = []
    for policies in nfs_mount_path:
        for policy in policies.getElementsByTagName('nfs_mount_path'):
            nfs_mount_path_i = policy.firstChild.nodeValue
            nfs_mount_path_list.append(nfs_mount_path_i)
    return nfs_mount_path_list


##############################################################################
# ##name  :      get_ftp_client_ip
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.24
# ##Description: 获取FTP客户端的ip地址
##############################################################################
def get_ftp_client_ip():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ftp_client_info = config_info.getElementsByTagName('ftp_client_info')[0]
    ftp_client_ip = ftp_client_info.getElementsByTagName('ftp_client_ip')
    ftp_client_ip_list = []
    for policies in ftp_client_ip:
        for policy in policies.getElementsByTagName('ftp_client_ip'):
            ftp_client_ip_i = policy.firstChild.nodeValue
            ftp_client_ip_list.append(ftp_client_ip_i)
    return ftp_client_ip_list


##############################################################################
# ##name  :      get_ldap_ip_addresses
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.15
# ##Description: 获取ldap server的ip地址
##############################################################################
def get_ldap_ip_addresses():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_ip_addresses = ldap_server_info.getElementsByTagName('ldap_ip_addresses')
    ldap_ip_addresses_list = []
    for policies in ldap_ip_addresses:
        for policy in policies.getElementsByTagName('ldap_ip_addresses'):
            ldap_ip_address = policy.firstChild.nodeValue
            ldap_ip_addresses_list.append(ldap_ip_address)
    return ldap_ip_addresses_list


##############################################################################
# ##name  :      get_ldap_base_dn
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的base_dn
##############################################################################
def get_ldap_base_dn():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_base_dn = ldap_server_info.getElementsByTagName('ldap_base_dn')
    ldap_base_dn_list = []
    for policies in ldap_base_dn:
        for policy in policies.getElementsByTagName('ldap_base_dn'):
            ldap_base_dn_i = policy.firstChild.nodeValue
            ldap_base_dn_list.append(ldap_base_dn_i)
    return ldap_base_dn_list


##############################################################################
# ##name  :      get_ldap_bind_dn
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的bind_dn
##############################################################################
def get_ldap_bind_dn():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_bind_dn = ldap_server_info.getElementsByTagName('ldap_bind_dn')
    ldap_bind_dn_list = []
    for policies in ldap_bind_dn:
        for policy in policies.getElementsByTagName('ldap_bind_dn'):
            ldap_bind_dn_i = policy.firstChild.nodeValue
            ldap_bind_dn_list.append(ldap_bind_dn_i)
    return ldap_bind_dn_list


##############################################################################
# ##name  :      get_ldap_bind_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的bind_passwd
##############################################################################
def get_ldap_bind_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_bind_passwd = ldap_server_info.getElementsByTagName('ldap_bind_passwd')
    ldap_bind_passwd_list = []
    for policies in ldap_bind_passwd:
        for policy in policies.getElementsByTagName('ldap_bind_passwd'):
            ldap_bind_passwd_i = policy.firstChild.nodeValue
            ldap_bind_passwd_list.append(ldap_bind_passwd_i)
    return ldap_bind_passwd_list


##############################################################################
# ##name  :      get_ldap_domain_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.09.12
# ##Description: 获取ldap server的domain_passwd
##############################################################################
def get_ldap_domain_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_domain_passwd = ldap_server_info.getElementsByTagName('ldap_domain_passwd')
    ldap_domain_passwd_list = []
    for policies in ldap_domain_passwd:
        for policy in policies.getElementsByTagName('ldap_domain_passwd'):
            ldap_domain_passwd_i = policy.firstChild.nodeValue
            ldap_domain_passwd_list.append(ldap_domain_passwd_i)
    return ldap_domain_passwd_list


##############################################################################
# ##name  :      get_ldap_user_search_path
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的用户搜索路径
##############################################################################
def get_ldap_user_search_path():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_user_search_path = ldap_server_info.getElementsByTagName('ldap_user_search_path')
    ldap_user_search_path_list = []
    for policies in ldap_user_search_path:
        for policy in policies.getElementsByTagName('ldap_user_search_path'):
            ldap_user_search_path_i = policy.firstChild.nodeValue
            ldap_user_search_path_list.append(ldap_user_search_path_i)
    return ldap_user_search_path_list


##############################################################################
# ##name  :      get_ldap_group_search_path
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的用户组搜索路径
##############################################################################
def get_ldap_group_search_path():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_group_search_path = ldap_server_info.getElementsByTagName('ldap_group_search_path')
    ldap_group_search_path_list = []
    for policies in ldap_group_search_path:
        for policy in policies.getElementsByTagName('ldap_group_search_path'):
            ldap_group_search_path_i = policy.firstChild.nodeValue
            ldap_group_search_path_list.append(ldap_group_search_path_i)
    return ldap_group_search_path_list


##############################################################################
# ##name  :      get_ldap_user_name
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的用户名字
##############################################################################
def get_ldap_user_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_user_name = ldap_server_info.getElementsByTagName('ldap_user_name')
    ldap_user_name_list = []
    for policies in ldap_user_name:
        for policy in policies.getElementsByTagName('ldap_user_name'):
            ldap_user_name_i = policy.firstChild.nodeValue
            ldap_user_name_list.append(ldap_user_name_i)
    return ldap_user_name_list


##############################################################################
# ##name  :      get_ldap_user_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的用户密码
##############################################################################
def get_ldap_user_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_user_passwd = ldap_server_info.getElementsByTagName('ldap_user_passwd')
    ldap_user_passwd_list = []
    for policies in ldap_user_passwd:
        for policy in policies.getElementsByTagName('ldap_user_passwd'):
            ldap_user_passwd_i = policy.firstChild.nodeValue
            ldap_user_passwd_list.append(ldap_user_passwd_i)
    return ldap_user_passwd_list


##############################################################################
# ##name  :      get_ldap_group_name
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.08.16
# ##Description: 获取ldap server的用户组名字
##############################################################################
def get_ldap_group_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldap_server_info = config_info.getElementsByTagName('ldap_server_info')[0]
    ldap_group_name = ldap_server_info.getElementsByTagName('ldap_group_name')
    ldap_group_name_list = []
    for policies in ldap_group_name:
        for policy in policies.getElementsByTagName('ldap_group_name'):
            ldap_group_name_i = policy.firstChild.nodeValue
            ldap_group_name_list.append(ldap_group_name_i)
    return ldap_group_name_list


##############################################################################
# ##name  :      get_ldappdc_ip_addresses
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的ip地址
##############################################################################
def get_ldappdc_ip_addresses():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_ip_addresses = ldappdc_server_info.getElementsByTagName('ldappdc_ip_addresses')
    ldappdc_ip_addresses_list = []
    for policies in ldappdc_ip_addresses:
        for policy in policies.getElementsByTagName('ldappdc_ip_addresses'):
            ldappdc_ip_address = policy.firstChild.nodeValue
            ldappdc_ip_addresses_list.append(ldappdc_ip_address)
    return ldappdc_ip_addresses_list


##############################################################################
# ##name  :      get_ldappdc_base_dn
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的base_dn
##############################################################################
def get_ldappdc_base_dn():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_base_dn = ldappdc_server_info.getElementsByTagName('ldappdc_base_dn')
    ldappdc_base_dn_list = []
    for policies in ldappdc_base_dn:
        for policy in policies.getElementsByTagName('ldappdc_base_dn'):
            ldappdc_base_dn_i = policy.firstChild.nodeValue
            ldappdc_base_dn_list.append(ldappdc_base_dn_i)
    return ldappdc_base_dn_list


##############################################################################
# ##name  :      get_ldappdc_bind_dn
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的bind_dn
##############################################################################
def get_ldappdc_bind_dn():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_bind_dn = ldappdc_server_info.getElementsByTagName('ldappdc_bind_dn')
    ldappdc_bind_dn_list = []
    for policies in ldappdc_bind_dn:
        for policy in policies.getElementsByTagName('ldappdc_bind_dn'):
            ldappdc_bind_dn_i = policy.firstChild.nodeValue
            ldappdc_bind_dn_list.append(ldappdc_bind_dn_i)
    return ldappdc_bind_dn_list


##############################################################################
# ##name  :      get_ldappdc_bind_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的bind_passwd
##############################################################################
def get_ldappdc_bind_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_bind_passwd = ldappdc_server_info.getElementsByTagName('ldappdc_bind_passwd')
    ldappdc_bind_passwd_list = []
    for policies in ldappdc_bind_passwd:
        for policy in policies.getElementsByTagName('ldappdc_bind_passwd'):
            ldappdc_bind_passwd_i = policy.firstChild.nodeValue
            ldappdc_bind_passwd_list.append(ldappdc_bind_passwd_i)
    return ldappdc_bind_passwd_list


##############################################################################
# ##name  :      get_ldappdc_domain_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.09.12
# ##Description: 获取ldappdc server的domain_passwd
##############################################################################
def get_ldappdc_domain_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_domain_passwd = ldappdc_server_info.getElementsByTagName('ldappdc_domain_passwd')
    ldappdc_domain_passwd_list = []
    for policies in ldappdc_domain_passwd:
        for policy in policies.getElementsByTagName('ldappdc_domain_passwd'):
            ldappdc_domain_passwd_i = policy.firstChild.nodeValue
            ldappdc_domain_passwd_list.append(ldappdc_domain_passwd_i)
    return ldappdc_domain_passwd_list


##############################################################################
# ##name  :      get_ldappdc_user_search_path
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的用户搜索路径
##############################################################################
def get_ldappdc_user_search_path():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_user_search_path = ldappdc_server_info.getElementsByTagName('ldappdc_user_search_path')
    ldappdc_user_search_path_list = []
    for policies in ldappdc_user_search_path:
        for policy in policies.getElementsByTagName('ldappdc_user_search_path'):
            ldappdc_user_search_path_i = policy.firstChild.nodeValue
            ldappdc_user_search_path_list.append(ldappdc_user_search_path_i)
    return ldappdc_user_search_path_list


##############################################################################
# ##name  :      get_ldappdc_group_search_path
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的用户组搜索路径
##############################################################################
def get_ldappdc_group_search_path():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_group_search_path = ldappdc_server_info.getElementsByTagName('ldappdc_group_search_path')
    ldappdc_group_search_path_list = []
    for policies in ldappdc_group_search_path:
        for policy in policies.getElementsByTagName('ldappdc_group_search_path'):
            ldappdc_group_search_path_i = policy.firstChild.nodeValue
            ldappdc_group_search_path_list.append(ldappdc_group_search_path_i)
    return ldappdc_group_search_path_list


##############################################################################
# ##name  :      get_ldappdc_user_name
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的用户名字
##############################################################################
def get_ldappdc_user_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_user_name = ldappdc_server_info.getElementsByTagName('ldappdc_user_name')
    ldappdc_user_name_list = []
    for policies in ldappdc_user_name:
        for policy in policies.getElementsByTagName('ldappdc_user_name'):
            ldappdc_user_name_i = policy.firstChild.nodeValue
            ldappdc_user_name_list.append(ldappdc_user_name_i)
    return ldappdc_user_name_list


##############################################################################
# ##name  :      get_ldappdc_user_passwd
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的用户密码
##############################################################################
def get_ldappdc_user_passwd():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_user_passwd = ldappdc_server_info.getElementsByTagName('ldappdc_user_passwd')
    ldappdc_user_passwd_list = []
    for policies in ldappdc_user_passwd:
        for policy in policies.getElementsByTagName('ldappdc_user_passwd'):
            ldappdc_user_passwd_i = policy.firstChild.nodeValue
            ldappdc_user_passwd_list.append(ldappdc_user_passwd_i)
    return ldappdc_user_passwd_list


##############################################################################
# ##name  :      get_ldappdc_group_name
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2019.03.20
# ##Description: 获取ldappdc server的用户组名字
##############################################################################
def get_ldappdc_group_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ldappdc_server_info = config_info.getElementsByTagName('ldappdc_server_info')[0]
    ldappdc_group_name = ldappdc_server_info.getElementsByTagName('ldappdc_group_name')
    ldappdc_group_name_list = []
    for policies in ldappdc_group_name:
        for policy in policies.getElementsByTagName('ldappdc_group_name'):
            ldappdc_group_name_i = policy.firstChild.nodeValue
            ldappdc_group_name_list.append(ldappdc_group_name_i)
    return ldappdc_group_name_list


##############################################################################
# ##name  :      get_ad_domain_name
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的域名
##############################################################################
def get_ad_domain_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_domain_names = ad_server_info.getElementsByTagName('ad_domain_names')
    ad_domain_name_list = []
    for ad_domain_name in ad_domain_names:
        ad_domain_name = ad_domain_name.getElementsByTagName('ad_domain_name')[0].firstChild.nodeValue
        ad_domain_name_list.append(ad_domain_name)
    return ad_domain_name_list


##############################################################################
# ##name  :      get_ad_dns_address
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的dns地址
##############################################################################
def get_ad_dns_address():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_dns_addresses = ad_server_info.getElementsByTagName('ad_dns_addresses')
    ad_dns_address_list = []
    for ad_dns_address in ad_dns_addresses:
        ad_dns_address = ad_dns_address.getElementsByTagName('ad_dns_address')[0].firstChild.nodeValue
        ad_dns_address_list.append(ad_dns_address)
    return ad_dns_address_list


##############################################################################
# ##name  :      get_ad_user_name
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的管理员用户名称
##############################################################################
def get_ad_user_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_user_names = ad_server_info.getElementsByTagName('ad_user_names')
    ad_user_name_list = []
    for policies in ad_user_names:
        for policy in policies.getElementsByTagName('ad_user_name'):
            ad_user_name = policy.firstChild.nodeValue
            ad_user_name_list.append(ad_user_name)
    return ad_user_name_list


##############################################################################
# ##name  :      get_ad_password
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的管理员用户密码
##############################################################################
def get_ad_password():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_passwords = ad_server_info.getElementsByTagName('ad_passwords')
    ad_password_list = []
    for ad_password in ad_passwords:
        ad_password = ad_password.getElementsByTagName('ad_password')[0].firstChild.nodeValue
        ad_password_list.append(ad_password)
    return ad_password_list


##############################################################################
# ##name  :      get_ad_users
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的用户
##############################################################################
def get_ad_users():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_users = ad_server_info.getElementsByTagName('ad_users')
    ad_user_name_list = []
    for policies in ad_users:
        for policy in policies.getElementsByTagName('ad_user'):
            ad_user = policy.firstChild.nodeValue
            ad_user_name_list.append(ad_user)
    return ad_user_name_list


##############################################################################
# ##name  :      get_ad_groups
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的用户组
##############################################################################
def get_ad_groups():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_groups = ad_server_info.getElementsByTagName('ad_groups')
    ad_group_name_list = []
    for policies in ad_groups:
        for policy in policies.getElementsByTagName('ad_group'):
            ad_group = policy.firstChild.nodeValue
            ad_group_name_list.append(ad_group)
    return ad_group_name_list


##############################################################################
# ##name  :      get_ad_user_pw
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的普通用户密码
##############################################################################
def get_ad_user_pw():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('ad_server_info')[0]
    ad_user_pws = ad_server_info.getElementsByTagName('ad_user_pws')
    ad_user_pw_list = []
    for ad_user_pw in ad_user_pws:
        ad_user_pw = ad_user_pw.getElementsByTagName('ad_user_pw')[0].firstChild.nodeValue
        ad_user_pw_list.append(ad_user_pw)
    return ad_user_pw_list


##############################################################################
# ##name  :      get_nis_domain_name
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取nis鉴权服务器的域名
##############################################################################
def get_nis_domain_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nis_server_info = config_info.getElementsByTagName('nis_server_info')[0]
    nis_domain_names = nis_server_info.getElementsByTagName('nis_domain_names')
    nis_domain_name_list = []
    for nis_domain_name in nis_domain_names:
        nis_domain_name = nis_domain_name.getElementsByTagName('nis_domain_name')[0].firstChild.nodeValue
        nis_domain_name_list.append(nis_domain_name)
    return nis_domain_name_list


##############################################################################
# ##name  :      get_nis_ip_address
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取nis鉴权服务器的地址
##############################################################################
def get_nis_ip_address():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nis_server_info = config_info.getElementsByTagName('nis_server_info')[0]
    nis_ip_addresses = nis_server_info.getElementsByTagName('nis_ip_addresses')
    nis_ip_address_list = []
    for nis_ip_address in nis_ip_addresses:
        nis_ip_address = nis_ip_address.getElementsByTagName('nis_ip_address')[0].firstChild.nodeValue
        nis_ip_address_list.append(nis_ip_address)
    return nis_ip_address_list


##############################################################################
# ##name  :      get_nis_users
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取nis鉴权服务器的用户
##############################################################################
def get_nis_users():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nis_server_info = config_info.getElementsByTagName('nis_server_info')[0]
    nis_users = nis_server_info.getElementsByTagName('nis_users')
    nis_user_name_list = []
    for policies in nis_users:
        for policy in policies.getElementsByTagName('nis_user'):
            nis_user = policy.firstChild.nodeValue
            nis_user_name_list.append(nis_user)
    return nis_user_name_list


##############################################################################
# ##name  :      get_nis_groups
# ##parameter:
# ##author:      zhangchengyu
# ##date  :      2018.11.21
# ##Description: 获取nis鉴权服务器的用户组
##############################################################################
def get_nis_groups():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nis_server_info = config_info.getElementsByTagName('nis_server_info')[0]
    nis_groups = nis_server_info.getElementsByTagName('nis_groups')
    nis_group_name_list = []
    for policies in nis_groups:
        for policy in policies.getElementsByTagName('nis_group'):
            nis_group = policy.firstChild.nodeValue
            nis_group_name_list.append(nis_group)
    return nis_group_name_list


##############################################################################
# ##name  :      get_nis_user_pw
# ##parameter:
# ##author:      jiangxiaoguang
# ##date  :      2018.08.24
# ##Description: 获取ad鉴权服务器的普通用户密码
##############################################################################
def get_nis_user_pw():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    nis_server_info = config_info.getElementsByTagName('nis_server_info')[0]
    nis_user_pws = nis_server_info.getElementsByTagName('nis_user_pws')
    nis_user_pw_list = []
    for nis_user_pw in nis_user_pws:
        nis_user_pw = nis_user_pw.getElementsByTagName('nis_user_pw')[0].firstChild.nodeValue
        nis_user_pw_list.append(nis_user_pw)
    return nis_user_pw_list


##############################################################################
# ##name  :      get_new_pkg_position
# ##parameter:
# ##author:      chenjy1
# ##date  :      2018.11.13
# ##Description: 每天发新包的位置
##############################################################################
def get_new_pkg_position():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    new_pkg_position = config_info.getElementsByTagName('new_pkg_position')[0].firstChild.nodeValue
    return new_pkg_position


def get_upgrade_case_file():
    """
    author:   baoruobing
    function: 获取升级后要跑的用例文件
    date:     2018-12-11
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    upgrade_case_file = config_info.getElementsByTagName('upgrade_case_list')[0].firstChild.nodeValue
    return upgrade_case_file


def get_win_client_ips():
    """
    name: get_win_client_ips
    function: 从nas配置文件中获取windows客户端ip
    author: liyao
    date: 2018-11-23
    :return: windows客户端ip
    """
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    win_client_info = config_info.getElementsByTagName('remote_win_client_info')[0]
    win_client_ips = win_client_info.getElementsByTagName('win_client_ips')[0]
    win_client_ips = win_client_ips.getElementsByTagName('win_client_ip')
    win_client_ip_lst = []
    for mem in win_client_ips:
        client_ip = mem.getElementsByTagName('win_ip')[0].firstChild.nodeValue
        win_client_ip_lst.append(client_ip)
    return win_client_ip_lst


def get_win_disk_symbols():
    """
    name: get_win_disk_symbols
    function: 从nas配置文件中获取windows客户端的盘符
    author: liyao
    date: 2018-11-26
    :return: windows客户端盘符列表
    """
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    win_client_info = config_info.getElementsByTagName('remote_win_client_info')[0]
    win_disk_symbols = win_client_info.getElementsByTagName('win_disk_symbols')[0]
    win_disk_symbols = win_disk_symbols.getElementsByTagName('win_disk_symbol')
    win_disk_symbol_lst = []
    for mem in win_disk_symbols:
        symbol = mem.getElementsByTagName('symbol')[0].firstChild.nodeValue
        win_disk_symbol_lst.append(symbol)
    return win_disk_symbol_lst


##############################################################################
# ##name  :      get_webui_ip  get_explore_name get_web_node_name  get_web_node_ip get_web_pkg_position
# ##parameter:
# ##author:      duyuli
# ##date  :      2018.12.04
# ##Description: 集群虚ip地址
##############################################################################
def get_web_ip():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_ip = dom.getElementsByTagName('webui_ip')[0].firstChild.nodeValue
    return web_ip


def get_explorer_name():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    explore_name = dom.getElementsByTagName('explorer_name')[0].firstChild.nodeValue
    return explore_name


def get_web_node_name():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    node_name = dom.getElementsByTagName('web_node_name')[0].firstChild.nodeValue
    return node_name


def get_web_node_ip():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    node_ip = dom.getElementsByTagName('web_node_ip')[0].firstChild.nodeValue
    return node_ip


def get_web_pkg_position():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_pkg_position = dom.getElementsByTagName('web_pkg_position')[0].firstChild.nodeValue
    return web_pkg_position


def get_web_eth_name_ctrl():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_eth_name_ctrl = dom.getElementsByTagName('web_eth_name_ctrl')[0].firstChild.nodeValue
    return web_eth_name_ctrl


def get_web_eth_name_no_ip():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_eth_name_no_ip = dom.getElementsByTagName('web_eth_name_no_ip')[0].firstChild.nodeValue
    return web_eth_name_no_ip


def get_web_eth_name_data_list():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_eth_name_data_list = dom.getElementsByTagName('web_eth_name_data')
    eth_name_data_list = []
    for web_eth_name_data in web_eth_name_data_list:
        eth_name_data_list.append(web_eth_name_data.firstChild.nodeValue)
    return eth_name_data_list


def get_web_disk_size():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_disk_size = dom.getElementsByTagName('web_disk_size')[0].firstChild.nodeValue
    return web_disk_size


def get_web_network_mask():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_network_mask = dom.getElementsByTagName('web_network_mask')[0].firstChild.nodeValue
    return web_network_mask


def get_web_machine():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_machine = dom.getElementsByTagName('web_machine')[0].firstChild.nodeValue
    return web_machine


def get_web_login_name():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_login_name = dom.getElementsByTagName('web_login_name')[0].firstChild.nodeValue
    return web_login_name


def get_web_login_pwd():
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    web_login_pwd = dom.getElementsByTagName('web_login_pwd')[0].firstChild.nodeValue
    return web_login_pwd


##############################################################################
# ##name  :      get_access_zone_name
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.06
# ##Description: 获取访问区的名称
##############################################################################
def get_access_zone_name():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    access_zone_info = config_info.getElementsByTagName('access_zone_info')[0]
    access_zone_name = access_zone_info.getElementsByTagName('access_zone_names')
    access_zone_name_list = []
    for policies in access_zone_name:
        for policy in policies.getElementsByTagName('access_zone_name'):
            access_zone_name_i = policy.firstChild.nodeValue
            access_zone_name_list.append(access_zone_name_i)
    return access_zone_name_list


##############################################################################
# ##name  :      get_ad_domain_name_dac
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.05
# ##Description: 获取ad鉴权服务器的域名，dac测试使用
##############################################################################
def get_ad_domain_name_dac():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('dac_ad_server_info')[0]
    ad_domain_names = ad_server_info.getElementsByTagName('ad_domain_names')
    ad_domain_name_list = []
    for ad_domain_name in ad_domain_names:
        ad_domain_name = ad_domain_name.getElementsByTagName('ad_domain_name')[0].firstChild.nodeValue
        ad_domain_name_list.append(ad_domain_name)
    return ad_domain_name_list


##############################################################################
# ##name  :      get_ad_users_dac
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.05
# ##Description: 获取ad鉴权服务器的用户，dac用
##############################################################################
def get_ad_users_dac():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('dac_ad_server_info')[0]
    ad_users = ad_server_info.getElementsByTagName('ad_users')
    ad_user_name_list = []
    for policies in ad_users:
        for policy in policies.getElementsByTagName('ad_user'):
            ad_user = policy.firstChild.nodeValue
            ad_user_name_list.append(ad_user)
    return ad_user_name_list


##############################################################################
# ##name  :      get_ad_user_pw_dac
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.05
# ##Description: 获取ad鉴权服务器的普通用户密码,dac用
##############################################################################
def get_ad_user_pw_dac():
    config_info = xml.dom.minidom.parse(NAS_CONFIG_FILE)
    ad_server_info = config_info.getElementsByTagName('dac_ad_server_info')[0]
    ad_user_pws = ad_server_info.getElementsByTagName('ad_user_pws')
    ad_user_pw_list = []
    for ad_user_pw in ad_user_pws:
        ad_user_pw = ad_user_pw.getElementsByTagName('ad_user_pw')[0].firstChild.nodeValue
        ad_user_pw_list.append(ad_user_pw)
    return ad_user_pw_list


def get_expand_ip_info():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    nodes_info = config_info.getElementsByTagName('expand_nodes')[0]
    nodes_info = nodes_info.getElementsByTagName('node')
    ip_list = []
    for node in nodes_info:
        ip = node.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    return ip_list


def get_tl():
    """
    author:   baoruobing
    function: 获取是否运行testlink
    date:     2018-12-11
    :return:
    """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_flag = dom.getElementsByTagName('testlink')[0].firstChild.nodeValue
    if tl_flag == 'true':
        return True
    else:
        return False


def get_tl_url():
    """
    author:   baoruobing
    function: 获取testlink的url
    date:     2018-12-11
    :return:
    """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_url = dom.getElementsByTagName('tlurl')[0].firstChild.nodeValue
    return tl_url


def get_tl_devkey():
    """
    author:   baoruobing
    function: 获取testlink的devkey
    date:     2018-12-11
    :return:
    """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_devkey = dom.getElementsByTagName('tldevkey')[0].firstChild.nodeValue
    return tl_devkey


def get_tl_projectname():
    """
    author:   baoruobing
    function: 获取testlink的projectname
    date:     2018-12-11
    :return:
    """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_projectname = dom.getElementsByTagName('tlprojectname')[0].firstChild.nodeValue
    return tl_projectname


def get_tl_planname():
    """
    author:   baoruobing
    function: 获取testlink的planname
    date:     2018-12-11
    :return:

    """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_planname = dom.getElementsByTagName('tlplanname')[0].firstChild.nodeValue
    return tl_planname


def get_tl_platformname():
    """
        author:   baoruobing
        function: 获取testlink的platformname
        date:     2018-12-11
        :return:
        """
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    tl_planname = dom.getElementsByTagName('tlplatformname')[0].firstChild.nodeValue
    return tl_planname


def get_esxi_info(is_get_all=False):
    """
    获取虚拟机ESXI的ip、用户名、密码
    :author:            caizhenxing
    :param is_get_all:  是否获取所有ESXI
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    esxi_info = config_info.getElementsByTagName('esxis')[0]
    esxi_infos = esxi_info.getElementsByTagName('esxi')
    esxi_info_lst = []
    for esxi in esxi_infos:
        ip = esxi.getElementsByTagName('ip')[0].firstChild.nodeValue
        name = esxi.getElementsByTagName('name')[0].firstChild.nodeValue
        pwd = esxi.getElementsByTagName('pwd')[0].firstChild.nodeValue
        esxi_ip = (ip,)
        esxi_name = (name,)
        esxi_pwd = (pwd,)
        esxi_info_final = esxi_ip + esxi_name + esxi_pwd
        esxi_info_lst.append(esxi_info_final)

    if is_get_all:
        return esxi_info_lst
    else:
        return list((random.choice(esxi_info_lst),))


##############################################################################
# ##name  :      get_cosbench_client_ip
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.24
# ##Description: 获取cosbench客户端ip
##############################################################################
def get_cosbench_client_ip():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    cosbench_ips = config_info.getElementsByTagName('cosbench_client_ips')[0]
    cosbench_ips = cosbench_ips.getElementsByTagName('cosbench_client_ip')
    cosbench_ip_list = []
    for mem in cosbench_ips:
        cosbench_ip = mem.firstChild.nodeValue
        cosbench_ip_list.append(cosbench_ip)
    return cosbench_ip_list


##############################################################################
# ##name  :      get_machine_type
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.24
# ##Description: 获取cosbench测试工具位置
##############################################################################
def get_cosbench_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    type_info = config_info.getElementsByTagName('cosbench_path')[0].firstChild.nodeValue
    return type_info


##############################################################################
# ##name  :      get_cosbench_xml_file_path
# ##parameter:
# ##author:      zhanghan
# ##date  :      2018.12.24
# ##Description: 获取cosbench的xml脚本路径
##############################################################################
def get_cosbench_xml_file_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    cosbench_paths = config_info.getElementsByTagName('cosbench_xml_file_paths')[0]
    cosbench_paths = cosbench_paths.getElementsByTagName('cosbench_xml_file_path')
    cosbench_path_list = []
    for mem in cosbench_paths:
        cosbench_path = mem.firstChild.nodeValue
        cosbench_path_list.append(cosbench_path)
    return cosbench_path_list


##############################################################################
# ##name  :      get_cosbench_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2018.12.28
# ##Description: 获取cosbench的参数，返回一个字典
##############################################################################
def get_cosbench_param():
    cosbench_param_dict = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    cosbench_params = config_info.getElementsByTagName('cosbench_param')[0]

    cosbench_path = cosbench_params.getElementsByTagName('cosbench_path')[0].firstChild.nodeValue
    cosbench_param_dict['cosbench_path'] = cosbench_path.encode('utf-8').split()[0]

    cosbench_client_ips = config_info.getElementsByTagName('cosbench_client_ips')
    cosbench_client_ip_lst = []
    for ip in cosbench_client_ips:
        cosbench_client_ip_lst = ip.firstChild.nodeValue.encode('utf-8').split()
        # cosbench_client_ip_lst.append(cosbench_client_ip.encode('utf-8').split()[0])
    cosbench_param_dict['cosbench_client_ip_lst'] = cosbench_client_ip_lst

    # create_file_path = cosbench_params.getElementsByTagName('create_file_path')[0].firstChild.nodeValue
    # cosbench_param_dict['create_file_path'] = create_file_path.encode('utf-8').split()[0]

    xml_paths = config_info.getElementsByTagName('xml_paths')
    xml_path_lst = []
    for xml_path in xml_paths:
        xml_path_lst = xml_path.firstChild.nodeValue.encode('utf-8').split()
        # xml_path_lst.append(xml_path.encode('utf-8').split()[0])
    cosbench_param_dict['xml_path_lst'] = xml_path_lst

    init_base_time = cosbench_params.getElementsByTagName('init_base_time')[0].firstChild.nodeValue
    cosbench_param_dict['init_base_time'] = init_base_time.encode('utf-8').split()[0]

    prepare_base_time = cosbench_params.getElementsByTagName('prepare_base_time')[0].firstChild.nodeValue
    cosbench_param_dict['prepare_base_time'] = prepare_base_time.encode('utf-8').split()[0]

    main_base_time = cosbench_params.getElementsByTagName('main_base_time')[0].firstChild.nodeValue
    cosbench_param_dict['main_base_time'] = main_base_time.encode('utf-8').split()[0]
    
    fault_in_which_stage = cosbench_params.getElementsByTagName('fault_in_which_stage')[0].firstChild.nodeValue
    cosbench_param_dict['fault_in_which_stage'] = fault_in_which_stage.encode('utf-8').split()[0]
    return cosbench_param_dict


##############################################################################
# ##name  :      get_fault_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2018.12.28
# ##Description: 获取做故障需要的参数，返回一个字典
##############################################################################
def get_fault_param():
    fault_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    fault_params = config_info.getElementsByTagName('fault_param')[0]

    fault_config_path = fault_params.getElementsByTagName('fault_config_path')[0].firstChild.nodeValue
    fault_param['fault_config_path'] = fault_config_path.encode('utf-8').split()[0]

    fault_num = fault_params.getElementsByTagName('fault_num')[0].firstChild.nodeValue
    fault_param['fault_num'] = fault_num.encode('utf-8').split()[0]
    return fault_param


##############################################################################
# ##name  :      get_data_consistency_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2018.12.28
# ##Description: 获取数据一致性脚本需要的参数，返回一个字典
##############################################################################
def get_data_consistency_param():
    data_consistency_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    data_consistency_params = config_info.getElementsByTagName('data_consistency_param')[0]

    parent_dir = data_consistency_params.getElementsByTagName('parent_dir')[0].firstChild.nodeValue
    data_consistency_param['parent_dir'] = parent_dir.encode('utf-8').split()[0]

    vdb_thread_num = data_consistency_params.getElementsByTagName('vdb_thread_num')[0].firstChild.nodeValue
    data_consistency_param['vdb_thread_num'] = vdb_thread_num.encode('utf-8').split()[0]

    vdb_width = data_consistency_params.getElementsByTagName('vdb_width')[0].firstChild.nodeValue
    data_consistency_param['vdb_width'] = vdb_width.encode('utf-8').split()[0]

    round_timeout = data_consistency_params.getElementsByTagName('round_timeout')[0].firstChild.nodeValue
    data_consistency_param['round_timeout'] = round_timeout.encode('utf-8').split()[0]
    return data_consistency_param


'''
##############################################################################
# ##name  :      get_s3_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2018.12.28
# ##Description: 获取s3相关参数，返回一个字典
##############################################################################
def get_s3_param():
    s3_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    domain_names = config_info.getElementsByTagName('s3_domain_name')
    # domain_names = config_info.getElementsByTagName('domain_name')
    domain_name_lst = []
    for domain_name in domain_names:
        domain_name_lst = domain_name.firstChild.nodeValue.encode('utf-8').split()
    s3_param['domain_name_lst'] = domain_name_lst
    return s3_param
'''


##############################################################################
# ##name  :      get_nas_vdbench_param
# ##parameter:
# ##author:      liuyzhb
# ##date  :      2019.1.19
# ##Description: 获取nas客户端的vdbench脚本需要的参数，返回一个字典
#############################################################################

def get_nas_vdbench_param():
    nas_vdbench_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    nas_vdbench_params = config_info.getElementsByTagName('nas_vdbench_param')[0]

    vdbflagname = nas_vdbench_params.getElementsByTagName('vdbflagname')[0].firstChild.nodeValue
    nas_vdbench_param['vdbflagname'] = vdbflagname.encode('utf-8').split()[0]

    vdb_thread_num = nas_vdbench_params.getElementsByTagName('vdb_flag')[0].firstChild.nodeValue
    nas_vdbench_param['vdb_flag'] = vdb_thread_num.encode('utf-8').split()[0]

    loop_execute_num = nas_vdbench_params.getElementsByTagName('anchor_path')[0].firstChild.nodeValue
    nas_vdbench_param['anchor_path'] = loop_execute_num.encode('utf-8').split()[0]

    journal_path = nas_vdbench_params.getElementsByTagName('journal_path')[0].firstChild.nodeValue
    nas_vdbench_param['journal_path'] = journal_path.encode('utf-8').split()[0]

    ip = nas_vdbench_params.getElementsByTagName('ip')[0].firstChild.nodeValue
    nas_vdbench_param['ip'] = ip.encode('utf-8').split()[0]

    elapsed = nas_vdbench_params.getElementsByTagName('elapsed')[0].firstChild.nodeValue
    nas_vdbench_param['elapsed'] = elapsed.encode('utf-8').split()[0]

    output_path = nas_vdbench_params.getElementsByTagName('output_path')[0].firstChild.nodeValue
    nas_vdbench_param['output_path'] = output_path.encode('utf-8').split()[0]

    operations = nas_vdbench_params.getElementsByTagName('operations')[0].firstChild.nodeValue
    nas_vdbench_param['operations'] = operations.encode('utf-8').split()[0]

    format = nas_vdbench_params.getElementsByTagName('format')[0].firstChild.nodeValue
    nas_vdbench_param['format'] = format.encode('utf-8').split()[0]

    threads = nas_vdbench_params.getElementsByTagName('threads')[0].firstChild.nodeValue
    nas_vdbench_param['threads'] = threads.encode('utf-8').split()[0]

    depth = nas_vdbench_params.getElementsByTagName('depth')[0].firstChild.nodeValue
    nas_vdbench_param['depth'] = depth.encode('utf-8').split()[0]

    width = nas_vdbench_params.getElementsByTagName('width')[0].firstChild.nodeValue
    nas_vdbench_param['width'] = width.encode('utf-8').split()[0]

    files = nas_vdbench_params.getElementsByTagName('files')[0].firstChild.nodeValue
    nas_vdbench_param['files'] = files.encode('utf-8').split()[0]

    size = nas_vdbench_params.getElementsByTagName('size')[0].firstChild.nodeValue
    nas_vdbench_param['size'] = size.encode('utf-8').split()[0]

    xfersize = nas_vdbench_params.getElementsByTagName('xfersize')[0].firstChild.nodeValue
    nas_vdbench_param['xfersize'] = xfersize.encode('utf-8').split()[0]
	
    jn_check_internal_step = nas_vdbench_params.getElementsByTagName('jn_check_internal_step')[0].firstChild.nodeValue
    nas_vdbench_param['jn_check_internal_step'] = jn_check_internal_step.encode('utf-8').split()[0]

    jn_map_storage_time = nas_vdbench_params.getElementsByTagName('jn_map_storage_time')[0].firstChild.nodeValue
    nas_vdbench_param['jn_map_storage_time'] = jn_map_storage_time.encode('utf-8').split()[0]

    return nas_vdbench_param


##############################################################################
# ##name  :      get_posix_vdbench_param
# ##parameter:
# ##author:      liuyzhb
# ##date  :      2019.1.19
# ##Description: 获取nas客户端的vdbench脚本需要的参数，返回一个字典
#############################################################################

def get_posix_vdbench_param():
    nas_vdbench_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    nas_vdbench_params = config_info.getElementsByTagName('posix_vdbench_param')[0]

    vdbflagname = nas_vdbench_params.getElementsByTagName('vdbflagname')[0].firstChild.nodeValue
    nas_vdbench_param['vdbflagname'] = vdbflagname.encode('utf-8').split()[0]

    vdb_thread_num = nas_vdbench_params.getElementsByTagName('vdb_flag')[0].firstChild.nodeValue
    nas_vdbench_param['vdb_flag'] = vdb_thread_num.encode('utf-8').split()[0]

    loop_execute_num = nas_vdbench_params.getElementsByTagName('anchor_path')[0].firstChild.nodeValue
    nas_vdbench_param['anchor_path'] = loop_execute_num.encode('utf-8').split()[0]

    journal_path = nas_vdbench_params.getElementsByTagName('journal_path')[0].firstChild.nodeValue
    nas_vdbench_param['journal_path'] = journal_path.encode('utf-8').split()[0]

    ip = nas_vdbench_params.getElementsByTagName('ip')[0].firstChild.nodeValue
    nas_vdbench_param['ip'] = ip.encode('utf-8').split()[0]

    elapsed = nas_vdbench_params.getElementsByTagName('elapsed')[0].firstChild.nodeValue
    nas_vdbench_param['elapsed'] = elapsed.encode('utf-8').split()[0]

    output_path = nas_vdbench_params.getElementsByTagName('output_path')[0].firstChild.nodeValue
    nas_vdbench_param['output_path'] = output_path.encode('utf-8').split()[0]

    operations = nas_vdbench_params.getElementsByTagName('operations')[0].firstChild.nodeValue
    nas_vdbench_param['operations'] = operations.encode('utf-8').split()[0]

    format = nas_vdbench_params.getElementsByTagName('format')[0].firstChild.nodeValue
    nas_vdbench_param['format'] = format.encode('utf-8').split()[0]

    threads = nas_vdbench_params.getElementsByTagName('threads')[0].firstChild.nodeValue
    nas_vdbench_param['threads'] = threads.encode('utf-8').split()[0]

    depth = nas_vdbench_params.getElementsByTagName('depth')[0].firstChild.nodeValue
    nas_vdbench_param['depth'] = depth.encode('utf-8').split()[0]

    width = nas_vdbench_params.getElementsByTagName('width')[0].firstChild.nodeValue
    nas_vdbench_param['width'] = width.encode('utf-8').split()[0]

    files = nas_vdbench_params.getElementsByTagName('files')[0].firstChild.nodeValue
    nas_vdbench_param['files'] = files.encode('utf-8').split()[0]

    size = nas_vdbench_params.getElementsByTagName('size')[0].firstChild.nodeValue
    nas_vdbench_param['size'] = size.encode('utf-8').split()[0]

    xfersize = nas_vdbench_params.getElementsByTagName('xfersize')[0].firstChild.nodeValue
    nas_vdbench_param['xfersize'] = xfersize.encode('utf-8').split()[0]
	
    jn_check_internal_step = nas_vdbench_params.getElementsByTagName('jn_check_internal_step')[0].firstChild.nodeValue
    nas_vdbench_param['jn_check_internal_step'] = jn_check_internal_step.encode('utf-8').split()[0]

    jn_map_storage_time = nas_vdbench_params.getElementsByTagName('jn_map_storage_time')[0].firstChild.nodeValue
    nas_vdbench_param['jn_map_storage_time'] = jn_map_storage_time.encode('utf-8').split()[0]


    return nas_vdbench_param

def get_read_ahead_switch(conf_file):
    """
    author:   liuhe
    function: 获取conf中预读开关状态
    date:     2010-01-22
    :return:
    """
    dom = xml.dom.minidom.parse(conf_file)
    read_ahead_status = dom.getElementsByTagName('read_ahead')[0].firstChild.nodeValue
    return read_ahead_status

##############################################################################
# ##name  :      get_log_collect_scripts_path
# ##parameter:
# ##author:      zhanghan
# ##date  :      2019.1.24
# ##Description: 获取收集日志脚本的位置，返回一个字符串
#############################################################################
def get_log_collect_scripts_path():
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    log_collect_param = config_info.getElementsByTagName('log_collect_param')[0]
    log_collect_scripts_path = log_collect_param.getElementsByTagName('log_collect_scripts_path')[0].firstChild.nodeValue
    return log_collect_scripts_path


##############################################################################
# ##name  :      get_log_storage_ip
# ##parameter:
# ##author:      zhanghan
# ##date  :      2019.1.24
# ##Description: 获取存放日志的节点ip，返回一个字符串
#############################################################################
def get_log_storage_ip():
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    log_collect_param = config_info.getElementsByTagName('log_collect_param')[0]
    log_storage_ip = log_collect_param.getElementsByTagName('log_storage_ip')[0].firstChild.nodeValue
    return log_storage_ip


##############################################################################
# ##name  :      get_log_storage_path
# ##parameter:
# ##author:      zhanghan
# ##date  :      2019.1.24
# ##Description: 获取存放日志的路径，返回一个字符串
#############################################################################
def get_log_storage_path():
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    log_collect_param = config_info.getElementsByTagName('log_collect_param')[0]
    log_storage_path = log_collect_param.getElementsByTagName('log_storage_path')[0].firstChild.nodeValue
    return log_storage_path

##############################################################################
# ##name  :      get_dac_smb_info
# ##parameter:
# ##author:      zhanghan
# ##date  :      2019.1.29
# ##Description: 获取dac所需smb客户端的信息，返回一个字典
#############################################################################
def get_dac_smb_info():
    dac_smb_info_dict = dict()
    tree = xml.etree.ElementTree.parse(NAS_CONFIG_FILE)
    root = tree.find('dac_smb_info')
    # print(root)
    for item in root:
        dac_smb_info_dict[item.tag] = item.text
    return dac_smb_info_dict


def get_rep_config_file():
    '''
    author:chenjy1
    description:获取rep配置文件名
    :return:
    '''
    dom = xml.dom.minidom.parse(CONFIG_FILE)
    rep_config_file_name = dom.getElementsByTagName('rep_config_file_name')[0].firstChild.nodeValue
    return os.path.join(config_path, rep_config_file_name)


def get_rep_master_test_path():
    '''
    author:chenjy1
    description:获取远程复制主端测试路径
    :return:
    '''
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    client_install_path = config_info.getElementsByTagName('rep_master_test_path')[0].firstChild.nodeValue
    return client_install_path


def get_slave_node_lst():
    """
    author:chenjy1
    description:获取远程复制从端集群ip
    :param:
    :return: ip_list
    """
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    nodes_info = config_info.getElementsByTagName('slave_nodes')[0]
    nodes_info = nodes_info.getElementsByTagName('node')
    ip_list = []
    for node in nodes_info:
        ip = node.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    return ip_list


def get_slave_client_lst():
    """
    author:chenjy1
    description:获取远程复制从端客户端ip
    :param:
    :return: ip_list
    """
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    client_info = config_info.getElementsByTagName('slave_clients')[0]
    client_infos = client_info.getElementsByTagName('client')
    ip_list = []
    for client in client_infos:
        ip = client.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    ip_list2 = list(set(ip_list))
    ip_list2.sort(key=ip_list.index)
    return ip_list


def get_salve_volume_names():
    '''
    author:chenjy1
    description:获取从端卷名列表
    :return:
    '''
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    volumes = config_info.getElementsByTagName('slave_volumes')[0]
    volumes = volumes.getElementsByTagName('volume')
    volume_list = []
    for mem in volumes:
        volume = mem.firstChild.nodeValue
        volume_list.append(volume)
    return volume_list


def get_third_cluster_volume_names():
    '''
    author:chenjy1
    description:获取第三集群卷名列表
    :return:
    '''
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    volumes = config_info.getElementsByTagName('third_cluster_volumes')[0]
    volumes = volumes.getElementsByTagName('volume')
    volume_list = []
    for mem in volumes:
        volume = mem.firstChild.nodeValue
        volume_list.append(volume)
    return volume_list


def get_slave_volume_name(num=0):
    '''
    author:chenjy1
    description:获取从端第n个卷名
    :param num:
    :return:
    '''
    volume_list = get_salve_volume_names()
    if num >= len(volume_list):
        num = len(volume_list) - 1
    return volume_list[num]


def get_rep_slave_test_path():
    '''
    author:chenjy1
    description:获取从端测试路径
    :return:
    '''
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    client_install_path = config_info.getElementsByTagName('rep_slave_test_path')[0].firstChild.nodeValue
    return client_install_path

def get_third_cluster_nodes_lst():
    """
    author:chenjy1
    description:获取第三端集群ip
    :param:
    :return: ip_list
    """
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    nodes_info = config_info.getElementsByTagName('third_cluster_nodes')[0]
    nodes_info = nodes_info.getElementsByTagName('node')
    ip_list = []
    for node in nodes_info:
        ip = node.getElementsByTagName('ctrl_ip')[0].firstChild.nodeValue
        ip_list.append(ip)
    return ip_list


def get_third_cluster_volume_name(num=0):
    '''
    author:chenjy1
    description:获取第三集群第n个卷名
    :param num:
    :return:
    '''
    volume_list = get_salve_volume_names()
    if num >= len(volume_list):
        num = len(volume_list) - 1
    return volume_list[num]


def get_rep_third_cluster_test_path():
    '''
    author:chenjy1
    description:获取第三集群测试路径
    :return:
    '''
    config_info = xml.dom.minidom.parse(get_rep_config_file())
    client_install_path = config_info.getElementsByTagName('rep_third_cluster_test_path')[0].firstChild.nodeValue
    return client_install_path


##############################################################################
# ##name  :      get_nas_iozone_param
# ##parameter:
# ##author:      liuyzhb
# ##date  :      2019.02.19
# ##Description: 获取nas nfs客户端的iozone参数
##############################################################################
def get_nas_iozone_param():
    nas_iozone_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    nas_iozone_params = config_info.getElementsByTagName('nas_iozone_param')[0]

    iozonethreads = nas_iozone_params.getElementsByTagName('iozonethreads')[0].firstChild.nodeValue
    nas_iozone_param['iozonethreads'] = iozonethreads.encode('utf-8').split()[0]

    size = nas_iozone_params.getElementsByTagName('size')[0].firstChild.nodeValue
    nas_iozone_param['size'] = size.encode('utf-8').split()[0]

    xfersize = nas_iozone_params.getElementsByTagName('xfersize')[0].firstChild.nodeValue
    nas_iozone_param['xfersize'] = xfersize.encode('utf-8').split()[0]

    num = nas_iozone_params.getElementsByTagName('num')[0].firstChild.nodeValue
    nas_iozone_param['num'] = num.encode('utf-8').split()[0]
    return nas_iozone_param


##############################################################################
# ##name  :      get_posix_iozone_param
# ##parameter:
# ##author:      liuyzhb
# ##date  :      2019.02.20
# ##Description: 获取posix客户端的iozone参数
##############################################################################
def get_posix_iozone_param():
    posix_iozone_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    posix_iozone_params = config_info.getElementsByTagName('posix_iozone_param')[0]

    iozonethreads = posix_iozone_params.getElementsByTagName('iozonethreads')[0].firstChild.nodeValue
    posix_iozone_param['iozonethreads'] = iozonethreads.encode('utf-8').split()[0]

    size = posix_iozone_params.getElementsByTagName('size')[0].firstChild.nodeValue
    posix_iozone_param['size'] = size.encode('utf-8').split()[0]

    xfersize = posix_iozone_params.getElementsByTagName('xfersize')[0].firstChild.nodeValue
    posix_iozone_param['xfersize'] = xfersize.encode('utf-8').split()[0]

    num = posix_iozone_params.getElementsByTagName('num')[0].firstChild.nodeValue
    posix_iozone_param['num'] = num.encode('utf-8').split()[0]

    return posix_iozone_param


##############################################################################
# ##name  :      get_windows__paths
# ##parameter:
# ##author:      caizhenxing
# ##date  :      2019.02.22
# ##Description: 获取windows文件路径
##############################################################################
def get_windows__paths():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    mnt_paths = config_info.getElementsByTagName('windows_paths')[0]
    mnt_paths = mnt_paths.getElementsByTagName('mount_path')
    mnt_path_list = []
    for mem in mnt_paths:
        mnt_path = mem.firstChild.nodeValue
        mnt_path_list.append(mnt_path)
    return mnt_path_list


##############################################################################
# ##name  :      get_one_windows_path
# ##parameter:   num=0:第几条路径，默认是第一条
# ##author:      caizhenxing
# ##date  :      2019.02.22
# ##Description: 获取一条windows文件路径，默认是第一条
##############################################################################
def get_one_windows_path(num=0):
    mnt_path_list = get_windows__paths()
    if num >= len(mnt_path_list):
        num = len(mnt_path_list) - 1
    return mnt_path_list[num]


##############################################################################
# ##name  :      get_mdtest_param
# ##parameter:
# ##author:      xutengda
# ##date  :      2019.02.23
# ##Description: 获取客户端的mdtest参数
##############################################################################
def get_mdtest_param():
    get_mdtest_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    get_mdtest_params = config_info.getElementsByTagName('mdtest_param')[0]

    depth = get_mdtest_params.getElementsByTagName('depth')[0].firstChild.nodeValue
    get_mdtest_param['depth'] = depth.encode('utf-8').split()[0]

    width = get_mdtest_params.getElementsByTagName('width')[0].firstChild.nodeValue
    get_mdtest_param['width'] = width.encode('utf-8').split()[0]

    files = get_mdtest_params.getElementsByTagName('files')[0].firstChild.nodeValue
    get_mdtest_param['files'] = files.encode('utf-8').split()[0]

    sizes = get_mdtest_params.getElementsByTagName('sizes')[0].firstChild.nodeValue
    get_mdtest_param['sizes'] = sizes.encode('utf-8').split()[0]

    num = get_mdtest_params.getElementsByTagName('num')[0].firstChild.nodeValue
    get_mdtest_param['num'] = num.encode('utf-8').split()[0]

    run_in_nas = get_mdtest_params.getElementsByTagName('run_in_nas')[0].firstChild.nodeValue
    get_mdtest_param['run_in_nas'] = run_in_nas.encode('utf-8').split()[0]

    run_in_posix = get_mdtest_params.getElementsByTagName('run_in_posix')[0].firstChild.nodeValue
    get_mdtest_param['run_in_posix'] = run_in_posix.encode('utf-8').split()[0]
    
    return get_mdtest_param



##############################################################################
# ##name  :      get_stress_type_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2019.02.25
# ##Description: 获取故障可靠性测试需要运行哪些压力
##############################################################################
def get_stress_type_param():
    stress_type_param = dict()
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    get_stress_type_params = config_info.getElementsByTagName('stress_type_param')[0]

    if_run_cosbench = get_stress_type_params.getElementsByTagName('if_run_cosbench')[0].firstChild.nodeValue
    stress_type_param['if_run_cosbench'] = if_run_cosbench.encode('utf-8').split()[0]

    if_run_s3_consistency = get_stress_type_params.getElementsByTagName('if_run_s3_consistency')[0].firstChild.nodeValue
    stress_type_param['if_run_s3_consistency'] = if_run_s3_consistency.encode('utf-8').split()[0]

    if_run_vdbench = get_stress_type_params.getElementsByTagName('if_run_vdbench')[0].firstChild.nodeValue
    stress_type_param['if_run_vdbench'] = if_run_vdbench.encode('utf-8').split()[0]

    if_run_iozone = get_stress_type_params.getElementsByTagName('if_run_iozone')[0].firstChild.nodeValue
    stress_type_param['if_run_iozone'] = if_run_iozone.encode('utf-8').split()[0]

    if_run_mdtest = get_stress_type_params.getElementsByTagName('if_run_mdtest')[0].firstChild.nodeValue
    stress_type_param['if_run_mdtest'] = if_run_mdtest.encode('utf-8').split()[0]

    return stress_type_param
    

##############################################################################
# ##name  :      get_stress_type_param
# ##parameter:
# ##author:      lichengxu
# ##date  :      2019.02.28
# ##Description: 部署集群-业务子网的个数
##############################################################################
def get_svip_num_param():
    config_info = xml.dom.minidom.parse(S3_CONFIG_FILE)
    svip_num = config_info.getElementsByTagName('svip_num')[0]
    svip_num = int(svip_num.firstChild.nodeValue.encode('utf-8'))
    return svip_num


def get_third_package_path():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    third_package_path = config_info.getElementsByTagName('third_package_path')[0].firstChild.nodeValue
    return third_package_path


if __name__ == '__main__':
    # print get_s3_param()
    # print get_data_consistency_param()
    print get_nas_iozone_param()
    print get_posix_iozone_param()