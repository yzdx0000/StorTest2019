# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import log
import get_config
import prepare_clean
import nas_common
import quota_common
#################################################################
#
# Author: chenjy1
# Date: 2018-8-8
# @summary：
#        创建配额规则后对应的配额规则一起删除
# @steps:
#       1、创建访问区
#       2、enable_nas
#       3、创建用户，用户组
#       4、创建目录、用户、用户组配额
#       5、删除配额目录
#       6、查看是否变为invalid状态
#       7、恢复环境
# @changelog：
#################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                       # DEFECT_PATH = "/mnt/volume1/defect_case
QUOTA_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                    # /mnt/volume1/defect_case/P300-611
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)                      # defect_case
QUOTA_CREATE_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)         # defect_case/P300-611


def case():
    log.info("case begin")
    log.info("1> 创建访问区")
    access_zone_name = FILE_NAME
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    str_node_id = ','.join(str(p) for p in node_id_lst)
    log.info(type(str_node_id))
    log.info(str_node_id)
    pscli_info = nas_common.create_access_zone(str_node_id, access_zone_name)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    access_zone_id = pscli_info['result']

    log.info("2> enable_nas")
    pscli_info = nas_common.enable_nas(access_zone_id)  # 访问区的Id
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    pscli_info = nas_common.get_access_zones(ids=access_zone_id)
    auth_provider_id = pscli_info['result']['access_zones'][0]['auth_provider_id']
    username = FILE_NAME + 'u'
    groupname = FILE_NAME + 'g'

    log.info("3> 创建用户，用户组")
    pscli_info = nas_common.create_auth_group(auth_provider_id, groupname)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    primary_group_id = pscli_info['result']

    pscli_info = nas_common.create_auth_user(auth_provider_id, username, '111111', primary_group_id)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    log.info("4> 创建目录、用户、用户组配额")
    quota_true_path_u = os.path.join(QUOTA_TRUE_PATH, 'u')
    quota_true_path_g = os.path.join(QUOTA_TRUE_PATH, 'g')
    quota_true_path_catalog = os.path.join(QUOTA_TRUE_PATH, 'c')
    quota_create_path_u = os.path.join(QUOTA_CREATE_PATH, 'u')
    quota_create_path_g = os.path.join(QUOTA_CREATE_PATH, 'g')
    quota_create_path_catalog = os.path.join(QUOTA_CREATE_PATH, 'c')

    quota_dict = {}
    quota_dict[quota_true_path_u] = quota_common.VOLUME_NAME + ':/' + quota_create_path_u
    quota_dict[quota_true_path_g] = quota_common.VOLUME_NAME + ':/' + quota_create_path_g
    quota_dict[quota_true_path_catalog] = quota_common.VOLUME_NAME + ':/' + quota_create_path_catalog

    for true_path in quota_dict:
        common.mkdir_path(common.SYSTEM_IP, true_path)

    """创建用户配额"""
    rc, pscli_info = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_create_path_u)),
                                                   auth_provider_id=auth_provider_id,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=2000,
                                                   user_type='USERTYPE_USER',
                                                   user_or_group_name=username)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    """创建用户组配额"""
    rc, pscli_info = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_create_path_g)),
                                                   auth_provider_id=auth_provider_id,
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=2000,
                                                   user_type='USERTYPE_GROUP',
                                                   user_or_group_name=groupname)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    """创建目录配额"""
    rc, pscli_info = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME,
                                                                     quota_create_path_catalog)),
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_hard_threshold=2000)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])

    log.info("5> 删除配额目录")
    for true_path in quota_dict:
        common.rm_exe(common.SYSTEM_IP, true_path)

    log.info('wait 20s')
    time.sleep(20)

    log.info("6> 查看是否变为invalid状态")
    state_still_work_quotaid = []
    all_quotaid = []
    rc, pscli_info = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    for quota in pscli_info['result']['quotas']:
        if quota['path'] in quota_dict.values():
            all_quotaid.append(quota['id'])
            if quota['state'] == 'QUOTA_WORK':
                state_still_work_quotaid.append(quota['id'])

    """检查"""
    if state_still_work_quotaid != []:
        for id in state_still_work_quotaid:
            quota_common.get_one_quota_info(id, print_flag=True)
        common.except_exit("some quota state is QUOTA_WORK ,failed")

    log.info('7> 恢复环境')
    """删除配额"""
    for id in all_quotaid:
        rc, pscli_info = quota_common.delete_one_quota(id)
        common.judge_rc(rc, 0, "delete quota failed")

    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    nas_common.delete_all_nas_config()
    case()
    prepare_clean.defect_test_clean(FILE_NAME, fault=True)
    nas_common.delete_all_nas_config()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
