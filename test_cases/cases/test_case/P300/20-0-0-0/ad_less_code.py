# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import time
import random
import re

import utils_path
import common
import log
import prepare_clean
import get_config
import nas_common
import make_fault
import snap_common
import tool_use
import nas_common_new

"""
 Author: liangxy
 date 2019-03-20
 @summary：
    ad测试用例代码去冗余
 @steps:
   

 @changelog：
 
"""
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0].replace('-', '_')                 # 本脚本名字


def init_ad():
    log.info("1.添加AD认证服务器")
    adobj = nas_common_new.AuthProviderAD(services_for_unix='NONE')
    msgad = adobj.add_auth_provider_ad()
    common.judge_rc(msgad['err_no'], 0, msgad['detail_err_msg'])
    return adobj.p_id


def init_az(provider_id=None):
    log.info("2.创建访问区，认证服务器id为{}".format(provider_id))
    azobj = nas_common_new.AccessZone(auth_provider_id=provider_id)
    msgaz = azobj.create_access_zone()
    common.judge_rc(msgaz['err_no'], 0, msgaz['detail_err_msg'])
    msgenable = azobj.enable_nas(protocol_types='NFS,SMB,FTP')
    common.judge_rc(msgenable['err_no'], 0, msgenable['detail_err_msg'])
    return azobj.a_id


def init_sub(access_id=None):

    log.info("3-1.创建子网，访问区id为{}".format(access_id))
    subobj = nas_common_new.Subnet(access_zone_id=access_id, description='English?')
    msgsub = subobj.create_subnet()
    common.judge_rc(msgsub['err_no'], 0, msgsub['detail_err_msg'])
    return subobj.subnet_id


def init_vip(subnet_id=None):

    log.info("3-2.创建vip池，子网id为{}".format(subnet_id))
    vipobj = nas_common_new.VipAddressPool(subnet_id=subnet_id)
    msgvip = vipobj.add_vip_address_pool()
    common.judge_rc(msgvip['err_no'], 0, msgvip['detail_err_msg'])
    return vipobj.vip_address_pool_id


def init_nfs_ex(a_id):
    log.info("4-1.导出nfs目录，访问区id为{}".format(a_id))
    nfsobj = nas_common_new.NfsExport(access_zone_id=a_id)
    msgnfs_ex = nfsobj.create_nfs_export()
    common.judge_rc(msgnfs_ex['err_no'], 0, msgnfs_ex['detail_err_msg'])
    return nfsobj.export_id


def init_nfs_auth(nfs_export_id):
    log.info("4-2.授权nfs目录，导出id为{}".format(nfs_export_id))
    nfsobj_au = nas_common_new.NfsExportAuthClient(export_id=nfs_export_id)
    msgmfs_autj = nfsobj_au.add_nfs_export_auth_clients()
    common.judge_rc(msgmfs_autj['err_no'], 0, msgmfs_autj['detail_err_msg'])
    return nfsobj_au.auth_client_id


def nfs_less_code(parass=None):
    if parass == []:
        parass = None
        log.warn("para dict is \{\},auto change to None")
    p_id = init_ad()
    a_id = init_az(provider_id=p_id)
    sub_id = init_sub(access_id=a_id)
    vip_id = init_vip(subnet_id=sub_id)
    log.info("vip pool id is {}".format(vip_id))
    return a_id


def ad_less_code(p_id):
    a_id = init_az(provider_id=p_id)
    sub_id = init_sub(access_id=a_id)
    vip_id = init_vip(subnet_id=sub_id)
    nfs_ex_id = init_nfs_ex(a_id=a_id)
    nfs_auth_id = init_nfs_auth(nfs_export_id=nfs_ex_id)
    log.info("vip id is {};nfs auth id is {}".format(vip_id, nfs_auth_id))
    return

