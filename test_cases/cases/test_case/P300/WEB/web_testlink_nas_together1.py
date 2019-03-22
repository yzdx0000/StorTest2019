# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean
import time
import tool_use

#######################################################
# 函数功能：界面自动化-----多测试用例集合测试(nas相关)
# 脚本作者：duyuli
# 日期：2018-12-25
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
script_path = "/home/StorTest/test_cases/cases/test_case/P300/WEB"
script_file_list = [
                    # "web_testlink_1-1-4-1.py",    # 跨节点池创建访问分区
                    "web_testlink_1-1-4-2_create_az_unused_node.py",               # 跨未用节点创建访问分区
                    "web_testlink_1-1-4-3_az_del_add_node.py",                     # 访问分区中节点移除、添加(包括1)
                    "web_testlink_1-1-4-6_del_az.py",                              # 删除访问分区
                    "web_testlink_1-1-4-7_create_subnet.py",                       # 创建业务子网
                    "web_testlink_1-1-4-8_update_subnet_multi_eth.py",             # 修改业务子网、绑定多网卡
                    "web_testlink_1-1-4-9_update_subnet_by_svip.py",               # 修改业务子网、修改SVIP
                    "web_testlink_1-1-4-10_del_subnet.py",                         # 删除业务子网
                    "web_testlink_1-1-4-11_num2_az_create_subnet.py",              # 第二三个访问分区创建业务子网
                    "web_testlink_1-1-4-12_create_vip_pool_data_ip.py",            # 创建ip池（复用数据网网卡）
                    "web_testlink_1-1-4-13_create_vip_pool_no_ip_eth.py",          # 创建ip池（无ip网卡）
                    "web_testlink_1-1-4-15_create_vip_pool_balance_strategy.py",   # 修改ip池，修改负载均衡策略
                    "web_testlink_1-1-4-16_del_vip_pool.py",                       # 删除ip池
                    "web_testlink_1-1-4-17_num2_az_update_vip.py",                 # 第二个访问分区创建IP池后，修改VIP地址
                    "web_testlink_1-1-4-18_num3_az_update_balance_strategy.py",    # 第三个访问分区创建IP池后，修改负载均衡策略
                    "web_testlink_1-1-4-19_num1_az_create_group_user.py",          # 第一个访问分区创建用户组用户
                    "web_testlink_1-1-4-20_num2_az_create_group_user.py",          # 第二个访问分区创建用户组用户
                    "web_testlink_1-1-4-21_num3_az_create_group_user.py",          # 第三个访问分区创建用户组用户
                    "web_testlink_1-1-4-22_ftp.py",                                # 第一个访问分区导出ftp共享
                    "web_testlink_1-1-4-23_nfs.py",                                # 第二个访问分区导出nfs共享
                    "web_testlink_1-1-4-24_smb.py",                                # 第二个访问分区导出smb共享
                    "web_testlink_1-1-4-26_disable_nas.py"                         # nas服务单独启停，全部启停
                   ]

def case():
    for script_file in script_file_list:
        start_time = time.time()
        log.info("start %s" % script_file)
        test_file_path = os.path.join(script_path, script_file)
        rc = os.system("python -u " + test_file_path)

        """判断是否上传结果到testlink"""
        end_time = time.time()
        run_time = end_time - start_time
        if 0 == rc:
            if get_config.get_tl():
                tool_use.report_tl_case_result(test_file_path, 'p', run_time)
        else:
            if get_config.get_tl():
                tool_use.report_tl_case_result(test_file_path, 'f', run_time)
            log.info("case %s failed" % script_file)
            raise Exception("unexpected result")


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
