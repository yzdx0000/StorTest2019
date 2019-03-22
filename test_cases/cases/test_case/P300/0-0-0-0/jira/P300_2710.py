# -*-coding:utf-8 -*
import os

import utils_path
import common
import log
import get_config
import prepare_clean
import quota_common

####################################################################################
#
# Author: chenjy
# date: 2018-08-07
# @summary：
#    创建软阈值，更改系统时间
# @steps:
#    1、创建目录文件数100软阈值配额，宽限时间70秒
#    2、触发阈值开始计算时间
#    3、修改主MGR点的系统时间
#    4、创建文件，验证在宽限期内能创建
#    5、修回系统时间
#    6、删除配额
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]               # 本脚本名字
DEFECT_PATH = get_config.get_one_defect_test_path()                       # DEFECT_PATH = "/mnt/volume1/defect_case
QUOTA_TRUE_PATH = os.path.join(DEFECT_PATH, FILE_NAME)                    # /mnt/volume1/defect_case/P300-2710
DEFECT_PATH_BASENAME = os.path.basename(DEFECT_PATH)                      # defect_case
QUOTA_CREATE_PATH = os.path.join(DEFECT_PATH_BASENAME, FILE_NAME)         # defect_case/P300-2710


def case():
    log.info("case begin")

    log.info("1> 创建目录文件数100软阈值配额，宽限时间70秒")
    rc, pscli_info = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, QUOTA_CREATE_PATH)),
                                                   filenr_quota_cal_type='QUOTA_LIMIT',
                                                   filenr_soft_threshold=100,
                                                   filenr_grace_time=70)
    common.judge_rc(pscli_info['err_no'], 0, "detail_err_msg:%s" % pscli_info['detail_err_msg'])
    rc, quotaid = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, QUOTA_CREATE_PATH)),
                                                u_or_g_type=quota_common.TYPE_CATALOG,)
    common.judge_rc(rc, 0, 'get_one_quota_id failed')
    log.info("2> 触发阈值开始计算时间")
    quota_common.creating_files(quota_common.CLIENT_IP_1, QUOTA_TRUE_PATH, 101, 1, "a")

    log.info("3> 修改主MGR点的系统时间")
    '''获取主MGR节点IP'''
    node_obj = common.Node()
    rc, master_id = quota_common.get_qmgr_id(quotaid)
    common.judge_rc(rc, 0, 'get_qmgr_id failed')
    master_ip = node_obj.get_node_ip_by_id(master_id)
    '''修改系统时间'''
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    log.info("time1 = " + stdout)
    time1 = int(stdout)
    sys_time = time1 - 120
    cmd = 'date -d @%s' % sys_time
    rc, stdout = common.run_command(master_ip, cmd)
    cmd = 'date -s "%s"' % stdout
    common.run_command(master_ip, cmd)

    '''
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    curtime = int(stdout)
    second = 0
    while curtime < time1:
        rc, stdout = common.run_command(master_ip, cmd)
        curtime = int(stdout)
        second += 1
        log.info("wait %s s time1 =%s  curtime=%s   "%(second, time1, stdout))
        time.sleep(1)
    log.info("int(stdout) >= time1")
    '''

    log.info("4> 创建文件，验证在宽限期内能创建")
    quota_common.creating_files(quota_common.CLIENT_IP_1, QUOTA_TRUE_PATH, 1, 1, "b")
    total_inodes = quota_common.dir_total_inodes(quota_common.CLIENT_IP_1, QUOTA_TRUE_PATH)

    log.info("5> 修回系统时间")
    cmd = 'date +%s'
    rc, stdout = common.run_command(master_ip, cmd)
    numerical_time = int(stdout) + 120
    sys_time = str(numerical_time)
    cmd = 'date -d @%s' % sys_time
    rc, stdout = common.run_command(master_ip, cmd)
    common.judge_rc(rc, 0, 'systemtime recovery failed')

    log.info("清除创建的配额")
    rc, quota_id = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, QUOTA_CREATE_PATH)),
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get quota info failed")

    '''删除配额'''
    quota_common.delete_single_quota_config(quota_id)

    if total_inodes != 102:
        common.except_exit('case failed')
    return


def main():
    prepare_clean.defect_test_prepare(FILE_NAME)
    case()
    prepare_clean.defect_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
