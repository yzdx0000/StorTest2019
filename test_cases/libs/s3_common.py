#!/usr/bin/python
# -*- encoding=utf8 -*-

#######################################################
# 脚本作者：鲍若冰
# 脚本说明：s3公共函数
#######################################################

from multiprocessing import Process
import time
import hmac
import base64
from hashlib import sha1
import xml.etree.ElementTree as Et

import log
import common
import get_config

S3_Port = "20480"

'''客户端节点ip'''
CLIENT_IP_1 = get_config.get_client_ip()


def get_ooss_node_ids():
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   获取oOss节点id
    :return:
    """
    rc, stdout = common.get_services()
    common.judge_rc(rc, 0, "get services failed!!!")
    stdout = common.json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    ooss_node_id_lst = []
    for node_info in node_info_lst:
        node_id = node_info['node_id']
        node_services_lst = node_info['services']
        for service_info in node_services_lst:
            if service_info['service_type'] == 'oOss':
                ooss_node_id_lst.append(node_id)
    return ooss_node_id_lst


def get_ooms_node_ids():
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   获取oOss节点id
    :return:
    """
    rc, stdout = common.get_services()
    common.judge_rc(rc, 0, "get services failed!!!")
    stdout = common.json_loads(stdout)
    node_info_lst = stdout['result']['nodes']
    ooms_node_id_lst = []
    for node_info in node_info_lst:
        node_id = node_info['node_id']
        node_services_lst = node_info['services']
        for service_info in node_services_lst:
            if service_info['service_type'] == 'oOms':
                ooms_node_id_lst.append(node_id)
    return ooms_node_id_lst


def get_ooss_node_ip():
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   获取一个oOss节点ip
    :return:
    """
    node_ooss_ip_lst = get_config.get_s3_access_ips()
    # node_ooss_ip_lst = get_config.get_vip_addresses()[-1].encode('utf-8').split(',')
    print("node_ooss_ip_lst is %s" % str(node_ooss_ip_lst))
    for ooss_ip in node_ooss_ip_lst:
        if common.check_ping(ooss_ip, num=1):
            return ooss_ip
    return None


def get_node_service_state(node_id, service_type):
    """
    :author:             baourobing
    :date:               2018.08.29
    :description:        获取一个节点的某个服务的状态
    :param node_id:      节点ip
    :param service_type: 服务类型
    :return:
    """
    rc, stdout = common.get_services(node_ids=node_id)
    if rc != 0:
        return rc, stdout
    service_info = common.json_loads(stdout)
    services_lst = service_info['result']['nodes'][0]['services']
    for service in services_lst:
        if service['service_type'] == service_type:
            service_state = service['inTimeStatus'].split('_')[-1]
            return rc, service_state
    return -1, None


def get_xml_tag_text(xml_str, tag):
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   从curl命令返回的xml字符串中找所有标签为tag的内容
    :param xml_str: (str)curl命令返回的xml字符串
    :param tag:     (str)标签名字
    :return:        (list)标签内容的list
    """
    root = Et.fromstring(xml_str)
    prefix_str = root.tag.split('}')[0] + '}'
    name_str = "%s%s" % (prefix_str, tag)
    name_lst = []
    for name in root.iter(name_str):
        name_lst.append(name.text)
    return name_lst


def retry_curl_cmd(func):
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   curl命令重试的装饰器
    :param func:    curl命令函数
    :return:
    """
    def inner(*args, **kwargs):
        if 'retry' in kwargs and kwargs['retry'] is True:
            i = 0
            while True:
                result = func(*args, **kwargs)
                if result[0] != 0:
                    if i == 15:
                        return result
                    else:
                        log.info("wait 10s, retry")
                        time.sleep(10)
                        i += 1
                        continue
                else:
                    return result
        else:
            return func(*args, **kwargs)
    return inner


def set_ooss_ip(func):
    """
    :author:        baourobing
    :date:          2018.12.19
    :description:   curl命令获取oossip的装饰器
    :param func:    curl命令函数
    :return:
    """
    def inner(*args, **kwargs):
        if 'ooss_ip' not in kwargs:
            kwargs['ooss_ip'] = get_ooss_node_ip()
        return func(*args, **kwargs)
    return inner


"""**************************************** 签名认证 ****************************************"""


def mk_sig(sk, stringtosign):
    """
    :author:              baourobing
    :date:                2018.08.29
    :description:         通过hmac算法计算sk的sig
    :param sk:            (str)sk
    :param stringtosign:  (str)原始消息message
    :return:
    """
    sig = hmac.new(str(sk), stringtosign.encode('utf-8'), sha1).digest()
    return sig


def mk_sig_code(sig):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 对sig进行base64编码
    :param sig:   (str)sig码
    :return:
    """
    base64sig = base64.b64encode(sig)
    return base64sig


def set_oss_http_auth(current):
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   修改s3签名认证的开关
    :param current: 1为打开, 0为关闭
    :return:
    """
    rc, stdout = common.update_param(section='oApp', name='oss_enable_http_auth', current=current)
    return rc, stdout


def add_account(name, email, quota):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 创建s3账户
    :param name:  (str)账户名字
    :param email: (str)邮箱
    :param quota: (int)配额，byte
    :return:
    """
    rc, stdout = common.add_account(account_name=name, account_email=email, account_quota=quota)
    if rc != 0:
        return rc, None
    else:
        stdout = common.json_loads(stdout)
        account_id = stdout['result']['account_id']
        return rc, account_id


def update_account(account_id, quota):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      更新s3账户
    :param account_id: (str)账户id
    :param quota:      (int)配额，byte
    :return:
    """
    rc, stdout = common.update_account(account_id=account_id, account_quota=quota)
    return rc, stdout


def del_account(account_id):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      删除s3账户
    :param account_id: 账户id
    :return:
    """
    rc, stdout = common.delete_account(account_id=account_id)
    return rc, stdout


def find_account(email):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 查找账户
    :param email: 账户邮箱
    :return:
    """
    rc, stdout = common.find_account(account_email=email)
    return rc, stdout


def get_account_id_by_email(email):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 根据邮箱获取账户id
    :param email: 账户邮箱
    :return:
    """
    rc, stdout = find_account(email)
    if rc != 0:
        return rc, None
    account_info = common.json_loads(stdout.strip())
    account_id = account_info['result']['account_id']
    return rc, account_id


def get_account_quote_by_email(email):
    """
    :author:      baourobing
    :date:        2018.08.29
    :description: 根据邮箱获取账户配额
    :param email: 账户邮箱
    :return:
    """
    rc, stdout = find_account(email)
    if rc != 0:
        return rc, None
    account_info = common.json_loads(stdout.strip())
    account_quota = account_info['result']['account_quota']
    return rc, account_quota

def get_account_storage(account_id):
    """
    :author:      zhanghan
    :date:        2018.12.24
    :description: 根据账户id获取账户容量信息
    :param account_id: 账户id
    :return:
    """
    rc, stdout = common.get_account(account_id)
    if rc != 0:
        return rc, None
    else:
        stdout = common.json_loads(stdout)
        account_storage_info = stdout['result']['used_bytes']
        return rc, account_storage_info



def add_certificate(account_id):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      创建s3证书
    :param account_id: (str)账户id
    :return:
    """
    rc, stdout = common.add_certificate(account_id=account_id)
    if rc != 0:
        return rc, None, None
    else:
        stdout = common.json_loads(stdout)
        certificate_id = stdout['result']['certificate_id']
        certificate = stdout['result']['secret_key']
        return rc, certificate_id, certificate


def update_certificate(certificate_id, state):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          更新s3证书
    :param certificate_id: 证书id
    :param state:          状态 eg.S3_CERTIFICATE_ENABLE S3_CERTIFICATE_DISABLE
    :return:
    """
    rc, stdout = common.update_certificate(certificate_id=certificate_id, state=state)
    return rc, stdout


