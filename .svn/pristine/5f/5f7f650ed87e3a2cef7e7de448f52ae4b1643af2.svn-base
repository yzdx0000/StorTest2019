# -*-coding:utf-8 -*
from multiprocessing import Process
import os
import re
import time
import json

import utils_path
import common
import log
import get_config
import prepare_clean
import upgrade_common
import quota_common
import tool_use
import online_upgrade

####################################################################################
#
# author 刘俊鑫
# date 2018-08-03
# @summary：
#   三节点，升级后查看升级前设置的目录逻辑空间硬阈值配额的有效性
# @steps:
#   step1: 设置目录逻辑空间硬阈值配额，查看配额有效性
#   step2：执行在线升级
#   step3：再次查看配额的有效性
#
# @changelog：
####################################################################################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                         # DEFECT_PATH = /mnt/vo/defect_case
DEFECT_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                     # DEFECT_TRUE_PATH= /mnt/vo/defect_case/p300
VOLUME_NAME = get_config.get_one_volume_name()                              # 卷名vo
QUORTA_TRUE_PATH = DEFECT_TRUE_PATH
QUORTA_PATH = VOLUME_NAME \
              + ':/' \
              + os.path.join(os.path.basename(DEFECT_PATH),
                             os.path.basename(DEFECT_TRUE_PATH))            # vo：/defect_case/p300
QUORTA_PATH_WITHOUT_VOLUME = re.sub('[%s:]' % VOLUME_NAME, '', QUORTA_PATH)  # /defect_case/p300
client_ip_lst = get_config.get_allclient_ip()                               # 客户端ip列表
server_ip_lst = get_config.get_allparastor_ips()


def quota_logical_check(path, quota_logical):
    """
    :author:               liujx
    :date:                 2018.08.03
    :description:          对于逻辑硬配额有效性检查
    :param path:           配额的路径
    :param quota_inode:    配额inode数目
    :return:
    """
    file_nums = quota_logical/1024/1024            # 2G的1M文件的个数
    log.info("quota check begin \nfirst time: create inode_logical files, expect succeed")
    """对有配额的目录写入配额数目的文件"""
    quota_common.creating_files(client_ip_lst[0], path, file_nums, 1, "a")

    log.info("second time: create 20 files, expect failed")
    """再尝试另一个客户端继续写入文件，预期不可写入"""
    quota_common.creating_files(client_ip_lst[1], path, 20, 1, "b")

    """检查配额是否生效"""
    log.info("quota_logical_check begin")
    total_inodes = quota_common.dir_total_inodes(client_ip_lst[0], path)
    if total_inodes != file_nums:
        raise Exception("quota_logical_check failed, quota_logocal=%d, but total_logical=%d" % (quota_logical,
                                                                                                total_inodes/1024))
    else:
        log.info("quota_logical_check succeed")

    common.rm_exe(client_ip_lst[0], os.path.join(path, '*'))

    return


def case():
    """

    :return:
    """
    quota_logical = quota_common.FILE_SIZE_2G
    """先创建配额并检查其有效性"""
    rc, pscli_info = quota_common.create_one_quota(path=QUORTA_PATH,
                                                   logical_quota_cal_type='QUOTA_LIMIT',
                                                   logical_hard_threshold=quota_logical)
    common.judge_rc(rc, 0, "create  quota failed")
    quota_logical_check(QUORTA_TRUE_PATH, quota_logical)

    """执行升级步骤"""
    online_upgrade.case()

    """升级后再次检查配额有效性"""
    quota_logical_check(QUORTA_TRUE_PATH, quota_logical)

    """删除配额"""
    quota_common.delete_all_quota_config()


def main():
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    upgrade_common.delete_upgrade()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
