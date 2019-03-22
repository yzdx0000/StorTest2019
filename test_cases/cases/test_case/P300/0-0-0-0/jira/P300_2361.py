# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import log
import get_config
import prepare_clean
import quota_common
import nas_common

####################################################################################
#
# Author: chenjy1
# date: 2018-08-07
# @summary：
#    创建已存在的用户，对其设置文件数硬阈值，然后创建文件，出ocnas的core
# @steps:
#    1、在用户和用户组已存在的情况下，再次使用pscli创建用户u1和用户组g1(创建时提示失败)
#    2、设置对于u1的文件数2000硬阈值
#    3、写1999个文件
#    4、清理环境
#    现象：出ocnas的core
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                       # DEFECT_PATH = "/mnt/volume1/defect_case
QUOTA_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                    # /mnt/volume1/defect_case/P300-2361
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)                      # defect_case
QUOTA_CREATE_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)         # defect_case/P300-2361


def case():
    ob_node = common.Node()
    node_ids = ob_node.get_node_id_by_ip(quota_common.NOTE_IP_1)  # 创建的访问区的ip
    pscli_info = nas_common.create_access_zone(node_ids, FILE_NAME)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    access_zone_id = pscli_info['result']

    cmd = 'chmod 777 %s ' % QUOTA_TRUE_PATH
    rc, stdout = common.run_command(common.SYSTEM_IP, cmd)
    common.judge_rc(rc, 0, 'cmd failed cmd: %s' % cmd)
    log.info("1> 在用户和用户组已存在的情况下，再次使用pscli创建用户u1和用户组g1(创建时提示失败)")
    """enable_nas"""
    pscli_info = nas_common.enable_nas(access_zone_id)  # 访问区的Id
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    pscli_info = nas_common.get_access_zones(ids=access_zone_id)
    auth_provider_id = pscli_info['result']['access_zones'][0]['auth_provider_id']

    username = FILE_NAME + 'u'
    groupname = FILE_NAME + 'g'
    """创建用户组和用户"""
    pscli_info = nas_common.create_auth_group(auth_provider_id, groupname)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    primary_group_id = pscli_info['result']

    pscli_info = nas_common.create_auth_user(auth_provider_id, username, '111111', primary_group_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    user_id = pscli_info['result']

    """再次创建用户和组"""
    nas_common.create_auth_group(auth_provider_id, groupname)
    nas_common.create_auth_user(auth_provider_id, username, '111111', primary_group_id)

    log.info("wait 40s")
    time.sleep(40)

    log.info("2> 创建文件数2000硬阈值的配额")
    rc, pscli_info = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, QUOTA_CREATE_PATH)),
                                                   auth_provider_id=auth_provider_id,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=2000,
                                                   user_type='USERTYPE_USER',
                                                   user_or_group_name=username)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    rc, quota_id = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, QUOTA_CREATE_PATH)),
                                                 u_or_g_type=quota_common.TYPE_USER,
                                                 u_or_g_name=username)

    log.info("3> 创建1999个文件")
    quota_common.creating_files_by_designated_user_or_group(quota_common.NOTE_IP_1, QUOTA_TRUE_PATH,
                                                            1999, 1, "a", username)
    """等10秒"""
    log.info("waiting 10s")
    time.sleep(10)

    log.info("4> 清理环境")
    """删除文件"""
    common.rm_exe(quota_common.NOTE_IP_1, QUOTA_TRUE_PATH)

    """删除配额"""
    quota_common.delete_single_quota_config(quota_id)

    """清除用户和用户组"""
    pscli_info = nas_common.delete_auth_users(user_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    pscli_info = nas_common.delete_auth_groups(primary_group_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    """disable_nas"""
    pscli_info = nas_common.disable_nas(access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    """清除访问区"""
    pscli_info = nas_common.delete_access_zone(access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    quota_common.delete_all_quota_config()
    nas_common.delete_all_nas_config()
    case()
    nas_common.delete_all_nas_config()
    quota_common.delete_all_quota_config()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