def del_certificate(certificate_id):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          删除证书
    :param certificate_id: 证书id
    :return:
    """
    rc, stdout = common.delete_certificate(certificate_id=certificate_id)
    return rc, stdout


def get_certificate_by_accountid(account_id):
    """
    :author:           baourobing
    :date:             2018.08.29
    :description:      通过账户id获取所有证书id
    :param account_id: 账户id
    :return:
    """
    rc, stdout = common.list_certificates(account_id=account_id)
    if rc != 0:
        return rc, None
    else:
        certificates_info = common.json_loads(stdout)
        certificate_info_lst = certificates_info['result']['certificate_info']
        certificate_id_lst = []
        certificate_lst = []
        for certificate_info in certificate_info_lst:
            certificate_id = certificate_info['certificate_id']
            certificate = certificate_info['secret_key']
            certificate_id_lst.append(certificate_id)
            certificate_lst.append(certificate)
        return rc, certificate_id_lst, certificate_lst


def check_curl(output):
    """
    :author:       baourobing
    :date:         2018.08.29
    :description:  检查curl命令的输出
    :param output: (str)curl命令的输出
    :return:
    """
    '''
    line_lst = output.splitlines()
    for line in line_lst:
        if "HTTP/1.1" in line:
            result_code = ' '.join(line.split()[1:])
            if result_code == '200 OK':
                return True
            else:
                return False
    return False
    '''
    if '200 OK' in output:
        return True
    else:
        return False


@retry_curl_cmd
@set_ooss_ip
def add_bucket(bucket_name, certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          上传桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param exe_node_ip:    (str)执行命令的节点
    :return:
    """
    cmd = 'curl -s -i http://%s:%s/%s -X PUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def add_bucket_by_sk(bucket_name, certificate_id, certificate, complex=False, exe_node_ip=None, retry=False,
                     ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          通过SK上传桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id, AK
    :param certificate:    (str)证书, SK
    :param complex:        (bool)是否是复杂sk, 默认不复杂的
    :param exe_node_ip:    (str)执行命令的节点
    :return:
    """
    if complex is False:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"+bucket_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s -XPUT -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    else:
        stringtosign = ("PUT" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + ""
                        + "/" + bucket_name)
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s -XPUT -H "Date: Wed, 31 Jan 2018 14:37:09 GMT" -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def add_bucket_with_meta_by_sk(bucket_name, certificate_id, certificate, meta_num, complex=False,
                               exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.10.08
    :description:          通过SK上传带元数据的桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id, AK
    :param certificate:    (str)证书, SK
    :param complex:        (bool)是否是复杂sk, 默认不复杂的
    :param exe_node_ip:    (str)执行命令的节点
    :param meta_num:       (str)元数据的个数
    :return:
    """
    meta_cmd_str = ""
    for cmd_str in range(int(meta_num)):
        meta_cmd_str = meta_cmd_str + " "+'-H "x-amz-meta-key'+str(cmd_str)+':value'+str(cmd_str)+'"'

    meta_str_str = ""
    for str_str in range(int(meta_num)):
        if str_str == 0:
            meta_str_str = 'x-amz-meta-key' + str(str_str) + ':value' + str(str_str)
        else:
            meta_str_str = meta_str_str + "\n" + 'x-amz-meta-key'+str(str_str)+':value'+str(str_str)

    if complex is False:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + meta_str_str + "\n" + "/"+bucket_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s -XPUT ' % (ooss_ip, S3_Port, bucket_name) + meta_cmd_str +
               ' -H "Authorization: AWS %s:%s"' % (certificate_id, sig))
    else:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" \
                       + meta_str_str + "\n" + "/" + bucket_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s -XPUT -H "Date: Wed, 31 Jan 2018 14:37:09 GMT"'
               % (ooss_ip, S3_Port, bucket_name) + meta_cmd_str + ' -H "Authorization: AWS %s:%s"'
               % (certificate_id, sig))
    log.info("string:%s" % stringtosign)
    log.info("cmd:%s" % cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def add_object_with_meta_by_sk(bucket_name, object_name, filename, certificate_id, certificate, meta_num, complex=False,
                               exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.10.08
    :description:          通过SK上传带元数据的桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id, AK
    :param certificate:    (str)证书, SK
    :param complex:        (bool)是否是复杂sk, 默认不复杂的
    :param exe_node_ip:    (str)执行命令的节点
    :param meta_num:       (str)元数据的个数
    :return:
    """
    meta_cmd_str = ""
    for cmd_str in range(int(meta_num)):
        meta_cmd_str = meta_cmd_str + " "+'-H "x-amz-meta-key'+str(cmd_str)+':value'+str(cmd_str)+'"'

    meta_str_str = ""
    for str_str in range(int(meta_num)):
        if str_str == 0:
            meta_str_str = 'x-amz-meta-key' + str(str_str) + ':value' + str(str_str)
        else:
            meta_str_str = meta_str_str + "\n" + 'x-amz-meta-key'+str(str_str)+':value'+str(str_str)

    if complex is False:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + meta_str_str + "\n" + "/" + \
                       bucket_name+"/"+object_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s/%s -XPUT -T %s' % (ooss_ip, S3_Port, bucket_name, object_name, filename) +
               meta_cmd_str + ' -H "Authorization: AWS %s:%s"' % (certificate_id, sig))
    else:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" \
                       + meta_str_str + "\n" + "/" + bucket_name+"/"+object_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s/%s -XPUT -T %s -H "Date: Wed, 31 Jan 2018 14:37:09 GMT"'
               % (ooss_ip, S3_Port, bucket_name, object_name, filename) + meta_cmd_str +
               ' -H "Authorization: AWS %s:%s"' % (certificate_id, sig))
    log.info("string:%s" % stringtosign)
    log.info("cmd:%s" % cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def del_bucket(bucket_name, certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          删除桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param exe_node_ip:    (str)执行命令的节点
    :return:
    """
    cmd = 'curl -s -i http://%s:%s/%s -X DELETE -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def del_bucket_by_sk(bucket_name, certificate_id, certificate, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          通过SK上传桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id, AK
    :param certificate:    (str)证书, SK
    :param exe_node_ip:    (str)执行命令的节点
    :return:
    """
    stringtosign = "DELETE" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"+bucket_name
    sig = mk_sig(certificate, stringtosign)
    sig = mk_sig_code(sig)
    cmd = ('curl -i http://%s:%s/%s -XDELETE -H "Authorization: AWS %s:%s"'
           % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def del_bucket_by_sig(bucket_name, certificate_id, sig, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          通过SK上传桶
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id, AK
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :return:
    """
    cmd = ('curl -i http://%s:%s/%s -XDELETE -H "Authorization: AWS %s:%s"'
           % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def check_bucket(bucket_name, certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          检查桶是否存在
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = 'curl -s -i http://%s:%s/%s -X HEAD -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_bucket_meta(bucket_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.10.08
    :description:          检查桶是否存在
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s -i http://%s:%s/%s -X HEAD -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id)
    else:
        cmd = 'curl -s -i http://%s:%s/%s -X HEAD -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    meta_num = stdout.count("x-amz-meta-")

    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, meta_num
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_object_meta(bucket_name, object_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.10.08
    :description:          检查桶是否存在
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s -i http://%s:%s/%s/%s -X HEAD -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id)
    else:
        cmd = 'curl -s -i http://%s:%s/%s/%s -X HEAD -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    meta_num = stdout.count("x-amz-meta-")

    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, meta_num
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def check_bucket_by_sk(bucket_name, certificate_id, sk, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.09.06
    :description:          检查桶是否存在
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    stringtosign = "HEAD" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/" + bucket_name
    sig = mk_sig(sk, stringtosign)
    sig = mk_sig_code(sig)
    cmd = 'curl -s -i http://%s:%s/%s -X HEAD -H "Authorization: AWS %s:%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_all_bucket(certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取账户下所有桶的信息
    :param exe_node_ip:    (str)执行命令的节点
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = 'curl -s -i http://%s:%s -X GET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_all_bucket_name(certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个账户下所有桶
    :param exe_node_ip:    (str)执行命令的节点
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = 'curl -s -i http://%s:%s -X GET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            bucket_name_lst = get_xml_tag_text(xml_info, 'Name')
            return rc, bucket_name_lst
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def get_all_bucket_by_sk(certificate_id, sk, complex=False, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.09.07
    :description:          通过sk获取账户下所有桶的信息
    :param certificate_id: (str)证书id
    :param sk:             (str)sk
    :param complex:        (bool)是否是复杂sk, 默认不复杂的
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if complex is False:
        stringtosign = "GET" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"
        sig = mk_sig(sk, stringtosign)
        sig = mk_sig_code(sig)
        cmd = 'curl -s -i http://%s:%s/ -X GET -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, certificate_id, sig)
    else:
        stringtosign = "GET" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + "" + "/"
        sig = mk_sig(sk, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -s -i http://%s:%s/ -X GET  -H "Date: Wed, 31 Jan 2018 14:37:09 GMT" -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_all_bucket_by_sig(certificate_id, sig, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.09.07
    :description:          通过sig获取账户下所有桶的信息
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    cmd = ('curl -i http://%s:%s/ -XGET -H "Authorization: AWS %s:%s"' % (ooss_ip, S3_Port, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_bucket_storageinfo_by_sig(bucket_name, certificate_id, sig, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjla
    :date:                 2018.09.08
    :description:          获取一个桶的存量信息
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    cmd = ('curl -s -i http://%s:%s/%s?storageinfo -XGET -H "Authorization: AWS %s:%s"'
           % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            index = stdout.find('<?xml')
            xml_info = stdout[index:]
            bucket_storageinfo_lst = get_xml_tag_text(xml_info, 'Size')
            return rc, bucket_storageinfo_lst[0]
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def get_bucket_storageinfo(bucket_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjla
    :date:                 2018.09.08
    :description:          获取一个桶的存量信息
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if sig is None:
        cmd = ('curl -s -i http://%s:%s/%s?storageinfo -XGET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id))
    else:
        cmd = ('curl -s -i http://%s:%s/%s?storageinfo -XGET -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            index = stdout.find('<?xml')
            xml_info = stdout[index:]
            bucket_storageinfo_lst = get_xml_tag_text(xml_info, 'Size')
            return rc, bucket_storageinfo_lst[0]
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def update_bucket_quota(bucket_name, certificate_id, quota, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个桶下的所有桶对象
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param quota:          (int)桶的配额
    :return:
    """
    if exe_node_ip is None:
        cmd = 'curl -i http://%s:%s/%s?quota -XPUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" ' \
              '-d \'<?xml version="1.0" encoding="UTF-8"?>' \
              '<Quota xmlns="http://pos.com/doc/2006-03-01">' \
              '<StorageQuota>%s</StorageQuota>' \
              '</Quota>\'' % (ooss_ip, S3_Port, bucket_name, certificate_id, quota)
    else:
        cmd = 'ssh %s "curl -i http://%s:%s/%s?quota -XPUT -H \\\"Authorization: AWS4-HMAC-SHA256 Credential=%s\\\" ' \
              '-d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>' \
              '<Quota xmlns=\\\"http://pos.com/doc/2006-03-01\\\">' \
              '<StorageQuota>%s</StorageQuota>' \
              '</Quota>\'"' % (exe_node_ip, ooss_ip, S3_Port, bucket_name, certificate_id, quota)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def update_bucket_quota_by_sig(bucket_name, certificate_id, quota, sig, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.09.08
    :description:          认证模式下获取桶配额
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param quota:          (int)桶的配额
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if exe_node_ip is None:
        cmd = 'curl -i http://%s:%s/%s?quota -XPUT -H "Authorization: AWS %s:%s" ' \
              '-d \'<?xml version="1.0" encoding="UTF-8"?>' \
              '<Quota xmlns="http://pos.com/doc/2006-03-01">' \
              '<StorageQuota>%s</StorageQuota>' \
              '</Quota>\'' % (ooss_ip, S3_Port, bucket_name, certificate_id, sig, quota)
    else:
        cmd = 'ssh %s "curl -i http://%s:%s/%s?quota -XPUT -H \\\"Authorization: AWS %s:%s\\\" ' \
              '-d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>' \
              '<Quota xmlns=\\\"http://pos.com/doc/2006-03-01\\\">' \
              '<StorageQuota>%s</StorageQuota>' \
              '</Quota>\'"' % (exe_node_ip, ooss_ip, S3_Port, bucket_name, certificate_id, sig, quota)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_bucket_quota(bucket_name, certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个桶的配额大小
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = ('curl -s -i http://%s:%s/%s?quota -XGET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
           % (ooss_ip, S3_Port, bucket_name, certificate_id))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            bucket_quota_lst = get_xml_tag_text(xml_info, 'StorageQuota')
            return rc, bucket_quota_lst[0]
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def get_bucket_quota_by_sig(bucket_name, certificate_id, sig, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               wangjla
    :date:                 2018.09.08
    :description:          通过sig获取一个桶的配额大小
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    cmd = ('curl -s -i http://%s:%s/%s?quota -XGET -H "Authorization: AWS %s:%s"'
           % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            bucket_quota_lst = get_xml_tag_text(xml_info, 'StorageQuota')
            return rc, bucket_quota_lst[0]
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def set_bucket_acl(bucket_name, certificate_id, owner_account_id, owner_account_email,
                   des_account_id, dst_account_email, operation, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:                    baourobing
    :date:                      2018.08.29
    :description:               获取一个桶的配额大小
    :param exe_node_ip:         (str)执行命令的节点
    :param bucket_name:         (str)桶名字
    :param certificate_id:      (str)证书id
    :param owner_account_id:    (str)所有者账户id
    :param owner_account_email: (str)所有者账户邮箱
    :param des_account_id:      (str目标账户id
    :param dst_account_email:   (str)目标账户邮箱
    :param operation:           (str)许可
    :param sig:                 (str)sig
    :return:
    """
    if sig is None:
        if exe_node_ip is None:
            cmd = ('curl -i http://%s:%s/%s?acl -XPUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" '
                   '-d \'<?xml version="1.0" encoding="UTF-8"?>'
                   '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
                   '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
                   '<AccessControlList><Grant>'
                   '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant></AccessControlList></AccessControlPolicy>\''
                   % (ooss_ip, S3_Port, bucket_name, certificate_id, owner_account_id,
                      owner_account_email, des_account_id, dst_account_email, operation))
        else:
            cmd = ('ssh %s "curl -i http://%s:%s/%s?acl -XPUT -H \\\"Authorization: AWS4-HMAC-SHA256 Credential=%s\\\" '
                   '-d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>'
                   '<AccessControlPolicy xmlns=\\\"http://s3.amazonaws.com/doc/2006-03-01/\\\">'
                   '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
                   '<AccessControlList><Grant>'
                   '<Grantee xmlns:xsi=\\\"http://www.w3.org/2001/XMLSchema-instance\\\" xsi:type=\\\"CanonicalUser\\\">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant></AccessControlList></AccessControlPolicy>\'"'
                   % (exe_node_ip, ooss_ip, S3_Port, bucket_name, certificate_id, owner_account_id,
                      owner_account_email, des_account_id, dst_account_email, operation))
    else:
        if exe_node_ip is None:
            cmd = ('curl -i http://%s:%s/%s?acl -XPUT -H "Authorization: AWS %s:%s" '
                   '-d \'<?xml version="1.0" encoding="UTF-8"?>'
                   '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
                   '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
                   '<AccessControlList><Grant>'
                   '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant></AccessControlList></AccessControlPolicy>\''
                   % (ooss_ip, S3_Port, bucket_name, certificate_id, sig, owner_account_id,
                      owner_account_email, des_account_id, dst_account_email, operation))
        else:
            cmd = ('ssh %s "curl -i http://%s:%s/%s?acl -XPUT -H \\\"Authorization: AWS %s:%s\\\" '
                   '-d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>'
                   '<AccessControlPolicy xmlns=\\\"http://s3.amazonaws.com/doc/2006-03-01/\\\">'
                   '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
                   '<AccessControlList><Grant>'
                   '<Grantee xmlns:xsi=\\\"http://www.w3.org/2001/XMLSchema-instance\\\" xsi:type=\\\"CanonicalUser\\\">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant></AccessControlList></AccessControlPolicy>\'"'
                   % (exe_node_ip, ooss_ip, S3_Port, bucket_name, certificate_id, sig, owner_account_id,
                      owner_account_email, des_account_id, dst_account_email, operation))

    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def set_bucket_acl_multi(bucket_name, certificate_id, owner_account_id, owner_account_email,
                         des_account_info_lst, operation, retry=False, ooss_ip=None):
    """
    :author:                     baourobing
    :date:                       2018.08.29
    :description:                设置一个桶的多个acl信息
    :param bucket_name:          (str)桶名字
    :param certificate_id:       (str)证书id
    :param owner_account_id:     (str)所有者账户id
    :param owner_account_email:  (str)所有者账户邮箱
    :param des_account_info_lst: (list)每一项是字典:目标账户的信息, 键是'account_id'和'account_email'
                                 [{'account_id': '***', 'account_email': '***'}]
    :param operation:            (str)许可
    :param retry:
    :return:
    """
    cmd_lst = []
    cmd_pre = ('curl -i http://%s:%s/%s?acl -XPUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" '
               '-d \'<?xml version="1.0" encoding="UTF-8"?>'
               '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
               '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
               '<AccessControlList>'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, owner_account_id, owner_account_email))
    cmd_lst.append(cmd_pre)
    for des_account_info in des_account_info_lst:
        des_account_id = des_account_info['account_id']
        dst_account_email = des_account_info['account_email']
        cmd_tmp = ('<Grant>'
                   '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant>' % (des_account_id, dst_account_email, operation))
        cmd_lst.append(cmd_tmp)
    cmd_last = '</AccessControlList></AccessControlPolicy>\''
    cmd_lst.append(cmd_last)
    cmd = ''.join(cmd_lst)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_bucket_acl(bucket_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个桶的acl信息
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :return: 账户id, 账户邮箱, Permission
    """
    if sig is None:
        cmd = ('curl -i http://%s:%s/%s?acl -XGET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id))
    else:
        cmd = ('curl -i http://%s:%s/%s?acl -XGET -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None, None, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            account_id_lst = get_xml_tag_text(xml_info, 'ID')
            account_email_lst = get_xml_tag_text(xml_info, 'DisplayName')
            permission_lst = get_xml_tag_text(xml_info, 'Permission')
            return rc, account_id_lst, account_email_lst, permission_lst
        else:
            return -1, None, None, None


@retry_curl_cmd
@set_ooss_ip
def get_bucket_acl_info(bucket_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个桶的acl信息
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if sig is None:
        cmd = ('curl -i http://%s:%s/%s?acl -XGET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id))
    else:
        cmd = ('curl -i http://%s:%s/%s?acl -XGET -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


def get_system_disk(node_ip=None):
    """
    :author:        baourobing
    :date:          2018.08.29
    :description:   获取一个节点的系统盘
    :param node_ip: (str)节点ip
    :return:
    """
    cmd = 'df -l'
    if node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(node_ip, cmd, print_flag=False)
    common.judge_rc(rc, 0, "Execute command: \"%s\" failed. \nstdout: %s" % (cmd, stdout))
    line_lst = stdout.splitlines()
    return line_lst[1].split()[0].strip()


def create_file_m(file_path, size, exe_node_ip=None):
    """
    :author:            baourobing
    :date:              2018.08.29
    :description:       在一个节点上创建文件
    :param exe_node_ip: (str)节点ip
    :param file_path:   (str)文件全路径
    :param size:        (int)文件大小, 单位:M
    :return:
    """
    system_disk = get_system_disk(exe_node_ip)
    cmd = "dd if=%s of=%s bs=1M count=%s" % (system_disk, file_path, size)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    return rc, stdout

def create_file_k(file_path, size, exe_node_ip=None):
    """
    :author:            zhanghan
    :date:              2018.12.24
    :description:       在一个节点上创建文件
    :param exe_node_ip: (str)节点ip
    :param file_path:   (str)文件全路径
    :param size:        (int)文件大小, 单位:k
    :return:
    """
    system_disk = get_system_disk(exe_node_ip)
    cmd = "dd if=%s of=%s bs=1k count=%s" % (system_disk, file_path, size)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    return rc, stdout


def truncate_file(file_path, size, exe_node_ip=None):
    """
    :author:            lichengxu
    :date:              2018.11.19
    :description:       在一个节点上创建空洞文件
    :param exe_node_ip: (str)节点ip
    :param file_path:   (str)文件全路径
    :param size:        (str)文件大小
    :return:
    """
    # system_disk = get_system_disk(exe_node_ip)
    # cmd = "dd if=%s of=%s bs=1M count=%s" % (system_disk, file_path, size)
    cmd = "touch %s;truncate -s %s %s" % (file_path, size, file_path)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    return rc, stdout


def get_file_md5(file_path, nodeip=None):
    """
    :author:          baourobing
    :date:            2018.08.29
    :description:     获取文件的md5值
    :param nodeip:
    :param file_path:
    :return:
    """
    cmd = 'md5sum %s' % file_path
    if nodeip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(nodeip, cmd)
    md5 = stdout.strip().split()[0]
    return rc, md5


@retry_curl_cmd
@set_ooss_ip
def add_object(bucket_name, object_name, filepath, certificate_id, exe_node_ip=None, print_flag=True, retry=False,
               ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          添加对象
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param filepath:       (str)文件的绝对路径
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = 'curl -i http://%s:%s/%s/%s -X PUT -T %s -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def add_object_info(bucket_name, object_name, fileinfo, ak, sig=None, exe_node_ip=None, print_flag=True, retry=False,
                    ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          添加对象
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param fileinfo:       (str)文件的绝对路径
    :return:
    """
    if sig is None:
        cmd = 'curl -i http://%s:%s/%s/%s -X PUT -d "%s" -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, fileinfo, ak)
    else:
        cmd = 'curl -i http://%s:%s/%s/%s -X PUT -d "%s" -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, fileinfo, ak, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def add_object_over_quota(bucket_name, object_name, filepath, certificate_id, exe_node_ip=None, retry=False,
                          ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          添加对象超过配额
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param filepath:       (str)文件的绝对路径
    :param certificate_id: (str)证书id
    :return:
    """
    cmd = 'curl -i http://%s:%s/%s/%s -X PUT -T %s -H Expect: -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    return rc, stdout


@retry_curl_cmd
@set_ooss_ip
def add_object_by_sk(bucket_name, object_name, file_path, certificate_id, certificate, complex=False, exe_node_ip=None,
                     retry=False, ooss_ip=None):
    """
    :author:               wangjianlei
    :date:                 2018.09.07
    :description:          通过SK上传对象
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param file_path:      (str)上传的文件的绝对路径
    :param certificate_id: (str)证书id, AK
    :param certificate:    (str)证书, SK
    :param complex:        (bool)是否是复杂sk, 默认不复杂的
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if complex is False:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"+bucket_name+"/"+object_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s/%s -XPUT -T %s -H "Authorization: AWS %s:%s"'
               % (ooss_ip, S3_Port, bucket_name, object_name, file_path, certificate_id, sig))
    else:
        stringtosign = "PUT" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + "" \
                       + "/" + bucket_name+"/"+object_name
        sig = mk_sig(certificate, stringtosign)
        sig = mk_sig_code(sig)
        cmd = ('curl -i http://%s:%s/%s/%s -XPUT -T %s -H "Date: Wed, 31 Jan 2018 14:37:09 GMT"'' -H "Autho'
               'rization: AWS %s:%s"' % (ooss_ip, S3_Port, bucket_name, object_name, file_path, certificate_id, sig))
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def set_object_acl(bucket_name, object_name, owner_certificate_id, owner_accountid, owner_email, target_accountid,
                   target_email, acl, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:                     wangjianlei
    :date:                       2018.10.09
    :description:                设置对象acl
    :param exe_node_ip:          (str)执行命令的节点ip
    :param bucket_name:          (str)桶名字
    :param object_name:          (str)对象名字
    :param owner_certificate_id: (str)所有者证书id
    :param owner_accountid:      (str)所有者账户id
    :param owner_email:          (str)所有者邮箱
    :param target_accountid:     (str)目标者账户id
    :param target_email:         (str)目标者邮箱
    :param acl:                  (str)acl
    :return:
    """
    if sig is None:
        if exe_node_ip is None:
            cmd = 'curl -i http://%s:%s/%s/%s?acl -X PUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" -d \'' \
              '<?xml version="1.0" encoding="UTF-8"?>' \
              '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">' \
              '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>' \
              '<AccessControlList><Grant>' \
              '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">' \
              '<ID>%s</ID><DisplayName>%s</DisplayName>' \
              '</Grantee>' \
              '<Permission>%s</Permission>' \
              '</Grant></AccessControlList></AccessControlPolicy>\'' % \
              (ooss_ip, S3_Port, bucket_name, object_name, owner_certificate_id, owner_accountid,
               owner_email, target_accountid, target_email, acl)
        else:
            cmd = 'ssh %s "curl -i http://%s:%s/%s/%s?acl -X PUT -H \\\"Authorization: AWS4-HMAC-SHA256 Credential=%s\\\"' \
              ' -d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>' \
              '<AccessControlPolicy xmlns=\\\"http://s3.amazonaws.com/doc/2006-03-01/\\\">' \
              '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>' \
              '<AccessControlList><Grant>' \
              '<Grantee xmlns:xsi=\\\"http://www.w3.org/2001/XMLSchema-instance\\\" xsi:type=\\\"CanonicalUser\\\">' \
              '<ID>%s</ID><DisplayName>%s</DisplayName>' \
              '</Grantee>' \
              '<Permission>%s</Permission>' \
              '</Grant></AccessControlList></AccessControlPolicy>\'"' % \
              (exe_node_ip, ooss_ip, S3_Port, bucket_name, object_name, owner_certificate_id, owner_accountid,
               owner_email, target_accountid, target_email, acl)
    else:
        if exe_node_ip is None:
            cmd = 'curl -i http://%s:%s/%s/%s?acl -X PUT -H "Authorization: AWS %s:%s" -d \'' \
              '<?xml version="1.0" encoding="UTF-8"?>' \
              '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">' \
              '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>' \
              '<AccessControlList><Grant>' \
              '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">' \
              '<ID>%s</ID><DisplayName>%s</DisplayName>' \
              '</Grantee>' \
              '<Permission>%s</Permission>' \
              '</Grant></AccessControlList></AccessControlPolicy>\'' % \
              (ooss_ip, S3_Port, bucket_name, object_name, owner_certificate_id, sig, owner_accountid,
               owner_email, target_accountid, target_email, acl)
        else:
            cmd = 'ssh %s "curl -i http://%s:%s/%s/%s?acl -X PUT -H \\\"Authorization: AWS %s:%s\\\"' \
              ' -d \'<?xml version=\\\"1.0\\\" encoding=\\\"UTF-8\\\"?>' \
              '<AccessControlPolicy xmlns=\\\"http://s3.amazonaws.com/doc/2006-03-01/\\\">' \
              '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>' \
              '<AccessControlList><Grant>' \
              '<Grantee xmlns:xsi=\\\"http://www.w3.org/2001/XMLSchema-instance\\\" xsi:type=\\\"CanonicalUser\\\">' \
              '<ID>%s</ID><DisplayName>%s</DisplayName>' \
              '</Grantee>' \
              '<Permission>%s</Permission>' \
              '</Grant></AccessControlList></AccessControlPolicy>\'"' % \
              (exe_node_ip, ooss_ip, S3_Port, bucket_name, object_name, owner_certificate_id, sig, owner_accountid,
               owner_email, target_accountid, target_email, acl)
    log.info(cmd)
    rc, stdout = common.run_command_shot_time(cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def set_object_acl_multi(bucket_name, object_name, certificate_id, owner_account_id, owner_account_email,
                         des_account_info_lst, operation, retry=False, ooss_ip=None):
    """
    :author:                     baourobing
    :date:                       2018.08.29
    :description:                设置一个桶的多个acl信息
    :param bucket_name:          (str)桶名字
    :param certificate_id:       (str)证书id
    :param owner_account_id:     (str)所有者账户id
    :param owner_account_email:  (str)所有者账户邮箱
    :param des_account_info_lst: (list)每一项是字典:目标账户的信息, 键是'account_id'和'account_email'
                                 [{'account_id': '***', 'account_email': '***'}]
    :param operation:            (str)许可
    :param retry:
    :return:
    """
    cmd_lst = []
    cmd_pre = ('curl -i http://%s:%s/%s/%s?acl -XPUT -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" '
               '-d \'<?xml version="1.0" encoding="UTF-8"?>'
               '<AccessControlPolicy xmlns="http://s3.amazonaws.com/doc/2006-03-01/">'
               '<Owner><ID>%s</ID><DisplayName>%s</DisplayName></Owner>'
               '<AccessControlList>'
               % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, owner_account_id, owner_account_email))
    cmd_lst.append(cmd_pre)
    for des_account_info in des_account_info_lst:
        des_account_id = des_account_info['account_id']
        dst_account_email = des_account_info['account_email']
        cmd_tmp = ('<Grant>'
                   '<Grantee xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:type="CanonicalUser">'
                   '<ID>%s</ID><DisplayName>%s</DisplayName>'
                   '</Grantee>'
                   '<Permission>%s</Permission>'
                   '</Grant>' % (des_account_id, dst_account_email, operation))
        cmd_lst.append(cmd_tmp)
    cmd_last = '</AccessControlList></AccessControlPolicy>\''
    cmd_lst.append(cmd_last)
    cmd = ''.join(cmd_lst)
    rc, stdout = common.run_command_shot_time(cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_object_acl(bucket_name, object_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取对象acl
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -i http://%s:%s/%s/%s?acl -XGET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id)
    else:
        cmd = 'curl -i http://%s:%s/%s/%s?acl -XGET -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig)
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(stdout)
    if rc != 0:
        return rc, None, None, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            account_id_lst = get_xml_tag_text(xml_info, 'ID')
            account_email_lst = get_xml_tag_text(xml_info, 'DisplayName')
            permission_lst = get_xml_tag_text(xml_info, 'Permission')
            return rc, account_id_lst, account_email_lst, permission_lst
        else:
            return -1, None, None, None


@retry_curl_cmd
@set_ooss_ip
def get_obj_in_bucket(bucket_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baoruobing
    :date:                 2018.09.06
    :description:          获取桶的信息
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :param sig:            (str)sig
    :param exe_node_ip:    (str)执行命令的节点
    :param retry:
    :return:
    """
    if sig is None:
        cmd = 'curl -s -i http://%s:%s/%s -X GET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id)
    else:
        cmd = 'curl -s -i http://%s:%s/%s -X GET -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id, sig)

    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def get_all_object_in_bucket(bucket_name, certificate_id, sig=None, complex=False, exe_node_ip=None, retry=False,
                             ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          获取一个桶的信息
    :param exe_node_ip:    (str)执行命令的节点
    :param bucket_name:    (str)桶名字
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s -i http://%s:%s/%s -X GET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, certificate_id)
    else:
        if complex is False:
            cmd = 'curl -s -i http://%s:%s/%s -X GET -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id, sig)
        else:
            cmd = 'curl -s -i http://%s:%s/%s -X GET -H "Date: Wed, 31 Jan 2018 14:37:09 GMT" -H' \
                  ' "Authorization: AWS %s:%s"' % (ooss_ip, S3_Port, bucket_name, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            object_name_lst = get_xml_tag_text(xml_info, 'Key')
            return rc, object_name_lst
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def del_object(bucket_name, object_name, certificate_id, sig=None, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          删除对象
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -i http://%s:%s/%s/%s -X DELETE -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id)
    else:
        cmd = 'curl -i http://%s:%s/%s/%s -X DELETE -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def multi_del_object(bucket_name, object_name_lst, certificate_id, sig=None, exe_node_ip=None, retry=False,
                     ooss_ip=None):
    """
    :author:               lichengxu
    :date:                 2018.11.23
    :description:          批量删除指定对象
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)指定删除对象列表
    :param certificate_id: (str)证书id
    :return:
    """
    del_object_str = '\'<Delete>'
    for object_name in object_name_lst:
        tmp_str = "<Object><Key>%s</Key></Object>" % object_name
        del_object_str += tmp_str
    del_object_str += '</Delete>\''

    if sig is None:
        cmd = 'curl -i http://%s:%s/%s?delete -X POST -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" -d %s' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id, del_object_str)
    else:
        cmd = 'curl -i http://%s:%s/%s?delete -X POST -H "Authorization: AWS %s:%s" -d %s' \
              % (ooss_ip, S3_Port, bucket_name, certificate_id, sig, del_object_str)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def download_object(bucket_name, object_name, filepath, certificate_id, sig=None, exe_node_ip=None, print_flag=True,
                    retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          下载对象
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param filepath:       (str)存文件的路径
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id)
    else:
        cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id, sig)
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
    return rc, stdout


@retry_curl_cmd
@set_ooss_ip
def cp_object(dest_bucket_name, dest_object_name, certificate_id, src_bucket_name, src_obj_name, sig=None, byte=None,
              exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:                 baourobing
    :date:                   2018.08.29
    :description:            拷贝对象
    :param exe_node_ip:      (str)执行命令的节点ip
    :param dest_bucket_name: (str)目的桶名字
    :param dest_object_name: (str)目的对象名字
    :param certificate_id:   (str)证书id
    :param src_bucket_name:  (str)源桶名字
    :param src_obj_name:     (str)源对象名字
    :return:
    """
    if byte is None:
        if sig is None:
            cmd = ('curl -i http://%s:%s/%s/%s -X PUT  -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" '
                   '-H "x-amz-copy-source: /%s/%s"'
                   % (ooss_ip, S3_Port, dest_bucket_name, dest_object_name, certificate_id, src_bucket_name,
                      src_obj_name))
        else:
            cmd = ('curl -i http://%s:%s/%s/%s -X PUT  -H "Authorization: AWS %s:%s" -H "x-amz-copy-source:/%s/%s"'
                   % (ooss_ip, S3_Port, dest_bucket_name, dest_object_name, certificate_id, sig, src_bucket_name,
                      src_obj_name))
    else:
        if sig is None:
            cmd = ('curl -i http://%s:%s/%s/%s -X PUT  -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" ' 
                   '-H "x-amz-copy-source: /%s/%s" -H %s'
                   % (ooss_ip, S3_Port, dest_bucket_name, dest_object_name, certificate_id, src_bucket_name,
                      src_obj_name, byte))
        else:
            cmd = ('curl -i http://%s:%s/%s/%s -X PUT  -H "Authorization: AWS %s:%s" -H "x-amz-copy-source:/%s/%s" '
                   '-H %s' % (ooss_ip, S3_Port, dest_bucket_name, dest_object_name, certificate_id, sig,
                              src_bucket_name, src_obj_name, byte))
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return 0, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def init_put_object_by_segment(bucket_name, object_name, certificate_id, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          初始化多段上传命令
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param certificate_id: (str)证书id
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:               (str)UploadId
    """
    cmd = ('curl -i -s http://%s:%s/%s/%s?uploads -XPOST -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
           % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            uploadid_lst = get_xml_tag_text(xml_info, 'UploadId')
            return rc, uploadid_lst[0]
        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def put_object_segment(bucket_name, object_name, part_number, upload_id, certificate_id, part_name, exe_node_ip=None,
                       retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          多段上传命令
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param part_number:    (str)分段号
    :param upload_id:      (str)UploadId
    :param certificate_id: (str)证书id
    :param part_name:      (str)分段文件的绝对路径及名称
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:
    """
    cmd = ('curl -i -s http://%s:%s/%s/%s?partNumber=%s\&uploadId=%s -XPUT '
           '-H "Authorization: AWS4-HMAC-SHA256 Credential=%s" -T %s'
           % (ooss_ip, S3_Port, bucket_name, object_name, part_number, upload_id, certificate_id, part_name))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def cancle_put_object_segmet(bucket_name, object_name, upload_id, certificate_id, exe_node_ip=None, retry=False,
                             ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          取消多段上传命令
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param upload_id:      (str)UploadId
    :param certificate_id: (str)证书id
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:
    """
    cmd = ('curl -i http://%s:%s/%s/%s?uploadId=%s -XDELETE -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"'
           % (ooss_ip, S3_Port, bucket_name, object_name, upload_id, certificate_id))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    log.info(cmd)
    log.info(stdout)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def merge_object_seg(bucket_name, object_name, upload_id, certificate_id, part_number, exe_node_ip=None, retry=False,
                     ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          多段上传后合并对象
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param upload_id:      (str)UploadId
    :param certificate_id: (str)证书id
    :param part_number:    (int)分段个数
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:
    """
    cmd_str_lst = []
    cmd_pre = "<CompleteMultipartUpload>"
    cmd_str_lst.append(cmd_pre)
    for i in range(1, int(part_number)+1):
        cmd_str = "<Part><PartNumber>%d</PartNumber><ETag>etag</ETag></Part>" % i
        cmd_str_lst.append(cmd_str)
    cmd_last = "</CompleteMultipartUpload>"
    cmd_str_lst.append(cmd_last)
    cmd_file = "/tmp/s3_merge_object"
    with open(cmd_file, 'w') as f:
        f.writelines(cmd_str_lst)

    cmd = ('curl -i http://%s:%s/%s/%s?uploadId=%s -XPOST -H "Authorization: AWS4-HMAC-SHA256 Credential=%s" -T %s'
           % (ooss_ip, S3_Port, bucket_name, object_name, upload_id, certificate_id, cmd_file))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        scp_cmd = 'scp -r %s root@%s:/tmp' % (cmd_file, exe_node_ip)
        common.run_command_shot_time(scp_cmd)
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


def set_force_delete_bucket(current):
    """
    :author:        liuping
    :date:          2018.10.25
    :description:   修改强删桶的开关
    :param current: 1为打开, 0为关闭
    :return:
    """
    rc, stdout = common.update_param(section='oApp', name='pos_enable_force_delete_bucket', current=current)
    return rc, stdout


def cleaning_environment(account_email_lst):
    """
    :author:                  baourobing
    :date:                    2018.08.29
    :description:             清理s3用例环境
    :param account_email_lst: (list)账户邮箱
    :return:
    """
    """打开强删桶的开关"""
    rc, stdout = set_force_delete_bucket(1)
    common.judge_rc(rc, 0, "set_force_delete_bucket=1 fail!!!")

    """获取账户id"""
    for account_email in account_email_lst:
        rc, account_id = get_account_id_by_email(account_email)
        if rc != 0:
            continue

        """获取证书id列表"""
        rc, certificate_id_lst, certificate_lst = get_certificate_by_accountid(account_id)
        common.judge_rc(rc, 0, "find certificate failed!!!")

        for certificate_id in certificate_id_lst:
            """获取所有桶的列表"""
            rc, bucket_name_lst = get_all_bucket_name(certificate_id)
            common.judge_rc(rc, 0, "get all becket failed!!!")
            for bucket_name in bucket_name_lst:
                '''                
                """获取桶中所有对象的名字"""
                rc, object_name_lst = get_all_object_in_bucket(bucket_name, certificate_id)
                common.judge_rc(rc, 0, "get all object in bucket failed!!!")
                """删除对象"""
                for object_name in object_name_lst:
                    del_object(bucket_name, object_name, certificate_id)
                    common.judge_rc(rc, 0, "del_object failed!!!")
                '''
                """删除桶"""
                del_bucket(bucket_name, certificate_id)
            """删除证书"""
            del_certificate(certificate_id)
        """删除账户"""
        del_account(account_id)

    """关闭强删桶的开关"""     # add by zhanghan 20181222
    rc, stdout = set_force_delete_bucket(0)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")

    return


def cleaning_environment_no_force(account_email_lst):
    """
    :author:                  baourobing
    :date:                    2018.08.29
    :description:             清理s3用例环境
    :param account_email_lst: (list)账户邮箱
    :return:
    """
    '''
    """关闭强删桶的开关"""
    rc, stdout = set_force_delete_bucket(0)
    common.judge_rc(rc, 0, "set_force_delete_bucket=0 fail!!!")
   '''
    """获取账户id"""
    for account_email in account_email_lst:
        rc, account_id = get_account_id_by_email(account_email)
        if rc != 0:
            continue

        """获取证书id列表"""
        rc, certificate_id_lst, certificate_lst = get_certificate_by_accountid(account_id)
        common.judge_rc(rc, 0, "find certificate failed!!!")

        for certificate_id in certificate_id_lst:
            """获取所有桶的列表"""
            rc, bucket_name_lst = get_all_bucket_name(certificate_id)
            common.judge_rc(rc, 0, "get all becket failed!!!")
            for bucket_name in bucket_name_lst:
                """获取桶中所有对象的名字"""
                rc, object_name_lst = get_all_object_in_bucket(bucket_name, certificate_id)
                common.judge_rc(rc, 0, "get all object in bucket failed!!!")
                """删除对象"""
                for object_name in object_name_lst:
                    del_object(bucket_name, object_name, certificate_id)
                    common.judge_rc(rc, 0, "del_object failed!!!")
                """删除桶"""
                del_bucket(bucket_name, certificate_id)
            """删除证书"""
            del_certificate(certificate_id)
        """删除账户"""
        del_account(account_id)
    return


@retry_curl_cmd
@set_ooss_ip
def put_object_segment_by_sig(bucket_name, object_name, part_number, upload_id, certificate_id, certificate, part_name,
                              faultsig=None, complex=False,  exe_node_ip=None, retry=False, ooss_ip=None):
    """
    description：当正常测试上传段时，faultsig不传参数，如果想要测试错误的sig，把错误的sig值传给faultsig
    :author:               liuyzhb
    :date:                 2018.10.09
    :description:          开启http认证时多段上传命令
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param part_number:    (str)分段号
    :param upload_id:      (str)UploadId
    :param certificate_id:    (str)证书AK
    :param certificate:    (str)证书SK
    :param part_name:      (str)分段文件的绝对路径及名称
    :param faultsig:       （str）错误的sig
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:
    """
    if complex is False:
        if faultsig is None:
            stringtosign = ("PUT" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/" + bucket_name + "/" +
                            object_name + '?partNumber=' + str(part_number) + '&uploadId=' + str(upload_id))
            log.info('param of sig is %s' % stringtosign)
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)
            log.info('sig of put_object_segment_by_sig is %s' % sig)
        else:
            sig = faultsig
            log.info('faultsig of put_object_segment_by_sig is %s' % sig)
        cmd = ('curl -i -s http://%s:%s/%s/%s?partNumber=%s\&uploadId=%s -XPUT '
               '-H "Authorization: AWS %s:%s" -T %s'
               % (ooss_ip, S3_Port, bucket_name, object_name, part_number, upload_id, certificate_id, sig, part_name))
        log.info(cmd)
    else:
        if faultsig is None:
            stringtosign = ("PUT" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + ""
                            + "/" + bucket_name + "/" + object_name + '?partNumber=' + str(part_number) + '&uploadId='
                            + str(upload_id))
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)
        else:
            sig = faultsig
            log.info('faultsig of put_object_segment_by_sig is %s' % sig)
        cmd = ('curl -i -s http://%s:%s/%s/%s?partNumber=%s\&uploadId=%s -XPUT -H '
               '-H "Authorization: AWS %s:%s" -T %s'
               % (ooss_ip, S3_Port, bucket_name, object_name, part_number, upload_id, certificate_id, sig, part_name))
        log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def init_put_object_by_segment_by_sig(bucket_name, object_name, certificate_id, certificate, faultsig=None,
                                      complex=False, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    description：当正常测试初始化多段时，faultsig不传参数，如果想要测试错误的sig，把错误的sig值传给faultsig
    :author:               liuyzhb
    :date:                 2018.10.09
    :description:          http认证开启下的初始化多段上传命令
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param certificate_id:   (str)证书, AK
    :param certificate:    (str)证书, SK
    :param faultsig:       （str）错误的sig
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:               (str)UploadId
    """
    if complex is False:
        if faultsig is None:
            stringtosign = ("POST" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/"
                            + bucket_name + "/"+object_name + '?uploads')
            log.info('param of init_put_object_by_segment_by_sig is %s' % stringtosign)
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)
            log.info('sig of init_put_object_by_segment_by_sig is %s' % sig)

            cmd = ('curl -i http://%s:%s/%s/%s?uploads -XPOST -H "Authorization: AWS %s:%s"' %
                   (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig))
            log.info('cmd of init_put_object_by_segment_by_sig is %s' % cmd)
        else:
            sig = faultsig
            log.info('faultsig of init_put_object_by_segment_by_sig is %s' % sig)
            cmd = ('curl -i http://%s:%s/%s/%s?uploads -XPOST -H "Authorization: AWS %s:%s"' % (
                ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig))
            log.info('cmd of init_put_object_by_segment_by_sig is %s' % cmd)

    else:
        if faultsig is None:
            stringtosign = ("POST" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + ""
                            + "/" + bucket_name + "/"+object_name + '?uploads')
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)

            cmd = ('curl -i http://%s:%s/%s/%s?uploads -XPOST -H "Date: Wed, 31 Jan 2018 14:37:09 GMT" -H '
                   '"Authorization: AWS %s:%s"' % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig))
        else:
            sig = faultsig
            log.info('faultsig of init_put_object_by_segment_by_sig is %s' % sig)
            cmd = ('curl -i http://%s:%s/%s/%s?uploads -XPOST -H "Date: Wed, 31 Jan 2018 14:37:09 GMT" -H '
                   '"Authorization: AWS %s:%s"' % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig))
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        print ''
        return rc, None
    else:
        if check_curl(stdout):
            xml_info = stdout.splitlines()[-1]
            uploadid_lst = get_xml_tag_text(xml_info, 'UploadId')
            return rc, uploadid_lst[0]

        else:
            return -1, None


@retry_curl_cmd
@set_ooss_ip
def merge_object_seg_by_sig(bucket_name, object_name, upload_id, certificate_id, certificate, part_number,
                            faultsig=None, complex=False, exe_node_ip=None, retry=False, ooss_ip=None):
    """
    description：当正常测试合并段时，faultsig不传参数，如果想要测试错误的sig，把错误的sig值传给faultsig
    :author:               liuyzhb
    :date:                 2018.10.09
    :description:          多段上传后合并对象
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param upload_id:      (str)UploadId
    :param certificate_id:    (str)证书AK
    :param certificate:    (str)证书SK
    :param part_number:    (int)分段个数
    :param faultsig:       （str）错误的sig
    :param exe_node_ip:    (str)执行命令的节点ip
    :return:
    """
    cmd_str_lst = []
    cmd_pre = "<CompleteMultipartUpload>"
    cmd_str_lst.append(cmd_pre)
    for i in range(1, int(part_number)+1):
        cmd_str = "<Part><PartNumber>%d</PartNumber><ETag>etag</ETag></Part>" % i
        cmd_str_lst.append(cmd_str)
    cmd_last = "</CompleteMultipartUpload>"
    cmd_str_lst.append(cmd_last)
    cmd_file = "/tmp/s3_merge_object"
    with open(cmd_file, 'w') as f:
        f.writelines(cmd_str_lst)
    if complex is False:
        if faultsig is None:
            stringtosign = ("POST" + "\n" + "" + "\n" + "" + "\n" + "" + "\n" + "" + "/" + bucket_name + "/"
                            + object_name + '?uploadId=' + upload_id)
            log.info('param of sig is %s' % stringtosign)
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)
            log.info('sig of put_object_segment_by_sig is %s' % sig)
        else:
            sig = faultsig
            log.info('faultsig of put_object_segment_by_sig is %s' % sig)

        cmd = ('curl -i  http://%s:%s/%s/%s?uploadId=%s -XPOST '
               '-H "Authorization: AWS %s:%s" -T %s'
               % (ooss_ip, S3_Port, bucket_name, object_name, upload_id, certificate_id, sig, cmd_file))
        cmda = 'cat ' + cmd_file
        rca, stdouta = common.run_command_shot_time(cmda)
        log.info('data form %s is :' % cmd_file)
        log.info(stdouta)
        log.info(cmd)
    else:
        if faultsig is None:
            stringtosign = ("POST" + "\n" + "" + "\n" + "" + "\n" + "Wed, 31 Jan 2018 14:37:09 GMT" + "\n" + ""
                            + "/" + + bucket_name + "/" + object_name + '?uploadId=' + upload_id)
            log.info('param of sig is %s' % stringtosign)
            sig = mk_sig(certificate, stringtosign)
            sig = mk_sig_code(sig)
            log.info('sig of put_object_segment_by_sig is %s' % sig)
        else:
            sig = faultsig
            log.info('fault sig of put_object_segment_by_sig is %s' % sig)
        cmd = ('curl -i  http://%s:%s/%s/%s?uploadId=%s -XPOST -H "Date: Wed, 31 Jan 2018 14:37:09 GMT"'
               '-H "Authorization: AWS %s:%s" -T %s'
               % (ooss_ip, S3_Port, bucket_name, object_name, upload_id, certificate_id, sig, cmd_file))
        log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        scp_cmd = 'scp -r %s root@%s:/tmp' % (cmd_file, exe_node_ip)
        common.run_command_shot_time(scp_cmd)
        rc, stdout = common.run_command(exe_node_ip, cmd)
    if rc != 0:
        return rc, stdout
    else:
        if check_curl(stdout):
            return rc, stdout
        else:
            return -1, stdout


@retry_curl_cmd
@set_ooss_ip
def download_object_by_sig(bucket_name, object_name, filepath, certificate_id, sig=None, exe_node_ip=None,
                           print_flag=True, retry=False, ooss_ip=None):
    """
    :author:               baourobing
    :date:                 2018.08.29
    :description:          下载对象
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param filepath:       (str)存文件的路径
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id)
    else:
        cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, filepath, certificate_id, sig)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
    log.info(cmd)
    log.info(stdout)
    return rc, stdout


@retry_curl_cmd
@set_ooss_ip
def download_object_print(bucket_name, object_name, certificate_id, sig=None, exe_node_ip=None, print_flag=True,
                          retry=False, ooss_ip=None):
    """
    :author:               liuyanzhe
    :date:                 2018.08.29
    :description:          下载对象
    :param exe_node_ip:    (str)执行命令的节点ip
    :param bucket_name:    (str)桶名字
    :param object_name:    (str)对象名字
    :param filepath:       (str)存文件的路径
    :param certificate_id: (str)证书id
    :return:
    """
    if sig is None:
        cmd = 'curl -s http://%s:%s/%s/%s -X GET -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
          % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id)
    else:
        cmd = 'curl -s http://%s:%s/%s/%s -X GET  -H "Authorization: AWS %s:%s"' \
              % (ooss_ip, S3_Port, bucket_name, object_name, certificate_id, sig)
    log.info(cmd)
    if exe_node_ip is None:
        rc, stdout = common.run_command_shot_time(cmd)
    else:
        rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
    return rc, stdout


def record_info_for_enables3(iplst):
    """
    Author:         chenjy1
    Date :          2018-11-20
    Description：   在enable_s3期间，9分钟未成功则记录一些信息，方便定位
    :param iplst:  记录信息的节点
    :return:       无
    """
    enable_s3_timeout_minutes = 10
    time.sleep((enable_s3_timeout_minutes-1)*60)
    cmd_lst = []
    cmd_lst.append('df /')
    cmd_lst.append('mount |grep system_volume')
    cmd_lst.append('ps aux |grep nas')
    cmd_lst.append('pstack $(pidof oCnas)')
    for ip in iplst:
        for cmd in cmd_lst:
            common.run_command(ip, cmd, print_flag=True)  # 仅看信息不判断
    return


def enable_s3(access_zone_id, print_flag=True, fault_node_ip=None):
    """
    Author:         chenjy1
    Date :          2018-11-20
    Description：   enable_s3
    :param access_zone_id: 访问分区id
    :return:       rc, stdout
    """
    p1 = Process(target=record_info_for_enables3, args=(get_config.get_allparastor_ips(),))
    p1.daemon = True
    p1.start()
    rc, stdout = common.enable_s3(access_zone_id, print_flag=print_flag, fault_node_ip=fault_node_ip)
    common.judge_rc(rc, 0, 'enable_nas failed', exit_flag=False)
    p1.terminate()
    p1.join()
    return rc, stdout