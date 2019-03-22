# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：11-3-1-10 【稳定性】配置修改过程中主oPara节点全部网
#                   络故障
# 修改时间：20181109 duyuli：修改全部网络断开pscli不能执行的问题
#######################################################

import os
import time
import multiprocessing
from multiprocessing import Process

import utils_path
import log
import common
import make_fault
import quota_common
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]              # 本脚本名字


def update_quota_when_all_data_net_fault(subprocess_list):
    # 多次修改配额规则
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, quota_id = quota_common.get_one_quota_id(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                 u_or_g_type=quota_common.TYPE_CATALOG)
    common.judge_rc(rc, 0, "get_one_quota_id failed")

    rc, check_result2 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_suggest_threshold=2000,
                                            filenr_soft_threshold=3000,
                                            filenr_grace_time=5,
                                            filenr_hard_threshold=4000,
                                            logical_quota_cal_type='QUOTA_LIMIT',
                                            logical_suggest_threshold=2147483648,
                                            logical_soft_threshold=3221225472,
                                            logical_grace_time=10,
                                            logical_hard_threshold=4294967296,
                                            fault_node_ip=subprocess_list[0])
    check_result2 = common.json_loads(check_result2)
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)

    rc, check_result3 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_COMPUTE',
                                            logical_quota_cal_type='QUOTA_LIMIT',
                                            logical_suggest_threshold=1073741824,
                                            logical_soft_threshold=2147483648,
                                            logical_grace_time=1,
                                            logical_hard_threshold=3221225472,
                                            fault_node_ip=subprocess_list[0])
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result3 = common.json_loads(check_result3)

    rc, check_result4 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_suggest_threshold=1000,
                                            filenr_soft_threshold=2000,
                                            filenr_grace_time=1,
                                            filenr_hard_threshold=3000,
                                            logical_quota_cal_type='QUOTA_COMPUTE',
                                            fault_node_ip=subprocess_list[0])
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result4 = common.json_loads(check_result4)

    rc, check_result5 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_COMPUTE',
                                            logical_quota_cal_type='QUOTA_COMPUTE',
                                            fault_node_ip=subprocess_list[0])
    common.judge_rc(rc, 0, "update quota failed", exit_flag=False)
    check_result5 = common.json_loads(check_result5)

    # 修改成不合法的配额规则
    rc, check_result6 = common.update_quota(id=quota_id,
                                            filenr_quota_cal_type='QUOTA_LIMIT',
                                            filenr_suggest_threshold=4000,
                                            filenr_soft_threshold=3000,
                                            filenr_grace_time=5,
                                            filenr_hard_threshold=2000,
                                            logical_quota_cal_type='QUOTA_LIMIT',
                                            logical_suggest_threshold=2147483648,
                                            logical_soft_threshold=3221225472,
                                            logical_grace_time=10,
                                            logical_hard_threshold=4294967296,
                                            fault_node_ip=subprocess_list[0],
                                            print_flag=False)
    check_result6 = common.json_loads(check_result6)

    # 结果检查
    if (check_result2["err_no"] != 0 or
            check_result3["err_no"] != 0 or
            check_result4["err_no"] != 0 or
            check_result5["err_no"] != 0 or
            "Soft threshold value must larger than" not in check_result6["detail_err_msg"]):
        log.info("check_result6:%s" % check_result6["detail_err_msg"])
        raise Exception("update_quota_when_all_data_net_fault is failed!")
    return


def all_data_net_fault_when_update_quota(subprocess_list, process_name):
    # 进程名 -> 节点id -> 节点管理ip -> 节点业务ip
    # 获取主oPara进程所在节点的id
    process_node_id = quota_common.get_master_process_node_id(process_name)
    if process_node_id != 250:
        # 获取主oPara进程所在的节点的管理ip
        node_manage_ip = quota_common.get_node_ip_by_id(process_node_id)
        subprocess_list.append(node_manage_ip)
    else:
        raise Exception("get oPara master id failed")

    # 获取故障节点的数据ip
    cmd = "ifconfig | grep -E \"inet 20|inet 30\""
    rc, stdout = common.run_command(node_manage_ip, cmd)
    common.judge_rc(rc, 0, "quota_11_3_1_10 failed", exit_flag=False)

    # 获取20,30网段的数据ip
    data_ip_20_net = stdout.split()[1]
    data_ip_30_net = stdout.split()[7]
    print data_ip_20_net
    print data_ip_30_net

    # 根据ip获取网口名称
    cmd = "ip a| grep -E \"%s|%s\"" % (data_ip_20_net, data_ip_30_net)
    rc, stdout = common.run_command(node_manage_ip, cmd)
    common.judge_rc(rc, 0, "get_ifc_failed", exit_flag=False)

    print stdout.split()
    eth_name_20 = stdout.split()[6]
    eth_name_30 = stdout.split()[13]
    subprocess_list.append(eth_name_20)
    subprocess_list.append(eth_name_30)

    # 根据网口名称down网口,down之前等待p1进程执行一会
    time.sleep(20)
    rc = make_fault.down_eth(node_manage_ip, [eth_name_20, eth_name_30])
    common.judge_rc(rc, 0, "down_ifc_failed", exit_flag=False)
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def executing_case():
    print "（2）executing_case"
    subprocess_list = multiprocessing.Manager().list()

    '''
    1、测试执行
    2、结果检查
    '''
    # 测试执行

    p2 = Process(target=all_data_net_fault_when_update_quota, args=(subprocess_list, "oPara"))
    p2.start()
    time.sleep(10)  # 等待p2写入数据
    p1 = Process(target=update_quota_when_all_data_net_fault, args=(subprocess_list,))
    p1.start()

    p1.join()
    p2.join()

    # 根据网口名称up网口来恢复网络环境
    rc = make_fault.up_eth(subprocess_list[0], [subprocess_list[1], subprocess_list[2]])
    common.judge_rc(rc, 0, "up_ifc_failed", exit_flag=False)

    # 结果检查
    if p1.exitcode != 0:
        raise Exception("11-3-1-10 Failed")
    else:
        print "11-3-1-10 Succeed"
    return


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    print "（1）preparing_environment"

    quota_common.creating_dir(quota_common.CLIENT_IP_1, quota_common.QUOTA_PATH)
    quota_dir = quota_common.QUOTA_PATH_BASENAME
    rc, check_result1 = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                      filenr_quota_cal_type='QUOTA_LIMIT',
                                                      filenr_suggest_threshold=1000,
                                                      filenr_soft_threshold=2000,
                                                      filenr_grace_time=1,
                                                      filenr_hard_threshold=3000,
                                                      logical_quota_cal_type='QUOTA_LIMIT',
                                                      logical_suggest_threshold=1073741824,
                                                      logical_soft_threshold=2147483648,
                                                      logical_grace_time=1,
                                                      logical_hard_threshold=3221225472)
    common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
    '''
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    prepare_clean.test_prepare(FILE_NAME)
    quota_common.cleaning_environment()
    preparing_environment()
    executing_case()
    if quota_common.DEBUG != "on":
        quota_common.cleaning_environment()
    log.info("%s succeed" % FILE_NAME)
    return


class Quota_Class_11_3_1_10():
    def quota_method_11_3_1_10(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)