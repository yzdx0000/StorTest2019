#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import json
import random
import warnings
import ConfigParser
import shell
import time
import subprocess
import commands
import log
import common
import common2
import ReliableTest
import breakdown
import get_config
import sys
import re
import random
import datetime
import decorator_func
from get_config import config_parser as CP

reload(sys)
sys.setdefaultencoding('utf-8')

__all__ = ['oSan']

# global CONF_FILE

conf_file = get_config.CONFIG_FILE
deploy_ips = get_config.get_env_ip_info(conf_file)  # 获取集群IP列表
client_ips = get_config.get_allclient_ip()  # 获取客户端IP

com2 = common2.oSan()
node = common.Node()
current_path=os.getcwd()
father_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class oSan():
    '''
    x1000相关操作
    create_
    create_access_zone
    create_storage_pool
    set_vip
    create_node_pool
    create_subnet
    add_vip_address_pool
    enable_san
    create_host_group
    add_host
    add_initiator
    add_nodes
    create_lun
    map_lun
    write_iqn
    delete_lun_map
    delete_lun
    remove_hosts
    remove_initiator
    shutdown

    os_reboot

    gen_dict
    get_node_pool_disks
    get_vip_address_pools
    discover_scsi
    iscsi_login
    iscsi_logout
    ls_scsi_dev
    get_nodes
    get_free_nodes
    get_storage_id
    get_subnet_id
    get_access_zone_id
    get_hosts
    get_host_groups
    get_lun
    get_lun_maps
    get_lun_maps_by_lunid
    get_iqn
    get_initiators
    get_option
    gen_vdb_xml
    get_targets
    run_vdb
    auto_gen_vdb_xml
    vdb_write

    update_access_zone

    install_Xstor
    uninstall_Xstor
    '''

    def __init__(self):
        pass

    @classmethod
    def install_Xstor(cls, s_ip, deploy_conf_file='/home/deploy/deploy_config.xml'):
        """
        安装Xstor,安装包和xml配置文件必须在/home/deploy目录下
        :param s_ip:
        :return:
        """

        log.info("Starting install Xstor...")
        cmd = (
                  "ssh %s \"/home/deploy/%s/deploy  --deploy_config=%s  --type=BLOCK\"") % (
                  s_ip, CP('xstor_package', 'pack_name'), deploy_conf_file)
        log.info(cmd)
        (rc, final) = commands.getstatusoutput(cmd)
        if 0 != rc:
            log.error(final)
            log.error("install Xstor failed!")
            exit(1)
        else:
            log.info(final)
            log.info("install Xstor  success")

        cmd = ("ssh root@{} '/home/parastor/bin/oSan   -v'".format(s_ip))
        res, output = commands.getstatusoutput(cmd)
        log.info("安装的xstor版本是{}".format(output))

    # @decorator_func.deco_uninstall_Xstor
    def uninstall_Xstor(self, s_ip, deploy_conf_file='/home/deploy/deploy_config.xml'):
        """
        卸载xstor
        :param s_ip:
        :param deploy_conf_file: 安装xstor的配置文件名字
        :return:
        """
        warnings.warn("this is a warn test", DeprecationWarning)
        log.info("\033[47m替换x1000.conf的包名为最新的包 ...\033[0m")
        cmd = ("ssh root@{} 'ls -t /home/deploy | grep -m1 'parastor.*.tar.xz''".format(s_ip))
        rc, info = commands.getstatusoutput(cmd)
        info = info[:-7]
        log.info(info)
        cmd_1 = (
            "sed -i 's/pack_name.*/pack_name={}/' {}/test_cases/cases/test_case/X1000/lun_manager/x1000.conf".format(
                info,father_path))
        log.info(cmd_1)
        res,final=commands.getstatusoutput(cmd_1)
        if res:
            log.error("替换x1000.conf包名失败!请检查x1000.conf的路径！！！")
            exit(1)

        log.info("\033[46m替换deploy文件:{}的包名为最新的包 ...\033[0m".format(deploy_conf_file))
        cmd = ("ssh root@%s \"sed -r -i 's/\/home\/deploy\/.*<\/package_path>/"
               "\/home\/deploy\/%s.tar.xz<\/package_path>/g' %s\"" % (
                   s_ip, CP('xstor_package', 'pack_name'), deploy_conf_file))
        commands.getstatusoutput(cmd)
        log.info("\033[46m开始解压xstor安装包...,包名:{}\033[0m".format(info))
        cmd1 = ("ssh root@{} 'cd /home/deploy;tar -xvf {}.tar.xz'".format(s_ip, CP('xstor_package', 'pack_name')))
        commands.getstatusoutput(cmd1)
        log.info("Starting uninstall Xstor...")
        cmd = (
                  "ssh %s \"/home/deploy/%s/server/tools/deployment/clean.py     --deploy_config=%s\"") % (
                  s_ip, CP('xstor_package', 'pack_name'), deploy_conf_file)
        log.info(cmd)
        (rc, final) = commands.getstatusoutput(cmd)
        if not rc:
            log.info("unistall Xstor  sucess")

    def update_param(self, s_ip=None, section=None, name=None, current=None):
        """
        更新参数
        :param s_ip:
        :param section (str): The section of this parameter, e.g. NAL,MGR,oPara,oStor,oApp,oCnas,CUSTOM
        :param name (str): The name of this parameter
        :param current (str):  Current value of this parameter
        :return:
        """
        if None == s_ip:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip)")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"pscli --command=update_param --section=%s --name=%s --current=%s\" " % (
                s_ip, section, name, current))

            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update_param error.")
                exit(1)
            else:
                log.info("update_param sucess")

    def update_lun(self, s_ip, lun_id, lun_name=None, qos_op=None, total_bytes=None, max_throughput=None,
                   max_iops=None,
                   need_judge=None):
        """
        更新lun
        :param s_ip:
        :param lun_id:
        :param lun_name:
        :param qos_op:
        :param total_bytes:
        :param max_throughput:
        :param max_iops:
        :param need_judge:
        :return:
        """

        init_cmd = 'pscli   --command=update_lun --id={}'.format(lun_id)
        print init_cmd
        if lun_name:
            init_cmd = '%s --name=%s' % (init_cmd, lun_name)
        if total_bytes:
            init_cmd = "%s  --total_bytes=%s" % (init_cmd, total_bytes)
        if qos_op:
            init_cmd = "%s --qos_op=%s" % (init_cmd, qos_op)
        if max_throughput:
            max_throughput = int(max_throughput / 512)  # 521为字节和sector的换算
            init_cmd = "%s --max_throughput=%s" % (init_cmd, max_throughput)
        if max_iops:
            init_cmd = "%s --max_iops=%s " % (init_cmd, max_iops)
        cmd = (
            "timeout 300 ssh {} \"{} \" ".format(s_ip, init_cmd))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            if need_judge:
                result = json.loads(final)
                return (result['err_msg'])
            else:
                log.error("update_lun error.")
                log.info(final)
                os._exit(1)
        else:
            log.info("update_lun success")
            # final = json.loads(final)
            # return final['result'][-1]

    def startup(self, s_ip=None):
        """
        启动系统
        :param s_ip:服务节点ip
        :return:
        """
        if None == s_ip:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip)")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=startup\" " % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("startup error.")
                exit(1)
            else:
                log.info("startup sucess")

    def shutdown(self, s_ip=None):
        """
        启动系统
        :param s_ip:服务节点ip
        :return:
        """
        if None == s_ip:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip)")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=shutdown\" " % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("shutdown error.")
                exit(1)
            else:
                log.info("shutdown sucess")

    def disable_san(self, s_ip, access_zone_id, protocol_types=None, stop_server=None, force=None,
                    needjudge=None):
        if not all([access_zone_id, s_ip]):
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip) and access_zone_id(The access zone id to enable san.)  ")
            exit(1)
        init_cmd = "pscli   --command=disable_san --access_zone_id={}".format(access_zone_id)
        if protocol_types:
            init_cmd = "{}  --protocol_types={}".format(init_cmd, protocol_types)
        if stop_server:
            init_cmd = "{} --stop_server={}".format(init_cmd, stop_server)
        if force:
            init_cmd = "{}  --force={}".format(init_cmd, force)
        cmd = ("ssh {} \"{}\" ".format(s_ip, init_cmd))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res != 0:
            if needjudge:
                result = json.loads(final)
                log.error(result['detail_err_msg'])
                return result['detail_err_msg']
            else:
                log.error(final)
                log.error("disable san on access_zone_id:%s error." % (str(access_zone_id)))
                exit(1)
        else:
            log.info("disable san on access_zone_id:%s success." % (str(access_zone_id)))

    def enable_san(self, s_ip=None, access_zone_id=None, needjudge=None):
        """
        启动san
        :param s_ip:
        :param access_zone_id (int): The access zone id to enable san.
        :return:
        """
        if not all([access_zone_id, s_ip]):
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip) and access_zone_id(The access zone id to enable san.)  ")
            exit(1)
        else:
            cmd = ("pscli --command=enable_san --access_zone_id=%s " % access_zone_id)
            log.info(cmd)
            (res, final) = com2.run_pscli_cmd(cmd, time_out=300, times=1)
            if res != 0:
                if needjudge:
                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                    return result['detail_err_msg']
                else:
                    log.error(final)
                    log.error("Enable san on access_zone_id:%s error." % (str(access_zone_id)))
                    exit(1)
            else:
                log.info("Enable san on access_zone_id:%s success." % (str(access_zone_id)))

    #########################Config_Pasesr实例化#######################

    ###########################    查询相关操作    ####################
    def add_nodes(self, s_ip=None, conf_file=None, err=True):
        """

        :param s_ip:
        :param config_file:
        :return:
        """
        if all([s_ip]):
            cmd = (
                "ssh {} \" pscli --command=add_nodes --config_file={} \"".format(
                    s_ip, conf_file))
            log.info(cmd)
            (res, prefix) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(prefix)
                log.error("add node error.")
                if err:
                    os._exit(1)
                else:
                    return False
            else:
                log.info("add node success.")
                return json.loads(prefix)
                # nal = json.loads(prefix)
                # return nal['result'][-1]

    # @classmethod
    def get_option(*args, **kwargs):
        """
         Xstor的查询操作(主要是对pscli查询的返回值进行取值操作)
        :param  kwargs['s_ip']: 服务器节点ip
        :param kwargs['command']:   要查询的命令
        :param kwargs ['indexname'] :json文件的节点
        :param kwargs['argv']:要查询的属性
        :return:
        """
        warnings.warn("Replace this function with get_option_single", DeprecationWarning)
        result = []
        if None == kwargs['s_ip']:
            pass
            exit(1)
        else:
            cmd = ("ssh {} \"pscli --command={}\"".format(kwargs['s_ip'], kwargs['command']))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                pass
                exit(1)
            else:
                final = json.loads(final)
                # print final
                final = final['result']
                for i in range(0, final['total']):
                    result.append(final['%s' % (kwargs['indexname'])][i]['%s' % (kwargs['argv'])])
            # result=",".join(result)
            log.info(result)
            return result

    def get_option_single(*args, **kwargs):
        """
         Xstor的查询操作(主要是对pscli查询的返回值进行取值操作)
        :param  kwargs['s_ip']: 服务器节点ip
        :param kwargs['command']:   要查询的命令
        :param kwargs ['indexname'] :json文件的节点
        :param kwargs['argv']:要查询的属性
        :return:
        """

        result = []
        if None == kwargs['s_ip']:
            pass
            exit(1)
        else:
            cmd = (
                "ssh {} \"pscli --command={} --{}={}\"".format(kwargs['s_ip'], kwargs['command'], kwargs["ids"],
                                                               kwargs["argv1"]))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                pass
                exit(1)
            else:
                final = json.loads(final)
                final = final['result']
                result = (final['%s' % kwargs['indexname']][-1]['%s' % (kwargs['argv2'])])
            # log.info(result)
            return result

    def gen_dict(*args, **kwargs):
        """
        根据arg2查询arg1，并返回arg1的值
        :param args:
        :param kwargs:比如arg1是name；arg2是id；target为name的值；arg3为json的index的属性；command为要查询的命令
        :return:
        """
        result = []
        if None == kwargs['s_ip']:
            pass
            exit(1)
        else:
            cmd = (
                "ssh {} \"pscli --command={}\"".format(kwargs['s_ip'], kwargs['command']))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                pass
                exit(1)
            else:
                final = json.loads(final)
                final = final['result']
                arg1 = kwargs['arg1']
                arg2 = kwargs['arg2']
                arg1 = []
                arg2 = []
                for i in range(0, final['total']):
                    arg1.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg1'])])
                    arg2.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg2'])])
                newdict = dict(zip(arg1, arg2))
                for k, v in newdict.items():
                    if k == '{}'.format(kwargs['target']):
                        result = v
                        break

            return result

    def gen_dict1(*args, **kwargs):
        """
        根据lun名，获取对应lun_map id
        :param args:
        :param kwargs:比如arg1是name；arg2是id；target为name的值；arg3为json的index的属性；command为要查询的命令
        :return:
        """
        if None == kwargs['s_ip']:
            pass
            exit(1)
        else:
            cmd = (
                "ssh {} \"pscli --command={}\"".format(kwargs['s_ip'], kwargs['command']))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                pass
                exit(1)
            else:
                final = json.loads(final)
                final = final['result']
                arg1 = kwargs['arg1']
                arg2 = kwargs['arg2']
                arg1 = []
                arg2 = []
                for i in range(0, final['total']):
                    arg1.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg1'])])
                    arg2.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg2'])])
                newdict = dict(zip(arg1, arg2))
                for k, v in newdict.items():
                    if k == kwargs['target']:
                        return v

    def gen_dict_mul(*args, **kwargs):
        """
        返回多个值（list）
        :param args:
        :param kwargs:比如arg1是name；arg2是id；target为name的值；arg3为json的index的属性；command为要查询的命令
        :return:
        """
        if None == kwargs['s_ip']:
            pass
            exit(1)
        else:
            cmd = (
                "ssh {} \"pscli --command={}\"".format(kwargs['s_ip'], kwargs['command']))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                pass
                exit(1)
            else:
                final = json.loads(final)
                final = final['result']
                arg1 = kwargs['arg1']
                arg2 = kwargs['arg2']
                arg1 = []
                arg2 = []
                for i in range(0, final['total']):
                    arg1.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg1'])])
                    arg2.append(final['{}'.format(kwargs['arg3'])][i]['{}'.format(kwargs['arg2'])])
                print arg1
                newdict = dict(zip(arg2, arg1))
                print newdict
                L = []
                for k, v in newdict.items():
                    if v == kwargs['target']:
                        L.append(k)
                return L

    ###########################    创建相关操作    ####################

    def create_node_pool(self, s_ip=None, node_ids=None, replica_num='3', stripe_width='3', disk_parity_num='0',
                         node_parity_num='2', name=None,need_judge=None):
        """
        Description：创建节点池

        :param s_ip:服务节点ip
        :param node_ids:
        :param replica_num:
        :param stripe_width:
        :param disk_parity_num:
        :param node_parity_num:
        :param name:
        :return:
        """
        if None == s_ip or None == node_ids or None == name:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip),node_id(string) and name(The name of node pool).")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"pscli --command=create_node_pool --node_ids=%s --replica_num=%s "
                    "--stripe_width=%s --disk_parity_num=%s --node_parity_num=%s --name=%s\"" % (
                        s_ip,
                        node_ids,
                        replica_num,
                        stripe_width,
                        disk_parity_num,
                        node_parity_num,
                        name))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                if need_judge:
                    result = json.loads(final)
                    return (result['err_msg'])
                else:
                    log.error(final)
                    log.error("create_node_pool error.")
                    exit(1)
            else:
                final = json.loads(final)
        return final['result']["node_pools"][0]['id']

    def create_access_zone(self, s_ip=None, node_id=None, name=None,need_judge=None):
        """
        创建访问区
        :param s_ip:
        :param node_id (str): The node id list in access zone, e.g. 1,2,3
        :param name (str): The name of access zone to create, e.g. AccessZone1
        :return:
        """
        if None == s_ip or None == node_id or None == name:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip),node_id(string) and name(accesee zone name).")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=create_access_zone --node_ids=%s --name=%s\"" % (s_ip, str(node_id), name))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                if need_judge:
                    result = json.loads(final)
                    return (result['err_msg'])
                else:
                    log.error(final)
                    log.error("Create access zone error.")
                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                    os._exit(1)
            else:
                final = json.loads(final)
        return final['result']

    # @decorator.deco_create_storage_pool
    def create_storage_pool(self, s_ip=None, name=None, node_pool_ids=None, disk_ids=None, needjudge=None):
        """
        创建存储池
        :param s_ip: 服务节点ip
        :param name (str): The name of storage pool.
        :param node_pool_ids (str): The node pool ID list of this storage pool. All the free disks in the node pool will be added.
        :param disk_ids (str): disk IDs of each disk, e.g. 1,2,3.
        :return:
        """
        if None == name or None == node_pool_ids or s_ip == None:
            log.error("I need storage name= and node_pool_ids=")
            exit(1)
        elif None == disk_ids:
            cmd = ("ssh %s \" pscli --command=create_storage_pool --type=BLOCK --name=%s --node_pool_ids=%s\"" % (
                s_ip, name, str(node_pool_ids)))
        else:
            cmd = (
                    "ssh %s \" pscli --command=create_storage_pool --disk_ids=%s --type=BLOCK --name=%s --node_pool_ids=%s\"" % (
                s_ip, str(disk_ids), name, str(node_pool_ids)))
        log.info(cmd)
        (res, prefix) = commands.getstatusoutput(cmd)
        if res != 0:
            result = json.loads(prefix)
            log.error(result)
            if needjudge:
                return result['detail_err_msg']
            else:
                os._exit(1)
        else:
            log.info("Create storage pool success.")
        prefix = json.loads(prefix)
        return prefix['result']['storage_pool_id']

    def expand_storage_pool(self, s_ip, storage_pool_id, node_pool_ids=None, disk_ids=None, shared_types=None,
                            need_judge=None):
        """
        Author:wangxiang
        Date:2018-12-19
        扩容存储池
        :param s_ip:
        :param storage_pool_id:
        :param node_pool_ids:
        :param disk_ids:
        :param shared_types:
        :param needjudge:
        :return:
        """
        if not all([s_ip, storage_pool_id, disk_ids]):
            log.error("get error  arg!")
            exit(1)
        init_cmd = "pscli   --command=expand_storage_pool  --storage_pool_id={} --disk_ids={}".format(storage_pool_id,
                                                                                                      disk_ids)
        if node_pool_ids:
            init_cmd = "{}  --node_pool_ids={}".format(init_cmd, node_pool_ids)
        if shared_types:
            init_cmd = "{}  --shared_types={}".format(init_cmd, shared_types)

        cmd = "ssh {} \"{}\"".format(s_ip, init_cmd)
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:
            log.info("expand storage_pool sucess")
            # final = json.loads(final)
            # return final
        else:
            if need_judge:
                result = json.loads(final)
                return (result['err_msg'])
            else:
                log.info(final)
                os._exit(1)

    def set_vip(self, s_ip=None, v_ip=None):
        '''
        date    :   2018-05-29
        Description :   设置vip
        param   :   s_ip : iscsi服务端IP
        return  :   vip
        '''
        if None == s_ip:
            log.error("I need s_ip=server ip to set svip,or s_ip=server ip,v_ip=virtual ip to set virtual ip")
            exit(1)
        cmd = ("echo %s | sed -r 's/(.*)(.[0-9]+)/\\1/g'" % (s_ip))
        (res, prefix) = commands.getstatusoutput(cmd)
        for i in range(200, 254):
            test_ip = ("%s.%d" % (prefix, i))
            if test_ip == v_ip:
                continue
            cmd = ("ping -c 1 %s >& /dev/null" % (test_ip))
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                return test_ip
            if i == 253:
                log.error("Sorry,I can not find the ip you can use.")
                exit(1)

    def create_subnet(self, s_ip=None, sv_ip=None, access_zone_id="1", name="subnet1", mask=None, vv_ip=None,
                      gate_way=None, network_interface=None, deploy=None):
        '''
        date    :   2018-05-29
        Description :   创建subnet
        param   :   s_ip : iscsi服务端IP
        return  :   subnet ID
        '''
        if deploy:
            sv_ip = get_config.get_svip(conf_file)[0]
        if None == s_ip or None == sv_ip:
            log.error(
                "I need s_ip=server ip,sv_ip=svip at least,access_zone_id default value is 1,name default value is subnet1")
            os._exit(1)
        log.info("Get_network_interface")
        cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)/\\1/g'" % (sv_ip))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        prefix = final.strip("[|]|u")
        log.info("Get gateway.")
        gate_way = prefix + '.254'
        cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 7 | uniq\"" % (s_ip, prefix))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            log.error("Get_network_interface error.")
        else:
            if len(final) == 0:
                cmd = ("echo %s | sed -r 's/(.*)(\.[0-9]+)(\.[0-9]+)/\\1/g'" % (sv_ip))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
                prefix = final.strip("[|]|u")
                cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 7 | uniq\"" % (s_ip, prefix))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
            log.info("network_interface: %s" % (final))
            network_interface_ls = final.split('\n')
            if len(network_interface_ls) > 1:
                network_interface = ','.join(network_interface_ls)
            else:
                network_interface = network_interface_ls[0]
        log.info("Get mask.")
        cmd = ("ssh %s \"ip addr | grep -w %s | sed -r 's/^ +//g' | cut -d ' ' -f 2 | sed -r 's/.*\///g' | uniq\"" % (
            s_ip, prefix))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if 0 != res:
            log.error("Get mask error.")
            os._exit(1)
        else:
            log.info("Get mask is : %s" % (final))
            mask = final
        cmd1 = (
                "ssh %s \"pscli --command=create_subnet --access_zone_id=%s --name=%s --svip=%s --subnet_mask=%s --subnet_gateway=%s --network_interfaces=%s --ip_family=IPv4\"" % (
            s_ip, str(access_zone_id), name, sv_ip, mask, gate_way, network_interface))
        cmd2 = (
                "ssh %s \"pscli --command=create_subnet --access_zone_id=%s --name=%s --svip=%s --subnet_mask=%s --subnet_gateway=%s --network_interfaces=%s\"" % (
            s_ip, str(access_zone_id), name, sv_ip, mask, gate_way, network_interface))
        log.info(cmd1)
        (res, final) = commands.getstatusoutput(cmd1)
        if 0 != res:
            log.error(final)
            log.error("Create_subnet error.")
            log.info(cmd2)
            (res, final) = commands.getstatusoutput(cmd2)
            if 0 != res:
                log.error(final)
                log.error("Create_subnet error.")
                os._exit(1)
            else:
                log.info("Create_subnet success.")
                final = json.loads(final)
                return final['result']
        else:
            log.info("Create_subnet success.")
            final = json.loads(final)
            return final['result']

    def add_vip_address_pool(self, subnet_id, s_ip,deploy=None,vip=None, domain_name=None, supported_protocol='ISCSI',
                              allocation_method='DYNAMIC', load_balance_policy=None,ip_failover_policy=None,rebalance_policy='RB_AUTOMATIC', need_judge=None):
        """
        add vip地址段
        :Author:wangxiang
        :Date:2019/3/21
        :param id: 子网id
        :param s_ip: 节点ip
        :param vip_addresses:
        :return: 默认返回新创建的vip_address_pood的id;在need_judge判断为True时,返回添加vip_address的错误提示信息,一般用于预期添加vip_address失败的case作为判断条件
        """
        if deploy:
            vip = get_config.get_vip(conf_file)[0]
        if not all([s_ip, subnet_id,domain_name,vip,supported_protocol,allocation_method]):
            log.error("get error  arg!")
            exit(1)
        init_cmd = "pscli   --command=add_vip_address_pool  --subnet_id={}  --domain_name={}  --vip_addresses={}".format(subnet_id,domain_name,vip)
        if load_balance_policy:
            init_cmd = "{} --load_balance_policy={}".format(init_cmd, load_balance_policy)
        if ip_failover_policy:
            init_cmd = "{}  --ip_failover_policy={}".format(init_cmd, ip_failover_policy)
        if rebalance_policy:
            init_cmd = "{}   --rebalance_policy={}".format(init_cmd, rebalance_policy)
        if supported_protocol:
            init_cmd = "{}   --supported_protocol={}".format(init_cmd, supported_protocol)
        if allocation_method:
            init_cmd = "{}   --allocation_method={}".format(init_cmd, allocation_method)

        cmd = "timeout 300 ssh {} \"{}\"".format(s_ip, init_cmd)
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if not res:
            log.info("add vip_address sucess")
            final = json.loads(final)
            return final['result']
        else:
            if need_judge:
                result = json.loads(final)
                return (result['err_msg'])
            else:
                log.info(final)
                os._exit(1)

    def update_vip_policy(self, s_ip=deploy_ips[0], ip_failover_policy=None, rebalance_policy=None, id=1):
        """
        :param ip_failover_policy:自动均衡策略设置,eg.[IF_ROUND_ROBIN, IF_CONNECTION_COUNT]
        :param rebalance_policy: 自动均衡开关设置,eg.[RB_DISABLED, RB_AUTOMATIC]
        :param id: The vip address pool id
        :return:None
        """
        if None == ip_failover_policy and None == rebalance_policy:
            log.error("param ip_failover_policy and rebalance_policy is None")
            os._exit(1)
        elif None != ip_failover_policy and None == rebalance_policy:
            cmd = ("ssh %s 'pscli --command=update_vip_address_pool --id=%d --ip_failover_policy=%s'"
                   % (s_ip, id, ip_failover_policy))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("pscli command run failed.info:%s" % stdout)
        elif None == ip_failover_policy and None != rebalance_policy:
            cmd = ("ssh %s 'pscli --command=update_vip_address_pool --id=%d --rebalance_policy=%s'"
                   % (s_ip, id, rebalance_policy))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("pscli command run failed.info:%s" % stdout)
        else:
            cmd = (
                    "ssh %s 'pscli --command=update_vip_address_pool --id=%d --ip_failover_policy=%s --rebalance_policy=%s'"
                    % (s_ip, id, ip_failover_policy, rebalance_policy))
            rc, stdout = commands.getstatusoutput(cmd)
            if rc != 0:
                log.error("pscli command run failed.info:%s" % stdout)
        log.info("Update vip policy successful!")

    def get_vip_policy(self, s_ip=None, vip_pool_id=1):
        """
        :param s_ip:集群一个节点IP
        :return:rebalance_policy:VIP均衡配置设置,ip_failover_policy:VIP均衡配置策略
        """
        if None == s_ip:
            log.error("the s_ip is None!")
            os._exit(1)
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                cmd = ("ssh %s 'pscli --command=get_vip_address_pools'" % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("pscli command run failed.info:%s" % stdout)
                else:
                    result = json.loads(stdout)
                    vip_info = result['result']['ip_address_pools'][vip_pool_id - 1]
                    rebalance_policy = vip_info['rebalance_policy']
                    ip_failover_policy = vip_info['ip_failover_policy']
                    log.info("VIP自动均衡策略: %s" % ip_failover_policy)
                    log.info("VIP自动均衡开关: %s" % rebalance_policy)
                    return rebalance_policy, ip_failover_policy

    def get_vips_by_pool(self, s_ip=None, vip_pool_id=None):
        """
        :Arthur:wuyuqiao
        :param s_ip: 集群一个节点IP
        :param vip_pool_id: 需要查询的vip_pool_id
        :return: 获取该vip池的所有vip，返回一个VIP列表
        """

        if None == s_ip or None == vip_pool_id:
            log.error("the params exist None.")
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                cmd = ("ssh %s 'pscli --command=get_vip_address_pools --ids=%s'" % (s_ip, str(vip_pool_id)))
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    result = json.loads(stdout)
                    vips = result['result']['ip_address_pools'][0]['vip_addresses'][0]
                    vip_list = []
                    if '-' in vips:
                        vip_tmp = vips.split('-')
                        vip_end = vip_tmp[1]
                        vip_begs = vip_tmp[0].split('.')
                        vip_beg = vip_begs[-1]
                        for count in range(int(vip_beg), int(vip_end) + 1):
                            each_vip = '.'.join(vip_begs[:-1]) + '.' + str(count)
                            vip_list.append(each_vip)
                    else:
                        vip_list = list(vips)
                    return vip_list

    def get_vip_pool_ids(self, s_ip=None):
        """
        :Arthur:wuyuqiao
        :param s_ip:集群一个节点IP
        :return: 所有vip_pool_id的列表,list
        """
        if None == s_ip:
            log.error("the s_ip is None!")
            os._exit(1)
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                cmd = ("ssh %s 'pscli --command=get_vip_address_pools'" % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("pscli command run failed.info:%s" % stdout)
                else:
                    result = json.loads(stdout)
                    vip_info = result['result']['ip_address_pools']
                    ip_pool_ids = []
                    for ip_pool in vip_info:
                        ip_pool_ids.append(ip_pool['id'])
                    return ip_pool_ids

    def get_vip_list(self, vips=None):
        """
        :functions:get vip list from config file
        :return: vip list
        """
        if None == vips:
            log.error("The param vips is None.")
        else:
            vip_list = []
            if '-' in vips:
                vip_tmp = vips.split('-')
                vip_end = vip_tmp[1]
                vip_begs = vip_tmp[0].split('.')
                vip_beg = vip_begs[-1]
                for count in range(int(vip_beg), int(vip_end) + 1):
                    each_vip = '.'.join(vip_begs[:-1]) + '.' + str(count)
                    vip_list.append(each_vip)
            else:
                vip_list = list(vips)
            return vip_list

    def get_vips_by_node(self, s_ip=None, vip_pool_id=None):
        """
        :Arthur:wuyuqiao
        :param s_ip: 集群一个节点IP
        :param vip_pool_id: 需要查询的vip_pool_id
        :return: 节点s_ip上的vip列表
        """

        if None == s_ip or None == vip_pool_id:
            log.error("the params exist None.")
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                vips = get_config.get_vip(conf_file)
                vip_list = self.get_vip_list(vips[0])
                cmd = ("ssh %s 'ip a' | grep 'inet ' | awk -F 'inet ' '{print $2}'" % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    ips_info = stdout.split('\n')
                    node_ips = []
                    for ip_info in ips_info:
                        ip = ip_info.split('/')[0]
                        node_ips.append(ip)
                    node_vips = []
                    for vip in vip_list:
                        if vip in node_ips:
                            node_vips.append(vip)
                    log.info(
                        "the vip pool id %s in node %s vips:%s" % (str(vip_pool_id), s_ip, ';'.join(node_vips)))
                    return node_vips

    def get_vips_by_node_dict(self, s_ip=None, vip_pool_id=None):
        """
        :Arthur:wangxiang
        :param s_ip: 集群一个节点IP，传入则返回该ip对应vip字典，不传则返回集群所有ip对应vip的列表
        :param vip_pool_id: 需要查询的vip_pool_id
        :return:
        """
        if s_ip:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                vips = get_config.get_vip(conf_file)
                vip_list = self.get_vip_list(vips[0])
                cmd = ("ssh %s 'ip a' | grep 'inet ' | awk -F 'inet ' '{print $2}'" % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    ips_info = stdout.split('\n')
                    node_ips = []
                    for ip_info in ips_info:
                        ip = ip_info.split('/')[0]
                        node_ips.append(ip)
                    s_ips=[]
                    node_vips = []
                    for vip in vip_list:
                        if vip in node_ips:
                            node_vips.append(vip)
                            s_ips.append(s_ip)
                    log.info(
                        "the vip pool id %s in node %s vips:%s" % (str(vip_pool_id), s_ip, ';'.join(node_vips)))
                    return dict(zip(node_vips,s_ips))
        else:
            dicts = []
            for s_ip in deploy_ips:
                print "##########################################"
                if False is ReliableTest.check_ping(s_ip):
                    log.error("the s_ip %s is not ping OK." % s_ip)
                    os._exit(1)
                else:
                    vips = get_config.get_vip(conf_file)
                    vip_list = self.get_vip_list(vips[0])
                    cmd = ("ssh %s 'ip a' | grep 'inet '" % s_ip)
                    rc, stdout = commands.getstatusoutput(cmd)
                    if 0 != rc:
                        log.error("pscli command run failed.info:%s" % stdout)
                        os._exit(1)
                    else:
                        # global s_ips,node_vips
                        ips_info = stdout.split('\n')
                        node_ips = []
                        for ip_info in ips_info:
                            ip = ip_info.split('/')[0]
                            node_ips.append(ip)
                        s_ips=[]
                        node_vips = []

                        for vip in vip_list:
                            if vip in node_ips:
                                node_vips.append(vip)
                                s_ips.append(s_ip)
                        if dict(zip(node_vips, s_ips)):
                            dicts.append(dict(zip(node_vips, s_ips)))
                        log.info(
                            "the vip pool id %s in node %s vips:%s" % (str(vip_pool_id), s_ip, ';'.join(node_vips)))
            return dicts


    def get_vips_by_eth(self, s_ip, vip_pool_id=None, eth_name=None):
        """
        :Arthur:wuyuqiao
        :param s_ip:集群一个节点IP
        :param vip_pool_id:节点的vip池ID
        :param eth_name:网卡名字
        :return:
        """
        if None == s_ip or None == vip_pool_id or eth_name == None:
            log.error("the params exist None.")
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                vips = get_config.get_vip(conf_file)
                vip_list = self.get_vip_list(vips[vip_pool_id-1])
                cmd = ("ssh %s 'ip a' | grep inet | grep %s | awk -F 'inet ' '{print $2}'" % (s_ip, eth_name))
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    ips_info = stdout.split('\n')
                    node_ips = []
                    for ip_info in ips_info:
                        ip = ip_info.split('/')[0]
                        node_ips.append(ip)
                    eth_vips = []
                    for vip in vip_list:
                        if vip in node_ips:
                            eth_vips.append(vip)
                    log.info(
                        "the vip pool id %s in node:%s eth:%s vips:%s" % (
                            str(vip_pool_id), s_ip, eth_name, ';'.join(eth_vips)))
                    return eth_vips

    def get_vips_layout(self, vip_pool_id=1):
        """
        :Arthur:wuyuqiao
        :return:system all vips layout
        """
        io_eth_list = []
        for node_ip in deploy_ips:
            if True is ReliableTest.check_ping(node_ip):
                cmd = ("timeout 10 ssh %s 'pscli --command=get_subnets'" % node_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("get subnets infomation failed.info:%s" % stdout)
                    continue
                else:
                    result = json.loads(stdout)
                    io_eth_list = result['result']['subnets'][0]['network_interfaces']
                    break
        for node_ip in deploy_ips:
            if True is ReliableTest.check_ping(node_ip):
                log.info("node %s vips layout:" % node_ip)
                for eth_name in io_eth_list:
                    self.get_vips_by_eth(node_ip, vip_pool_id, eth_name)
            else:
                log.info("node %s is down status." % node_ip)

    def get_losnr_by_node(self, s_ip=None):
        """
        :Arthur:wuyuqiao
        :param s_ip: 集群一个节点IP
        :return: 节点的los数量
        """
        if None == s_ip:
            log.error("the s_ip is None!")
            os._exit(1)
        else:
            if False is ReliableTest.check_ping(s_ip):
                log.error("the s_ip %s is not ping OK." % s_ip)
                os._exit(1)
            else:
                s_id = breakdown.disk().get_node_id_by_ip(n_ip=s_ip)
                cmd = ("ssh %s '/home/parastor/tools/nWatch -t oSan -i %s -c oSan#jnlins_dump' | grep lnodenr" % (
                    s_ip, str(s_id)))
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    lnode_info = stdout.split(',')
                    lnodenr_info = ''
                    for info in lnode_info:
                        if 'lnodenr' in info:
                            lnodenr_info = info
                    lnodenr_info_tmp = lnodenr_info.split(':')
                    lnodenr = lnodenr_info_tmp[1]
                    log.info("the los number in node %s is %s" % (s_ip, lnodenr))
                    return int(lnodenr)

    def get_target_by_vip(self, vip=None):
        """
        :param vip:集群中一个vip
        :return: 返回target的ID
        """
        if None == vip:
            log.error("the vip is None!")
            os._exit(1)
        else:
            for s_ip in deploy_ips:
                if False is ReliableTest.check_ping(s_ip):
                    continue
                else:
                    cmd = ("ssh %s 'pscli --command=get_targets'" % s_ip)
                    rc, stdout = commands.getstatusoutput(cmd)
                    if 0 != rc:
                        log.error("pscli command run failed.info:%s" % stdout)
                        os._exit(1)
                    else:
                        result = json.loads(stdout)
                        targets = result['result']['targets']
                        for target in targets:
                            if target['ipAddr'] == vip:
                                return target['id']

    def get_luns_by_vip(self, vip=None):
        """
        :fuc: get lun ids by associated vip
        :param s_ip: 集群IP
        :param vip: 集群中一个VIP
        :return:与该VIP关联的Lun的id列表
        """
        if None == vip:
            log.error("the param is None!")
            os._exit(1)
        else:
            for s_ip in deploy_ips:
                if False is ReliableTest.check_ping(s_ip):
                    continue
                else:
                    target_id = self.get_target_by_vip(vip)
                    cmd = ("ssh %s 'pscli --command=get_lun_maps'" % s_ip)
                    rc, stdout = commands.getstatusoutput(cmd)
                    if 0 != rc:
                        log.error("pscli command run failed.info:%s" % stdout)
                        os._exit(1)
                    else:
                        result = json.loads(stdout)
                        lun_maps = result['result']['lun_maps']
                        lun_ids = []
                        for lun_map in lun_maps:
                            if lun_map['target_id'] == target_id:
                                lun_ids.append(lun_map['lun_id'])
                        return lun_ids

    def split_vip(self, num=2):
        """
        :fuc:将配置文件中的VIP拆分成想要的几组,eg:10.1.1.1-10-> [10.1.1.1-5,10.1.1.6-10]
        :param num: 组数
        :return: VIP列表
        """
        vips = get_config.get_vip(conf_file)
        vips = vips[0]
        vip_max = int(vips.split('-')[1])
        vip_tmp = vips.split('-')[0]
        vip_min = int(vip_tmp.split('.')[-1])
        step = (vip_max - vip_min) / num
        vip_com = vip_tmp.split('.')[:-1]
        vip_com = '.'.join(vip_com)
        vip_result = []
        for count in range(num):
            if count + 1 == num:
                vip_end = vip_max
            else:
                vip_end = int(vip_min) + step
            vip = vip_com + '.' + str(vip_min) + '-' + str(vip_end)
            vip_result.append(vip)
            vip_min = int(vip_min) + step + 1
        return vip_result

    def check_lnode_state(self):
        """
        :funtion:check all nodes lnode status
        :return: if all lnode is ok ,return 0
                 else return 1
        """
        for s_ip in deploy_ips:
            if False is ReliableTest.check_ping(s_ip):
                continue
            else:
                master_oRole = None
                cmd = ('ssh %s "pscli --command=get_services"' % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    result = json.loads(stdout)
                    nodes = result['result']['nodes']
                    for node in nodes:
                        for service in node['services']:
                            if service['service_type'] == 'oRole' and service['inTimeStatus'] == 'SERV_STATE_OK':
                                master_oRole = service['node_id']
                count = 1
                while True:
                    log.info("the %d time(s) check lnode state..." % count)
                    cmd = ('ssh %s "/home/parastor/tools/nWatch -t oRole -i %s -c oRole#rolemgr_view_dump"'
                           % (s_ip, str(master_oRole)))
                    rc, stdout = commands.getstatusoutput(cmd)
                    if rc != 0:
                        log.error("pscli command run failed.info:%s" % stdout)
                        os._exit(1)
                    else:
                        result = stdout.split('\n')
                        info_list = result[:]
                        for line in result:
                            if 'jtype:3' not in line:
                                info_list.remove(line)
                            else:
                                break
                        stat_list = []
                        for line in info_list:
                            if 'node_stat' in line:
                                stat_list.append(line)

                        tag_list = stat_list[:]
                        for stat in stat_list:
                            if 'node_stat: 0' in stat:
                                log.info(stat)
                                tag_list.remove(stat)
                            else:
                                log.info("%s.Wait lnode state restore." % stat)
                        if len(tag_list) == 0:
                            log.info("all nodes status is OK.")
                            return 0
                        time.sleep(5)
                        count += 1


    def check_vip_state(self):
        """
        :fuction:traverse the system about vips status
        :return:if any vip's status is running,return 1,
                else if vip's status is completed,return 0;
        """
        for s_ip in deploy_ips:
            if False is ReliableTest.check_ping(s_ip):
                continue
            else:
                master_oRole = None
                cmd = ('ssh %s "pscli --command=get_services"' % s_ip)
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    os._exit(1)
                else:
                    result = json.loads(stdout)
                    nodes = result['result']['nodes']
                    for node in nodes:
                        for service in node['services']:
                            if service['service_type'] == 'oRole' and service['inTimeStatus'] == 'SERV_STATE_OK':
                                master_oRole = service['node_id']

                cmd = ('ssh %s "/home/parastor/tools/nWatch -t oRole -i %s -c oPmgr#pmgr_vip_ctxt_dump | grep addr"'
                       % (s_ip, str(master_oRole)))
                rc, stdout = commands.getstatusoutput(cmd)
                if 0 != rc:
                    log.error("pscli command run failed.info:%s" % stdout)
                    continue
                else:
                    result = stdout.split('\n')
                    for each_line in result:
                        if 'job:completed' not in each_line:
                            log.info("exist vip's status is running.\n%s" % each_line)
                            return 1
                    log.info("all vip's status is completed!")
                    return 0

    def lun_map_by_target(self, s_ip=None, lun_ids=None, target_id=None, hp_id=1):
        """
        :param s_ip:集群IP
        :param lun_id: lun id
        :param target_id: target id
        :return: none
        """
        if s_ip == None or lun_ids == None or target_id == None:
            log.error("the param is None!")
            os._exit(1)
        else:
            cmd = ("ssh %s 'pscli --command=map_luns_to_host_group --lun_ids=%s --host_group_id=%d --target_id=%d'"
                   % (s_ip, lun_ids, int(hp_id), int(target_id)))
            log.info(cmd)
            rc, stdout = commands.getstatusoutput(cmd)
            if 0 != rc:
                log.error("pscli command run failed.info:%s" % stdout)
                os._exit(1)
            else:
                log.info("lun map successful by target id: %s" % target_id)
                return 0

    def Qos_count(self, c_ip, s_ip, qos_arg='bandwidth'):
        """
        计算vdbench的logfile实时的带宽或者IOPS值
        :param s_ip: 执行vdbench的主机端IP
        :param qos_arg(str): 例如logfile.html的第三列代表IOPS，第四列代表带宽,传入的值为IOPS和bandwidth
        :return:
        """
        log.info(" 计算vdbench的logfile实时的带宽或者IOPS值 ...")
        decorator_func.timer(wait_time=120, interval=12)
        cmd = (" ssh %s \"cat /root/output/%s_nor/logfile.html\" " % (c_ip, s_ip))
        res, final = commands.getstatusoutput(cmd)
        log.info(cmd)
        new_list = []
        line_list = final.split('\n')
        log.info(len(line_list))
        lenth = len(line_list)
        for count in range(lenth):
            if 'rate' in line_list[count] and 'sys' in line_list[count]:
                for add in range(1, 31):
                    if count + add == lenth:
                        break
                    else:
                        new_list.append(line_list[count + add])
        data_list = []
        data_list2 = []
        log.info(len(new_list))
        if qos_arg == "bandwidth":
            for line in new_list:
                if line == '':
                    continue
                line_ls = line.split()
                if len(line_ls) < 2:
                    continue
                elif str(line_ls[1]).isdigit() == True:
                    data_list.append(line_ls[3])
                else:
                    continue
            sum = 0
            print data_list
            length = len(data_list)
            for count in range(1, 31):
                sum += float(data_list[length - count])
            avg_bandwidth = float(sum) / float(30)
            log.info(avg_bandwidth * 1024 ** 2)
            return avg_bandwidth * 1024 ** 2
        elif qos_arg == 'iops':
            for line in new_list:
                if line == '':
                    continue
                line_ls = line.split()
                if len(line_ls) < 2:
                    continue
                elif str(line_ls[1]).isdigit() == True:
                    data_list.append(line_ls[2])
                else:
                    continue
            sum = 0
            print data_list
            length = len(data_list)
            for count in range(1, 31):
                sum += float(data_list[length - count])
            avg_iops = float(sum) / float(30)
            log.info(avg_iops)
            return avg_iops
        elif qos_arg == 'all':
            for line in new_list:
                if line == '':
                    continue
                line_ls = line.split()
                if len(line_ls) < 2:
                    continue
                elif str(line_ls[1]).isdigit() == True:
                    data_list.append(line_ls[2])
                    data_list2.append(line_ls[3])
                else:
                    continue
            sum = 0
            sum2 = 0
            log.info(data_list)
            log.info(data_list2)
            length = len(data_list)
            length2 = len(data_list2)
            for count in range(1, 31):
                sum += float(data_list[length - count])
            avg_iops = float(sum) / float(30)
            for count in range(1, 31):
                sum2 += float(data_list2[length2 - count])
            avg_bandwidth = float(sum2) / float(30)
            log.info(avg_iops)
            log.info(avg_bandwidth * 1024 ** 2)
            return avg_iops, avg_bandwidth * 1024 ** 2

    def create_host_group(self, s_ip=None, hg_name=None, need_judge=None):
        '''
        date    :   2018-06-06
        Description :   创建主机组
        param   :   s_ip : 服务节点IP hg_name : 主机组名称
        return  :   host group ID
        '''
        if None == s_ip or None == hg_name:
            log.error("Please input server ip")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=create_host_group --name=%s\"" % (s_ip, str(hg_name)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Create host group: %s error." % (hg_name))
                if need_judge:
                    result = json.loads(final)
                    return result['detail_err_msg']
                else:
                    os._exit(1)
            else:
                log.info("Create host group: %s success." % (hg_name))
                final = json.loads(final)
                return final['result'][-1]

    def add_host(self, s_ip=None, h_name=None, hg_id=None,need_judge=1):
        '''
        date    :   2018-06-06
        Description :   创建主机组
        param   :   s_ip : 服务节点IP hg_name : 主机组名称
        return  :   host group ID
        '''
        if None == s_ip or None == h_name or None == hg_id:
            log.error("Please input server ip")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=add_host --name=%s --host_group_id=%s\"" % (s_ip, str(h_name), str(hg_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                if need_judge:
                    result = json.loads(final)
                    return result['detail_err_msg']
                else:
                    log.error("Create host:%s error." % (h_name))
                    exit(1)
            else:
                log.info("Create host: %s success." % (h_name))
                final = json.loads(final)
                return final['result'][-1]

    def add_initiator(self, s_ip=None, h_id=None, iqn=None, alias=None, auth_type="NONE", user=None, passwd=None):
        '''
        date    :   2018-06-06
        Description :   添加启动器
        param   :
        return  :
        '''
        if None == s_ip or None == h_id or None == iqn or None == alias:
            log.error("add_initiator:got wrong parameters.")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"pscli --command=add_initiator --iqn=%s --alias=%s --host_id=%s --auth_type=%s --chap_username=%s  --chap_password=%s\"" % (
                s_ip, iqn, alias, str(h_id), auth_type, user, passwd))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Add initiator error.")
                os._exit(1)
            else:
                log.info("Add initiator success.")
                final = json.loads(final)
                return final['result']

    # @decorator.deco_create_lun
    def create_lun(self, s_ip=None, lun_name=None, lun_type="THIN", stor_pool_id=None, acc_zone_id=None,
                   total_bytes="1073741824", max_throughput="900000", max_iops="200000",
                   stripe_width="3", disk_parity_num="0", node_parity_num="2", replica_num="3", need_judge=None):
        """
        创建lun
        :param s_ip(str): 服务节点ip
        :param lun_name(str): The name of the lun, e.g. lun_ex
        :param lun_type(int): Type of lun. Available type: ['THIN', 'THICK'] e.g. THIN
        :param stor_pool_id(int): Storage pool ID.
        :param acc_zone_id(int): access zone ID.
        :param total_bytes(int): max size of this lun
        :param max_throughput(str): Maximum throughput for QoS.
        :param max_iops(str): Maximum IOPS for QoS
        :param stripe_width(int): The stripe width.
        :param disk_parity_num(int): The disk parity number.
        :param node_parity_num(int): The node parity number.
        :param replica_num(int): The replica number.
        :return:
        """
        if None == s_ip or None == lun_name or None == stor_pool_id or None == acc_zone_id:
            log.error("Create lun:got wrong parameters.")
            os._exit(1)
        elif str(stor_pool_id) == "1":
            log.error("stor_pool_id can not set 1.")
            os._exit(1)
        else:
            cmd = (
                    "pscli --command=create_lun --name=%s --type=%s --storage_pool_id=%s --access_zone_id=%s --total_bytes=%s --max_throughput=%s --max_iops=%s --stripe_width=%s --disk_parity_num=%s --node_parity_num=%s --replica_num=%s" % (
                lun_name, lun_type, str(stor_pool_id), str(acc_zone_id),
                str(total_bytes), str(max_throughput), str(max_iops), str(stripe_width),
                str(disk_parity_num), str(node_parity_num), str(replica_num)))

            res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, s_ip=s_ip, times=1)
            # (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Create lun error.\ncmd:%s\nError infor:%s " % (cmd, final))
                if need_judge:
                    result = json.loads(final)
                    return (result['err_msg'])
                else:
                    os._exit(1)
            else:
                log.info("Create lun success.")
                final = json.loads(final)
                return final['result'][-1]

    def create_lun_para(self, s_ip=None, lun_name=None, lun_type="THIN", stor_pool_id=None, acc_zone_id=None,
                        total_bytes="99999999999", max_throughput="9000", max_iops="2000",
                        stripe_width="3", disk_parity_num="0", node_parity_num="0", replica_num="3"):
        """
        创建lun
        :param s_ip(str): 服务节点ip
        :param lun_name(str): The name of the lun, e.g. lun_ex
        :param lun_type(int): Type of lun. Available type: ['THIN', 'THICK'] e.g. THIN
        :param stor_pool_id(int): Storage pool ID.
        :param acc_zone_id(int): access zone ID.
        :param total_bytes(int): max size of this lun
        :param max_throughput(str): Maximum throughput for QoS.
        :param max_iops(str): Maximum IOPS for QoS
        :param stripe_width(int): The stripe width.
        :param disk_parity_num(int): The disk parity number.
        :param node_parity_num(int): The node parity number.
        :param replica_num(int): The replica number.
        :return:
        """
        if None == s_ip or None == lun_name or None == stor_pool_id or None == acc_zone_id:
            log.error("Create lun:got wrong parameters.")
            exit(1)
        elif str(stor_pool_id) == "1":
            log.error("stor_pool_id can not set 1.")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"pscli --command=create_lun --name=%s --type=%s --storage_pool_id=%s --access_zone_id=%s --total_bytes=%s --max_throughput=%s --max_iops=%s --stripe_width=%s --disk_parity_num=%s --node_parity_num=%s --replica_num=%s&\"" % (
                s_ip, lun_name, lun_type, str(stor_pool_id), str(acc_zone_id),
                str(total_bytes), str(max_throughput), str(max_iops), str(stripe_width),
                str(disk_parity_num), str(node_parity_num), str(replica_num)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Create lun error.")
                result = json.loads(final)
                log.error(result['err_msg'])
                os._exit(1)
            else:
                log.info("Create lun success.")
                final = json.loads(final)
                return final['result'][-1]

    def map_lun(self, s_ip=None, lun_ids=None, hg_id=None, target_id=None):
        '''
        date    :   2018-06-09
        Description ： map lun
        param   :   lun_ids : 卷ID  hg_id : 主机组ID
        return  :
        '''
        if None == s_ip or None == lun_ids or None == hg_id:
            log.error("Map lun:got wrong parameters.")
            exit(1)
        else:
            if target_id is None:
                cmd = ("pscli --command=map_luns_to_host_group --lun_ids=%s --host_group_id=%s" % (
                    str(lun_ids), str(hg_id)))
            else:
                cmd = ("pscli --command=map_luns_to_host_group --lun_ids=%s --host_group_id=%s --target_id=%s" % (
                    str(lun_ids), str(hg_id), target_id))
            log.info(cmd)
            res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, s_ip=s_ip, times=1)
            # (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Map lun error.")
                os._exit(1)
            else:
                final = json.loads(final)
                log.info("Map lun success. \n%s" % (final))
                return final['result'][-1]

    def write_iqn(self, cli_ip=None, iqn=None):
        '''
        date    :   2018-06-09
        Description ： write iqn
        param   :  cli_ip : 客户端IP iqn : iqn
        return  :   None
        '''
        if None == cli_ip or None == iqn:
            log.error("Write iqn:got wrong parameters.")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"echo InitiatorName=%s > /etc/iscsi/initiatorname.iscsi;sleep 5;service iscsid restart\"" % (
                cli_ip, str(iqn)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Write iqn error.")
                exit(1)
            else:
                log.info("Write iqn:{} success.".format(iqn))
                return iqn

    def update_iscsid_conf(self, cli_ip=None, CHAPTYPE='None', s_ip=None):
        """

        :param cli_ip: StorTest  IP
        :param CHAPTYPE:
        :param s_ip:   iscsi  client  IP
        :return:
        """
        if None == cli_ip or None == CHAPTYPE:
            log.error("Write iqn:got wrong parameters.")
            exit(1)
        else:
            cmd = (
                    "ssh %s \"scp  /home/StorTest/test_cases/cases/test_case/X1000/lun_manager/iscsid.conf_%s %s:/etc/iscsi/iscsid.conf;sleep7;service iscsid stop;service iscsid start\"" % (
                cli_ip, CHAPTYPE, s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("update iscsid.conf error.")
                exit(1)
            else:
                log.info("update iscsid.conf success.")

    def delete_lun_map(self, s_ip=None, map_id=None):
        '''
        date    :   2018-06-19
        Description ：
        param   :  s_ip : 服务节点IP map_id : map ID
        return  :   None
        ===================================
        修改加入timeout参数
        '''
        if None == s_ip or None == map_id:
            log.error("Write iqn:got wrong parameters.")
            os._exit(1)
        else:
            cmd = ("pscli --command=delete_lun_map --id=%s" % (str(map_id)))
            log.info(cmd)
            res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, s_ip=s_ip, times=1)
            # (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Delete map : %s error." % (str(map_id)))
                os._exit(1)
            else:
                log.info("Delete map : %s success." % (str(map_id)))

    def delete_lun(self, s_ip=None, lun_id=None, needjudge=None):
        """
        :param s_ip:
        :param lun_id:
        :param needjudge: needjudge不为None，删除lun失败不会退出，而是返回错误信息用于判断；needjudge为None，删除lun失败则会报错退出
        :return:
        ===================================
        修改加入timeout参数
        """
        if None == s_ip or None == lun_id:
            log.error("Write iqn:got wrong parameters.")
            exit(1)
        else:
            cmd = ("pscli --command=delete_lun --id=%s" % (str(lun_id)))
            res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, s_ip=s_ip, times=1)
            # (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error("Delete lun : %s error.res: %s \nInfo: %s." % (str(lun_id), res, final))
                if needjudge and "Killed" not in final:
                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                    return result['detail_err_msg']
                else:
                    log.info(final)
                    os._exit(1)
            else:
                log.info("Delete lun : %s success." % (str(lun_id)))

    def delete_node_pools(self, s_ip=None, node_pool_id=None, needjudge=None):
        '''
        date    :   2018-06-19
        Description ：
        param   :  s_ip : 服务节点IP id : lun ID
        return  :   None
        '''
        if None == s_ip or None == node_pool_id:
            log.error("Write iqn:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=delete_node_pools --ids=%s\"" % (s_ip, str(node_pool_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                if needjudge:
                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                    return result['detail_err_msg']
                else:
                    log.error("Delete node_pool : %s error." % (str(node_pool_id)))
                    exit(1)
            else:
                log.info("Delete node_pool : %s success." % (str(node_pool_id)))

    def remove_initiator(self, s_ip=None, ini_id=None):
        '''
        date    :   2018-07-02
        Description ：
        param   :  s_ip : 服务节点IP ini_id : initiator ID
        return  :   None
        '''
        if None == s_ip or None == ini_id:
            log.error("Remove intiator:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=remove_initiator --id=%s\"" % (s_ip, str(ini_id)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Remove initiator : %s error." % (str(ini_id)))
                result = json.loads(final)
                return result['detail_err_msg']
                exit(1)
            else:
                log.info("Remove initiator : %s success." % (str(ini_id)))

    def remove_node(self, s_ip=None, node_id=None):
        """
        :Author: wangxiang
		:Date :2018-08-07
        :Description:移除xstor集群节点
        :param s_ip(str): 执行节点的ip
        :param node_id(int): 要移除的节点id
        :return:

        change_log:

            ===================================================
            2018-08-07:
            change:wangxiang
            1.描述:创建
        """
        if None == s_ip or None == node_id:
            log.error("Remove intiator:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli   --command=remove_node   --id=%s\"" % (s_ip, node_id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Remove node : %s error." % (node_id))
                result = json.loads(final)
                log.info(result['detail_err_msg'])
                os._exit(1)
            else:
                log.info("Remove node : %s success." % (node_id))

    def cancel_remove_node(self, s_ip=None, node_id=None):
        """
        :Author: wangxiang
        :Date :2018-09-07
        :Description:取消移除xstor集群节点
        :param s_ip(str): 执行节点的ip
        :param node_id(int): 要移除的节点id
        :return:

        change_log:

            ===================================================
            2018-08-07:
            change:wangxiang
            1.描述:创建
        """
        if None == s_ip or None == node_id:
            log.error("Remove intiator:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli   --command=cancel_remove_nodes  --ids=%s\"" % (s_ip, node_id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Remove node : %s error." % (node_id))
                result = json.loads(final)
                log.info(result['detail_err_msg'])
                os._exit(1)

            else:
                log.info("Remove node : %s success." % (node_id))

    def remove_hosts(self, s_ip=None, id=None, need_judge=None):
        """

        :param s_ip (str):
        :param id (str):
        :return:
        """
        if None == s_ip or None == id:
            log.error("Remove hosts:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=remove_hosts --ids=%s\"" % (s_ip, id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                if need_judge:

                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                else:
                    log.error("Remove hosts : %s error." % (id))
                    os._exit(1)
            else:
                log.info("Remove hosts : %s success." % (id))

    def delete_host_groups(self, s_ip=None, id=None, need_judge=None):
        """

        :param s_ip (str):
        :param id (str):
        :return:
        """
        if None == s_ip or None == id:
            log.error("Remove hostgroup:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=delete_host_groups --ids=%s\"" % (s_ip, id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Remove hostgroup : %s error." % (id))
                if need_judge:
                    result = json.loads(final)
                    log.error(result['detail_err_msg'])
                else:
                    os._exit(1)
            else:
                log.info("Remove hostgroup : %s success." % (id))

    def delete_vip_address_pool(self, s_ip=None, id=None, need_judge=None):
        """

        :param s_ip (str):
        :param id (str):
        :return:
        """
        if None == s_ip or None == id:
            log.error("Remove hostgroup:got wrong parameters.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=delete_vip_address_pool --id=%s\"" % (s_ip, id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                if need_judge:
                    result = json.loads(final)
                    return result['err_msg']
                else:
                    log.error("Remove vip_address_pool : %s error." % (id))
                    os._exit(1)
            else:
                log.info("Remove vip_address_pool : %s success." % (id))

    def delete_subnet(self, s_ip=None, id=None, need_judge=None):
        if all([s_ip, id]):
            cmd = ("ssh {} \"pscli   --command=delete_subnet  --id={}\" ".format(s_ip, id))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                result = json.loads(final)
                if need_judge:
                    return (result['err_msg'])
                else:
                    log.error("delete_subnet error.")
                    os._exit(1)
            else:
                log.info("delete_subnet success")
        else:
            log.info("get error arg !")
            os._exit(1)

    def delete_access_zone(self, s_ip=None, azid=None, need_judge=None):
        """

        :param s_ip:
        :param azid:
        :param need_judge:
        :return:
        """
        if all([s_ip, id, ]):
            cmd = ("ssh {} \"pscli   --command=delete_access_zone  --id={}\" ".format(s_ip, azid))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                result = json.loads(final)
                if need_judge:
                    return (result['err_msg'])
                else:
                    log.error("delete_access_zone %s error." % (azid))
                    log.error(final)
                    os._exit(1)
            else:
                log.info("delete_access_zone %s success" % (azid))
        else:
            log.info("get error arg !")
            os._exit(1)

    def delete_storage_pool(self, s_ip=None, id=None, needjudge=None):
        """
        Author:wangxiang
        :param s_ip (str):
        :param id (str):
        :return:
        """
        last_disk_ids = []
        node_ids = []
        for aip in deploy_ips:
            node_id = breakdown.Os_Reliable().get_node_id_by_ip(aip)
            share_disk, data_disk = breakdown.Os_Reliable().get_share_monopoly_disk_ids(
                s_ip=aip,
                node_id=node_id)

            node_disk_ids = []
            for data_disk in data_disk:
                disk_id = breakdown.disk().get_diskid_by_name(s_ip=aip,
                                                              node_id=node_id,
                                                              disk_name=data_disk)  # 集群中的磁盘id
                node_disk_ids.append(disk_id)
            storage_disk_ids = breakdown.disk().get_diskid_in_disk_pool(aip, id)
            last_disk_id = (
                list(set(node_disk_ids) & set(set([int(x) for x in storage_disk_ids['%s' % id]]))))
            node_ids.append(node_id)
            last_disk_ids.append(last_disk_id)

        dict_1 = dict(zip(node_ids, last_disk_ids))
        log.info(dict_1)

        cmd = ("ssh %s \" pscli --command=delete_storage_pool --id=%s\"" % (s_ip, id))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(final)
            if needjudge:
                result = json.loads(final)
                log.error(result['detail_err_msg'])
                return result['detail_err_msg']
            else:
                os._exit(1)

        for k, v in dict_1.items():
            for d_id in v:
                while True:
                    cmd2 = (
                            "ssh %s \" /home/parastor/tools/nWatch -t oStor -i %s -c oStor#disk_is_deleted -a \"diskid=%s\"\"" % (
                        s_ip, k, d_id))
                    log.info(cmd2)
                    print cmd2
                    (res, final) = commands.getstatusoutput(cmd2)
                    if final == 1:
                        break
                    break

    ###########################    获取信息相关操作    ####################

    def get_node_pool_disks(self, s_ip=None, ids=None, nodeid=1):
        '''
        date    :   2018-06-04
        Description :   获取节点池磁盘id
        param   :   ids : 节点池ID  nodeid : 节点ID
        return  :   list[diskid]
        '''
        disk_ids = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_free_disks_by_node_pool_id --ids=%s\"" % (s_ip, str(ids)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get node pool disk error.")
                exit(1)
            else:
                log.info("Get node pool disk success.")
            final = json.loads(final)
            finals = final['result']
            if len(finals) == 0:
                log.error("There is no disks.")
                exit(1)
            for i in range(0, len(finals[0]['children'])):
                if finals[0]['children'][i]['node_id'] == int(nodeid):
                    for j in range(0, len(finals[0]['children'][i]['children'])):
                        disk_ids.append(finals[0]['children'][i]['children'][j]['id'])
        if len(disk_ids) != 0:
            return disk_ids
        else:
            log.error("Found no disks.Maybe you put a wrong node id.")
            exit(1)

    def get_vip_address_pools(self, s_ip=None, n_id="1"):
        '''
        date    :   2018-05-15
        Description :   获取VIP
        param   :   s_ip : iscsi服务端IP;n_id : 节点ID
        return  :   VIP
        '''
        vip_list = []
        if None == s_ip:
            log.error("Got wrong server_ip: %s" % (s_ip))
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_vip_address_pools --ids=%s\"" % (s_ip, str(n_id)))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("Get_vip_address_pools error.")
            # exit(1)
        else:
            log.info("Get_vip_address_pools success.")
        final = json.loads(final)
        if final['result']['total'] == 0:
            pass
            # exit(1)
        else:
            finals = final['result']['ip_address_pools']
            for vip in finals:
                print vip
                vip_list.append(vip['vip_addresses'])
        return vip_list

    def get_map_target(self, s_ip):
        """
        :Auther: Liuhe
        :Description:通过lun map拿到vip对应的target
        :return: target 列表
        """
        cmd = ("ssh %s \"pscli --command=get_lun_maps\"" % (s_ip))
        rc, stdout = commands.getstatusoutput(cmd)
        if rc != 0:
            log.error("failed get lun maps")
        else:
            stdout = json.loads(stdout)
            map_infos = stdout["result"]["lun_maps"]
            targets = []
            for i in range(len(map_infos)):
                target_id = map_infos[i]["target_id"]
                # lun_id = map_infos[i]["lun_id"]
                cmd = ("ssh %s \"pscli --command=get_targets\"" % (s_ip))
                rc, final = commands.getstatusoutput(cmd)
                if rc != 0:
                    log.error("failed get lun maps")
                else:
                    final = json.loads(final)
                    iqn_infos = final["result"]["targets"]
                    for i in range(len(iqn_infos)):
                        tar_id = final["result"]["targets"][i]["id"]
                        if tar_id == target_id:
                            iqn = final["result"]["targets"][i]["name"]
                            targets.append(iqn)
            return targets

    def discover_scsi_list(self, client_ip, svip):
        """
        :Auther: Liu he
        :Description: 获取SVIP下所有的target信息
        :param client_ip: 客户端IP
        :param svip: 存储SVIP地址
        :return: target列表
        """
        iqn_infos = []
        cmd = ("ssh %s \"iscsiadm -m discovery -t st -p %s 2>&1\"" % (client_ip, svip))
        log.info(cmd)
        (res, target) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(target)
            log.error("Get target on %s error.Error Infor:\n" % (svip))
            os._exit(1)
        else:
            log.info("Get target on %s success." % (svip))
            target = target.split("\n")
            for iqn in target:
                iqn_info = iqn.split(" ")[1]
                if "iqn" in iqn_info:
                    iqn_infos.append(iqn_info)
                else:
                    log.error("Get Error Info:%s" % (target))
                    os._exit(1)
            return iqn_infos

    def discover_scsi(self, client_ip, vip):
        '''
        date    :   2018-05-10
        Description :   发现iscsi服务器
        param   :   vip : VIP;client_ip : iscsi客户端IP
        return  :   target
        修改：在discovery中加入2>&1标准输出，规避discovery 提示timeout问题
        '''
        cmd = ("ssh %s \"iscsiadm -m discovery -t st -p %s 2>&1\"" % (client_ip, vip))
        log.info(cmd)
        (res, target) = commands.getstatusoutput(cmd)
        log.info("Get Target: %s " % (target))
        if res != 0:
            log.error(target)
            log.error("Get target on %s error." % vip)
            exit(1)
        else:
            target_info = target.split('\n')
            for info in target_info:
                if 'target' in info:
                    target = info
            log.info("Get target on %s success." % vip)
            target = target.split(" ")[1]
            return target

    def iscsi_login(self, client_ip, iqn):
        '''
        date    :   2018-05-14
        Description :   登录
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        '''
        cmd = ("ssh %s \"iscsiadm -m node -T %s -l\"" % (client_ip, iqn))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("Login on %s error." % (client_ip))
            exit(1)
        else:
            log.info("Login success on node %s." % (client_ip))

    def host_rescan(self, cli_ip):
        cmd = ("ssh %s \"iscsiadm -m session -R\"" % cli_ip)
        log.info(cmd)
        res, final = commands.getstatusoutput(cmd)

    def fdisk_func(self, client_ip):
        """

        :param client_ip:
        :return:
        """
        cmd = ("ssh %s \"fdisk  -l|grep  dev|wc -l\"" % (client_ip))
        (res, final) = commands.getstatusoutput(cmd)
        log.info(cmd)
        if res != 0:
            log.error(final)
            log.error("fdisk %s error." % (client_ip))
            exit(1)
        else:
            log.info("fdisk success on node %s." % (client_ip))
            return final

    def iscsi_logout(self, client_ip, vip=None):
        '''
        date    :   2018-05-14
        Description :   登出
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        '''
        cmd = ("ssh %s \"iscsiadm -m session |grep %s| cut -d ' ' -f 4\"" % (client_ip, vip))
        (res, final) = commands.getstatusoutput(cmd)
        final = final.split('\n')
        for i in final:
            # cmd = ("ssh %s \"iscsiadm -m node -T %s -u -p %s\"" % (client_ip, i,vip))
            cmd = ("ssh %s \"iscsiadm -m node -T %s -p %s -o delete;sleep 5;iscsiadm -m node -T %s -u -p %s\"" % (
                client_ip, i, vip, i, vip))
            (res, final) = commands.getstatusoutput(cmd)
            log.info(cmd)
            if res != 0:
                log.error(final)
                log.error("Logout on %s error." % (client_ip))
            else:
                log.info("Logout success on node %s." % (client_ip))

    def iscsi_logout_all(self, client_ip):
        '''
        date    :   2018-05-14
        Description :   登出
        param   :   client_ip : iscsi客户端IP;  iqn :   discover_scsi的返回值
        return  :   null
        ================================
        change: Liu he
            添加删除session 操作
        '''
        cmd1 = ("ssh %s \"iscsiadm -m node -u \"" % (client_ip))
        log.info(cmd1)
        res1,final1=commands.getstatusoutput(cmd1)
        log.info(final1)
        cmd2 = ("ssh %s \"iscsiadm -m node -o delete\"" % (client_ip))
        log.info(cmd2)
        res2, final2=commands.getstatusoutput(cmd2)

        log.info(final2)

        time.sleep(5)
        return

    def ls_scsi_dev(self, client_ip):
        '''
        date    :   2018-05-16
        Description :  获取scsi设备名
        param   :   client_ip   :   iscsi客户端IP;
        return  :   scsi 设备名列表
        change_log
        Author:wangxiang
        Des:更改了关于iscsi设备的判断
        '''
        cmd = ("ssh %s \"lsscsi | grep Xstor\" | awk '{print $NF}'" % (client_ip))
        (res, final) = commands.getstatusoutput(cmd)
        if res != 0:
            log.error(final)
            log.error("Get scsi devices on %s failed.Error info: \n%s" % (client_ip, final))
            exit(1)
        else:
            log.info("Get scsi devices on %s success. Get Xstor disk : \n%s " % (client_ip, final))
        scsis = []
        scsis = final.split('\n')
        if scsis == ['']:
            scsis = []
        if len(scsis) == 0:
            log.error("There is no scsi devices on %s." % (client_ip))
        log.info("From %s host get iscsi device list : %s" % (client_ip, scsis))
        return scsis

    def get_nodes(self, s_ip=None):
        '''
        date    :   2018-06-05
        Description :   获取节点ID
        param   :   s_ip : 服务节点IP
        return  :   节点ID
        '''
        nodeids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_nodes\"" % (s_ip))
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get nodes error.")
                # exit(1)
            else:
                log.info("Get nodes success.")
                final = json.loads(final)
                for i in range(0, len(final['result']['nodes'])):
                    nodeids.append(final['result']['nodes'][i]['data_disks'][0]['nodeId'])
                    # nodes_ids = (",".join('%s' % id for id in nodeids))
        return nodeids

    def get_storage_id(self, s_ip=None):
        '''
        date    :   2018-06-05
        Description :   获取存储池ID
        param   :   s_ip : 服务节点IP
        return  :   存储池ID
        '''
        storids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_storage_pools\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get storage error.")
                exit(1)
            else:
                log.info("Get storage success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    storids.append(final['result']['storage_pools'][i]['id'])
        return storids

    def get_storage__type_id(self, s_ip=None, type="BLOCK"):
        '''
        date    :   2018-08-23
        Description :   获取存储池ID(根据存储池类型筛选)
        param   :   s_ip : 服务节点IP
        return  :   存储池ID
        '''
        storids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_storage_pools\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get storage error.")
                exit(1)
            else:
                log.info("Get storage success.")
                final = json.loads(final)
                storids_list = final['result']['storage_pools']
                for storids in storids_list:
                    if storids['type'] == type:
                        return storids['id']
        return storids

    def get_subnet_id(self, s_ip=None):
        '''
        date    :   20.18-06-05
        Description :   获取subnet ID
        param   :
        return  :   subnet ID
        '''
        subnetids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_subnets\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get subnet error.")
                exit(1)
            else:
                log.info("Get subnet success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    subnetids.append(final['result']['subnets'][i]['id'])
        return subnetids

    def get_access_zone_id(self, s_ip=None):
        '''
        date    :   20.18-06-05
        Description :   获取访问区 ID
        param   :
        return  :   access_zone ID
        '''
        access_zone_ids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            os._exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_access_zones\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(final)
                log.error("Get access zone error.")
                os._exit(1)
            else:
                log.info("Get access zone success.")
                final = json.loads(final)
                for i in range(0, final['result']['total']):
                    access_zone_ids.append(final['result']['access_zones'][i]['id'])
        return access_zone_ids

    def get_hosts(self, s_ip=None):
        '''
        date    :   2018-06-06
        Description :   获取host ID
        param   ：
        return  :   hosts ID
        '''
        hostids = []
        if None == s_ip:
            log.error("Please input the corrent ip.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_hosts\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get hosts error.")
                exit(1)
            else:
                log.info("Get hosts success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    hostids.append(final['hosts'][i]['id'])
            return hostids

    def get_host_groups(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取host ID
        param   ：
        return  :   host_group ID
        '''
        hostgroupids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        else:
            cmd = ("ssh %s \" pscli --command=get_host_groups\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get host group error.")
                exit(1)
            else:
                log.info("Get host group success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    hostgroupids.append(final['host_groups'][i]['id'])
            return hostgroupids

    def get_luns_by_node_id(self, node_id=None, node_ip=deploy_ips[0]):
        if all([node_ip, node_id]):
            lunsid = []
            cmd = (
                        "ssh %s \"/home/parastor/tools/nWatch -t oSan -i %s -c oSan#get_lcache| grep '^LUN ID'\" | awk -F ': ' '{print $2}'" % (
                node_ip, node_id))
            log.info(cmd)
            rc, output = commands.getstatusoutput(cmd)
            for lun in output.split("\n"):
                lunsid.append(int(lun))
            return lunsid

    def get_lun(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取lun ID
        param   ：
        return  :   lun ID
        '''
        lunids = []
        cmd = ("pscli --command=get_luns")
        log.info(cmd)
        # (res, final) = commands.getstatusoutput(cmd)
        res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if (res != 0):
            log.error(final)
            log.error("Get luns error.")
            exit(1)
        else:
            log.info("Get luns success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunids.append(final['luns'][i]['id'])
        log.info("numbers of lun {}".format(len(lunids)))
        lunids.sort()
        return lunids

    def get_lun_maps(self, s_ip=None):
        '''
        date    :   2018-06-19
        Description :   获取lun map ID
        param   ：
        return  :   lun map ID
        '''
        lunmapids = []
        # if None == s_ip:
        #     log.error("Please input the correct ip.")
        #     exit(1)
        # else:
        cmd = ("pscli --command=get_lun_maps" )
        # log.info(cmd)
        # (res, final) = commands.getstatusoutput(cmd)
        res, final = com2.run_pscli_cmd(pscli_cmd=cmd, time_out=300, times=1)
        if (res != 0):
            log.error(final)
            log.error("Get lun maps error.")
            exit(1)
        else:
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunmapids.append(final['lun_maps'][i]['id'])
        lunmapids.sort()
        log.info("get lun map success.%s" % (lunmapids))
        return lunmapids

    def get_lun_maps_by_lunid(self, s_ip=None, lun_ids=None):
        '''
        date    :   2018-06-19
        Description :   获取lun map ID
        param   ：
        return  :   lun map ID
        '''
        lunmapids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        elif None == lun_ids:
            cmd = ("ssh %s \"pscli --command=get_lun_maps_by_lun_id \"" % (s_ip))
        else:
            cmd = ("ssh %s \"pscli --command=get_lun_maps_by_lun_id --lun_ids=%s\"" % (s_ip, str(lun_ids)))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if (res != 0):
            log.error(final)
            log.error("Get lun maps error.")
            exit(1)
        else:
            log.info("Get lun maps success.")
            final = json.loads(final)
            final = final['result']
            for i in range(0, final['total']):
                lunmapids.append(final['lun_maps'][i]['id'])
        return lunmapids

    def get_iqn(self, s_ip=None, ids=None):
        '''
        date    :   2018-06-09
        Description :   获取iqn
        param   ：
        return  :   iqn
        '''
        iqn_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        else:
            if None == ids:
                cmd = ("ssh %s \"pscli --command=get_initiators\"" % (s_ip))
            else:
                cmd = ("ssh %s \"pscli --command=get_initiators --ids=%s\"" % (s_ip, str(ids)))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get iqns error.")
                exit(1)
            else:
                log.info("Get iqns success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    iqn_ids.append(final['initiators'][i]['name'])
            return iqn_ids

    def get_initiators(self, s_ip=None):
        '''
        date    :   2018-06-09
        Description :   获取initiators ID
        param   ：
        return  :   initiators ID
        '''
        iqn_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_initiators\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get initiators ID error.")
                exit(1)
            else:
                log.info("Get initiators ID success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    iqn_ids.append(final['initiators'][i]['id'])
            return iqn_ids

    def get_targets(self, s_ip=None):
        '''
        date    :   2018-07-16
        Description :   获取target
        param   ：
        return  :   target ID
        '''
        target_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli --command=get_targets\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get targets ID error.")
                exit(1)
            else:
                log.info("Get targets ID success.")
                final = json.loads(final)
                final = final['result']
                for i in range(0, final['total']):
                    target_ids.append(final['targets'][i]['id'])
            return target_ids

    def get_free_nodes(self, s_ip=None):
        '''
        date    :   2018-07-16
        Description :   获取free_nodes
        param   ：
        return  :   free_nodes ID
        '''
        free_nodes_ids = []
        if None == s_ip:
            log.error("Please input the correct ip.")
            exit(1)
        else:
            cmd = ("ssh %s \"pscli   --command=get_free_nodes\"" % (s_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if (res != 0):
                log.error(final)
                log.error("Get free_nodes ID error.")
                exit(1)
            else:
                log.info("Get free_nodes ID success.")
                final = json.loads(final)
                final = final['result']
                final = final['nodes']
                lens = (len(final))
                for i in range(0, lens):
                    free_nodes_ids.append(final[i]['node_id'])
                    # free_nodes_ids = (",".join('%s' % id for id in free_nodes_ids))
            return free_nodes_ids

    ###########################    vdbench相关操作    ####################

    def gen_vdb_xml(self, max_range='100M', maxdata='1G', thread=8, offset=None, align=None, lun=None, xfersize=None,
                    rdpct=None, seekpct=None, interval=1):
        '''
        date    :   2018-05-17
        Description :   生成vdbench配置文件
        param   :  vdbench标准配置参数
        return  :   vdbench xml file path
        '''
        t1 = datetime.datetime.now()
        template_file = get_config.get_tools_path() + "/osan/template"  # 获取配置文件模板路径
        vdb_xml = get_config.get_tools_path() + "/osan/vdb_xml." + str(t1.microsecond)  # vdbench测试所用的文件
        sd_num = 1  # 初始化sd数量
        threads = []
        # vdb_path = get_config.get_vdbench_path()        #获取vdbench路径
        if True == os.path.exists(vdb_xml):
            cmd = ("rm -rf %s" % (vdb_xml))
            commands.getstatusoutput(cmd)
        cmd = ("cp %s %s" % (template_file, vdb_xml))
        commands.getstatusoutput(cmd)
        if None == lun or len(lun) == 0:
            log.error("Found no scsi devices.")
            exit(1)
        if None != offset:
            cmd = ("sed -i '1s/$/,offset=%s/g' %s" % (str(offset), vdb_xml))  # 修改前偏移量
            log.info("Modify vdb_xml cmd %s" % (cmd))
            commands.getstatusoutput(cmd)
        if None != align:
            cmd = ("sed -i '1s/$/,align=%s/g' %s" % (str(align), vdb_xml))  # 修改后偏移量
            log.info("Modify vdb_xml cmd %s" % (cmd))
            commands.getstatusoutput(cmd)
        if None != rdpct:
            cmd = ("sed -i '2s/$/,rdpct=%s/g' %s" % (str(rdpct), vdb_xml))  # 修改读写占比
            log.info("Modify vdb_xml cmd %s" % (cmd))
            commands.getstatusoutput(cmd)
        if None != seekpct:
            cmd = ("sed -i '2s/$/,seekpct=%s/g' %s" % (str(seekpct), vdb_xml))  # 修改读写占比
            log.info("Modify vdb_xml cmd %s" % (cmd))
            commands.getstatusoutput(cmd)
        if None != xfersize:
            cmd = ("sed -i -r 's/xfersizes.*?\)/xfersize=%s/g' %s" % (xfersize, vdb_xml))  # 修改xferrsize
            log.info("Modify vdb_xml cmd %s" % (cmd))
            commands.getstatusoutput(cmd)
        for dev_name in lun:
            sd_xml = ("sd=sd%d,lun=%s,range=(0,%s)" % (sd_num, dev_name, max_range))
            wd_xml = ("wd=wd%d,sd=sd%d" % (sd_num, sd_num))
            cmd = ("sed -i '%da\%s' %s" % (sd_num, sd_xml, vdb_xml))  # 插入rd
            commands.getstatusoutput(cmd)
            cmd = ("sed -i '$i\%s' %s" % (wd_xml, vdb_xml))  # 插入wd
            commands.getstatusoutput(cmd)
            sd_num = sd_num + 1
            # threads.append("10")
        # threads = "3"
        # maxdata = len(lun) * 9
        cmd = ("sed -i -r 's/thread.*?\)/threads=%s/g' %s" % (thread, vdb_xml))  # 修改每个wd的进程数
        commands.getstatusoutput(cmd)
        cmd = ("sed -i -r 's/interval.*?/interval=%s/g' %s" % (interval, vdb_xml))  # 修改每个wd的interval
        commands.getstatusoutput(cmd)
        cmd = ("sed -r -i 's/maxdata=[0-9]+[a-zA-Z]+,/maxdata=%s,/g' %s" % (str(maxdata), vdb_xml))  # 修改每个wd的maxdata
        commands.getstatusoutput(cmd)
        log.info(vdb_xml)
        return vdb_xml

    def run_vdb(self, client_ip, vdb_xml, jn_jro=None):
        '''
        date    :   2018-05-17
        Description :   运行vdbench
        param   :   client_ip:运行vdbench的客户端IP；vdb_xml:vdbench配置文件;jn_jro：vdbench校验开关
        return  :   None
        '''
        if vdb_xml == None:
            log.error("Please input vdb xml.")
            exit(1)
        vdb_path = get_config.get_vdbench_path()  # vdbench工具所在路径
        if None == jn_jro or jn_jro == "no":
            cmd = ("ssh %s 'echo %s/vdbench -f %s'" % (client_ip, vdb_path, vdb_xml))
            res, output = commands.getstatusoutput(cmd)
            if res != 0:
                log.error(output)
                log.error("Error! Run vdbench error.")
                exit(1)
            else:
                cmd = ("rm -rf %s" % (vdb_xml))
                commands.getstatusoutput(cmd)
                log.info("Vdbench log path is /root/output.")
        else:
            if False == os.path.exists("/root/vdbench/journal"):
                cmd = ("ssh %s 'mkdir -p /root/vdbench/journal'" % (client_ip))
                commands.getstatusoutput(cmd)
            cmd1 = ("ssh %s '%s/vdbench -f %s -jn'" % (client_ip, vdb_path, vdb_xml))
            cmd2 = ("ssh %s '%s/vdbench -f %s -jro'" % (client_ip, vdb_path, vdb_xml))
            res, output = commands.getstatusoutput(cmd1)
            if res != 0:
                log.error(output)
                log.error("Error! Run vdbench with journal verify error.Vdbench log path is /root/output.")
                exit(1)
            else:
                log.info("Vdbench log path is /root/output.")
                res, output = commands.getstatusoutput(cmd2)
                if res != 0:
                    log.error("Error! Vdbench check data error,journal path is /root/vdbench/journal.")
                    exit(1)
                else:
                    cmd = ("rm -rf %s" % (vdb_xml))
                    commands.getstatusoutput(cmd)
                    log.info("Vdbench check data success.")
                    cmd = ("ssh %s 'rm -rf /root/vdbench/journal/*'" % (client_ip))
                    commands.getstatusoutput(cmd)

    def auto_gen_vdb_xml(self, lun=None, thread=None):
        '''
        date    :   2018-05-22
        Description :   随机生成vdbench配置文件
        param   :  vdbench标准配置参数
        return  :   vdbench xml file path
        '''
        sd_num = 1
        wd_num = 1
        threads = []
        template_file = get_config.get_tools_path() + "/osan/auto_vdb"  # 获取配置文件模板路径
        template = open(template_file, "w+")
        sd_default = "sd=default,journal=/root/vdbench/journal,openflags=o_direct\n"
        template.write(sd_default)
        # Write sd.
        for dev_name in lun:
            offset = random.randint(0, 9999)
            align = random.randint(0, 9999)
            offset = offset - (offset % 512)
            align = align - (align % 512)
            sd = ("sd=sd%d,lun=%s,offset=%d,align=%d\n" % (sd_num, dev_name, offset, align))
            sd_num = sd_num + 1
            template.write(sd)
        # Write wd.
        for dev_name in lun:
            # 读写比例
            rdpct = random.randint(0, 100)
            # 随机比例
            seekpct = random.randint(0, 100)
            # 读写块大小
            xfer1 = random.randint(1, 9999)
            xfer2 = random.randint(1, 9999)
            xfer3 = random.randint(1, 9999)
            xfer4 = random.randint(1, 9999)
            # 读写百分比
            seed = 100
            xfer_pcnt1 = random.randint(1, (seed / 2))
            xfer_pcnt2 = random.randint(1, (100 - xfer_pcnt1) / 2)
            xfer_pcnt3 = random.randint(1, (100 - xfer_pcnt2) / 2)
            xfer_pcnt4 = 100 - xfer_pcnt1 - xfer_pcnt2 - xfer_pcnt3
            wd = ("wd=wd%d,sd=sd%d,xfersize=(%dk,%d,%dk,%d,%dk,%d,%dk,%d),rdpct=%d,seekpct=%d\n") % (wd_num, wd_num,
                                                                                                     xfer1, xfer_pcnt1,
                                                                                                     xfer2, xfer_pcnt2,
                                                                                                     xfer3, xfer_pcnt3,
                                                                                                     xfer4, xfer_pcnt4,
                                                                                                     rdpct, seekpct)
            wd_num = wd_num + 1
            template.write(wd)
        # 队列深度，默认为4
        for dev_name in lun:
            if None == thread:
                threads.append("4")
            else:
                threads.append(thread)
        threads = tuple(threads)
        rd = ("rd=run1,wd=wd*,iorate=max,elapsed=600,maxdata=500G,threads=%s,interval=1\n") % (
            re.sub("'| ", "", str(threads)))
        template.write(rd)
        template.close()
        return template_file

    def vdb_write(self, sd=None, lun=None, wd=None, offset=0, align=0, xfersize="4k", rdpct=0, seekpct=0, threads=4):
        t1 = datetime.datetime.now()
        write_file = get_config.get_tools_path() + "/osan/write_vdb." + str(t1.microsecond)  # 获取配置文件模板路径
        if "default" == sd:
            w_file = open(write_file, "w+")
            sd_default = ("sd=default,journal=/root/vdbench/journal,openflags=o_direct\n")
            w_file.write(sd_default)
            rd = ("rd=run1,wd=wd*,iorate=max,elapsed=600,maxdata=500G,interval=1\n")
            w_file.write(rd)
            w_file.close()
        elif None == lun or None == sd or None == wd:
            log.error("Got wrong parameter.")
            exit(1)
        else:
            w_file = open(write_file, "a+")
            sd_line = (
                    "sd=%s,lun=%s,offset=%s,align=%s,threads=%s\n" % (sd, lun, str(offset), str(align), str(threads)))
            wd_line = (
                    "wd=%s,sd=%s,xfersize=%s,rdpct=%s,seekpct=%s\n" % (wd, sd, str(xfersize), str(rdpct), str(seekpct)))
            w_file.write(sd_line)
            w_file.write(wd_line)
            w_file.close()
        cmd = ("sort %s -o %s;s=`grep rd= %s `;sed -r -i 's/rd=.*//g' %s;sed -r -i '$a\\'$s %s " % (
            write_file, write_file, write_file, write_file, write_file))
        # cmd = ("s=`grep rd= %s `;sed -r -i '$a\\'$s %s ;sed -r -i 's/rd=.*//1' %s" % (write_file, write_file, write_file))
        res, output = commands.getstatusoutput(cmd)
        return write_file

    def save_vdb_log(self, c_ip=None, f_name=None):
        '''
        date    :   2018-06-14
        Description :   保存vdbench的日志
        param   :  c_ip : 客户端IP  f_name : 保存的目标文件名
        return  :   None
        '''
        if None == c_ip:
            log.error("Please check your IP you input.")
            exit(1)
        else:
            cmd = ('ssh %s "[ -e /root/output/summary.html ]"' % (c_ip))
            res, output = commands.getstatusoutput(cmd)
            if res != 0:
                pass
            else:
                cmd = (
                        "ssh %s 'mkdir /root/vdb_summary 2> /dev/null;cp /root/output/summary.html /root/vdb_summary/%s;cp /root/output/parmfile.html /root/vdb_summary/%s.parm;rm -rf /root/output/'" % (
                    c_ip, f_name, f_name))
                res, output = commands.getstatusoutput(cmd)

    ###################################  update  ################################
    def update_vip_address_pool(self, vip_id, s_ip, vip_addresses=None, domain_name=None, load_balance_policy=None,
                                ip_failover_policy=None, rebalance_policy=None, need_judge=None):
        """
        更改vip地址段
        :Author:wangxiang
        :Date:2018/10/12
        :param id: vip地址段id
        :param s_ip: 节点ip
        :param vip_addresses:
        :return:
        """
        if not all([s_ip, vip_id]):
            log.error("get error  arg!")
            exit(1)
        init_cmd = "pscli    --command=update_vip_address_pool  --id={}".format(vip_id)
        if domain_name:
            init_cmd = "{}  --domain_name={}".format(init_cmd, domain_name)
        if vip_addresses:
            init_cmd = "{}  --vip_addresses={}".format(init_cmd, vip_addresses)
        if load_balance_policy:
            init_cmd = "{} --load_balance_policy={}".format(init_cmd, load_balance_policy)
        if ip_failover_policy:
            init_cmd = "{}  --ip_failover_policy={}".format(init_cmd, ip_failover_policy)
        if rebalance_policy:
            init_cmd = "{}   --rebalance_policy={}".format(init_cmd, rebalance_policy)

        cmd = "timeout 300 ssh {} \"{}\"".format(s_ip, init_cmd)
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:
            log.info("update vip_address sucess")
            # final = json.loads(final)
            # return final
        else:
            if need_judge:
                result = json.loads(final)
                return (result['err_msg'])
            else:
                log.info(final)
                os._exit(1)

    def update_access_zone(self, s_ip, access_zone_id, node_ids=None, auth_provider_id=None, isns_address=None, err=True):
        """
        更新访问分区
        :param s_ip:
        :param access_zone_id:
        :param node_ids:
        :param auth_provider_id:
        :param isns_address:
        :return:
        """
        if not all([s_ip, access_zone_id]):
            log.error("Got wrong parameters.")
            exit(1)
        else:
            init_cmd = "pscli --command=update_access_zone --id={}".format(access_zone_id)

            if node_ids:
                init_cmd = "{} --node_ids={}".format(init_cmd, node_ids)

            if auth_provider_id:
                init_cmd = "{} --auth_provider_id={}".format(init_cmd, auth_provider_id)

            if isns_address:
                init_cmd = "{} --isns_address={}".format(init_cmd, isns_address)

            cmd = ("timeout 300 ssh {} \"{}\"".format(s_ip, init_cmd))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update access zone error.")
                if err is True:
                    os._exit(1)
                else:
                    return False
            else:
                log.error("update access zone success")
                # final = json.loads(final)
                # return final['result']

    def update_host_group(self, s_ip, hg_id, name=None, need_judge=None):
        """

        :param s_ip:
        :param hg_id:
        :param name:
        :param need_judge:
        :return:
        """
        if not all([s_ip, hg_id]):
            log.error("Got wrong parameters.")
            exit(1)
        else:
            init_cmd = "pscli   --command=update_host_group  --host_group_id={}".format(hg_id)

            if name:
                init_cmd = "{} --name={}".format(init_cmd, name)

            cmd = ("ssh {} \"{}\"".format(s_ip, init_cmd))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update host_group error.")
                exit(1)
            else:
                log.error("update host_group success")
                # final = json.loads(final)
                # return final['result']

    def update_host(self, s_ip, h_id, name=None, need_judge=None):
        """

        :param s_ip:
        :param hg_id:
        :param name:
        :param need_judge:
        :return:
        """
        if not all([s_ip, h_id]):
            log.error("Got wrong parameters.")
            exit(1)
        else:
            init_cmd = "pscli   --command=update_host  --host_id={}".format(h_id)

            if name:
                init_cmd = "{} --name={}".format(init_cmd, name)

            cmd = ("ssh {} \"{}\"".format(s_ip, init_cmd))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update host error.")
                exit(1)
            else:
                log.error("update host success")
                # final = json.loads(final)
                # return final['result']

    def update_node_pool(self, s_ip, node_ids, node_pool_id, name="nodepool1", err=True):
        """
        更新节点池
        :Author:wangxiang
        :param s_ip: 节点ip
        :param node_ids : 节点id
        :param access_zone_id: 节点池id
        :return:
        """
        if not all([s_ip, node_pool_id, name, node_ids]):
            log.error("Got wrong parameters.")
            exit(1)
        else:
            cmd = (
                "ssh {} \"pscli   --command=update_node_pool  --node_pool_id={}  --name={}  --node_ids={}\"".format(
                    s_ip, node_pool_id, name, node_ids,
                ))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update nodepool error.")
                if err is True:
                    exit(1)
                else:
                    return False
            else:
                final = json.loads(final)
                return final['result']

    def update_initiator(self, s_ip, ini_id, alias=None, auth_type=None, user=None, passwd=None):
        if not all([s_ip, ini_id]):
            log.error("Got wrong parameters.")
            exit(1)
        else:
            init_cmd = "pscli   --command=update_initiator  --initiator_id={}".format(ini_id)

            if alias:
                init_cmd = "{} --alias={}".format(init_cmd, alias)

            if auth_type:
                init_cmd = "{} --auth_type={}".format(init_cmd, auth_type)

            if user:
                init_cmd = "{} --chap_username={}".format(init_cmd, user)

            if passwd:
                init_cmd = "{} --chap_password={}".format(init_cmd, passwd)

            cmd = ("ssh {} \"{}\"".format(s_ip, init_cmd))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                log.error("update initiator  error.")
                exit(1)
            else:
                log.info("update initiator sucess")
                # final = json.loads(final)
                # return final['result']

    def enable_iscisid(self, cli_ip=None):
        """
        设置iscisi服务开机自启动
        :param cli_ip: 主机端ip
        :return:
        """
        if all([cli_ip]):
            cmd = ("ssh %s \"systemctl enable iscsi\" " % (cli_ip))
            log.info(cmd)
            commands.getstatusoutput(cmd)
        else:
            log.info("get error  arg！")

    def os_reboot(self, cli_ip=None):
        """

        :param cli_ip:
        :return:
        """
        if None is cli_ip:
            log.error("Got wrong parameters.")
            log.error("I need s_ip(server ip)")
            exit(1)
        else:
            cmd = ("ssh %s \"reboot\" " % (cli_ip))
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if 0 != res:
                log.error(final)
                pass
            else:
                log.info("reboot success")

    def check_ping_ip(self, ip, new_ip_length=6, cli_ip=client_ips[0]):
        """
        Author:wangxiang
        ping可用的ip
        :param ip:  被ping的ip
        :param new_ip_length:  最终取得的新ip列表的长度
        :return: 返回的新的ip
        change:fix  subnet和新的vip冲突的情况
        """
        new_ip_list = []
        for i in random.sample(range(1, 253), new_ip_length + 10):
            new_ip = ip.split(".")[0] + "." + ip.split(".")[1] + "." + ip.split(".")[2] + "." + str(i)
            cmd = ("ssh %s \"ping {}  -c 4 -w 16\"".format(new_ip)) % cli_ip
            log.info(cmd)
            res, output = commands.getstatusoutput(cmd)
            if res and new_ip != ip:
                new_ip_list.append(new_ip)
                if len(new_ip_list) >= new_ip_length:
                    break

        new_ips = (",".join('%s' % i for i in new_ip_list))
        return new_ips

    def update_subnet(self, s_ip, subnet_id, svip=None, subnet_name=None, subnet_mask=None, subnet_gateway=None,
                      network_interfaces=None, mtu=None, need_judge=None):
        """
        Author:wangxiang
        :param s_ip:
        :param subnet_id:
        :param svip:
        :param subnet_name:
        :param subnet_mask:
        :param subnet_gateway:
        :param network_interfaces:
        :param mtu:
        :param need_judge:
        :return:
        """
        if not all([s_ip, subnet_id]):
            log.error("get error arg!")
            exit(1)
        else:
            init_cmd = "pscli   --command=update_subnet  --id={}".format(subnet_id)
            if subnet_name:
                init_cmd = "{}  --name={}".format(init_cmd, subnet_name)
            if svip:
                init_cmd = "{} --svip={}".format(init_cmd, svip)
            if subnet_mask:
                init_cmd = "{} --subnet_mask={}".format(init_cmd, subnet_mask)
            if subnet_gateway:
                init_cmd = "{}  --subnet_gateway={}".format(init_cmd, subnet_gateway)
            if network_interfaces:
                init_cmd = "{} --network_interfaces={}".format(init_cmd, network_interfaces)
            if mtu:
                init_cmd = "{}  --mtu={}".format(init_cmd, mtu)
            cmd = "ssh {}  \"{}\"".format(s_ip, init_cmd)
            log.info(cmd)
            (res, final) = commands.getstatusoutput(cmd)
            if res:
                if need_judge:
                    result = json.loads(final)
                    return result['err_msg']
                else:
                    log.error("update subnet fail")
                    os._exit(1)
            else:
                log.info("update subnet success.")
                final = json.loads(final)
                return final['result']
        time.sleep(30)

    def xstor_pre_config(self, s_ip, osan_space_check=1, is_display_raw_capacity=0,load_wave=0):
        """
        Author:wangxiang
        Date:2018-11-19
        安装完xstor的预配置函数：包括打开或关闭空间管理特性,是否显示存储池原始空间等
        :param s_ip:
        :param osan_space_check: 空间管理开关，0为打开,1为关闭  --对传参限制为0或1
        :param is_display_raw_capacity:存储池空间改成显示原始空间(0为不显示,1为显示)(该配置项现在已经不起作用；开发代码应该默认显示裸容量了)   --对传参限制为0或1
        :param load_wave:实时监控。这里1为打开；--对传参限制为数字
        :return:
        """
        node_ids_list = oSan().get_nodes(deploy_ips[0])  # 获取xstor系统中节点id的list

        log.info("##############开始完成xstor的预配置###########")

        if all([any([osan_space_check in (0, 1)]), any([is_display_raw_capacity in (0, 1)]),any([re.match('\d+', str(load_wave))])]):
            if osan_space_check:
                log.info("配置空间预留特性为关闭 ...")
            else:
                log.info("配置空间预留特性为打开 ...")
            for i in node_ids_list:
                cmd = (
                    "ssh {} \"/home/parastor/tools/nWatch   -t oSan -i {} -c oSan#osan_space_check -a 'disable={}'\"".format(
                        s_ip, i, osan_space_check))
                log.info(cmd)
                (res, final) = commands.getstatusoutput(cmd)
                if res:
                    log.info(final)
                    log.error("execute failed,please check!!!")
                    os._exit(1)
                else:
                    log.info("execute success")

            if is_display_raw_capacity:
                pass
            else:
                pass
            pass

            if load_wave:
                for ip in deploy_ips:
                    cmd = (
                        "ssh {} \"/home/parastor/tools/pscli_setparam.sh SYSTEM#loadwave_scan_enable={}\"".format(ip,load_wave))
                    log.info(cmd)
                    (res, final) = commands.getstatusoutput(cmd)
                    if res:
                        log.info(final)
                        log.error("execute failed,please check!!!")
                        os._exit(1)
                    else:
                        log.info("execute success")

        else:
            log.error("get error arg, please check !!!")
            exit(1)




    def reserve_wait(self, storage_pool_id=None, res_reserverd=0, get_reserverd=None, time_wait=None):
        """
        释放空间
        Author:wangxiang
        Date:20181206
        :param storage_pool_id: 存储池id
        :param res_reserverd:  预期的预留空间目标值
        :param get_reserverd:  释放单纯的只获取存储池预留空间大小，默认不获取
        :param time_wait：如果指定time_wait则以等待时间的方式来等待空间释放
        :return:
        """
        # fault_ip = breakdown.Os_Reliable().get_master_oRole(deploy_ips[0])  # 获取oPmgr主进程节点ip
        fault_ip = breakdown.Os_Reliable().get_master_orole2(deploy_ips[0])
        fault_id = common.Node().get_node_id_by_ip(fault_ip)
        cmd = (
                "ssh %s \"/home/parastor/tools/nWatch   -t oSan -i %s -c oSan#osan_space_check\"|awk -F : '{print $NF}'" % (
            deploy_ips[0], fault_id))
        log.info(cmd)
        (res, final) = commands.getstatusoutput(cmd)
        if res == 0:  # 判断打开了空间预留特性才执行之后的代码
            if time_wait:
                log.info("将会采用等待时间的方式等待空间释放,等待时间为{}s".format(time_wait))
                decorator_func.timer(time_wait)
                return
            if storage_pool_id:
                while True:
                    fault_ip = breakdown.Os_Reliable().get_master_orole2(deploy_ips[0])
                    fault_id = common.Node().get_node_id_by_ip(fault_ip)
                    cmd = (
                            "ssh %s \"/home/parastor/tools/nWatch  -t oRole  -i %s  -c oPmgr#pmgr_lunset_resv_dump\" | grep 'pool id : %d'|awk -F :  '{print$NF}'" % (
                        deploy_ips[0], fault_id, storage_pool_id))
                    res, final = commands.getstatusoutput(cmd)
                    log.info(cmd)
                    log.info(final)
                    if get_reserverd:
                        return int(final.strip())
                    else:
                        if int(final.strip()) == res_reserverd:
                            break
                        else:
                            decorator_func.timer(20)
            else:
                stor_pool_ids = oSan().get_storage_id(s_ip=deploy_ips[0])
                print stor_pool_ids
                if len(stor_pool_ids) >= 2:
                    stor_pool_ids.remove(1)  # 列表删除共享池
                    log.info(stor_pool_ids)
                for stor_id in stor_pool_ids:
                    while True:
                        cmd = (
                                "ssh %s \"/home/parastor/tools/nWatch  -t oRole  -i %s  -c oPmgr#pmgr_lunset_resv_dump\" | grep 'pool id : %d'|awk -F :  '{print$NF}'" % (
                            deploy_ips[0], fault_id, stor_id))
                        res, final = commands.getstatusoutput(cmd)
                        log.info(cmd)
                        log.info(final)
                        if get_reserverd:
                            return int(final.strip())
                        if int(final.strip()) == res_reserverd:
                            break
                        else:
                            log.info("Waiting for space to be released ")
                            decorator_func.timer(20)
