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
# 函数功能：界面自动化-----检查项相关
# 脚本作者：duyuli
# 日期：2019-01-10
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
script_path = "/home/StorTest/test_cases/cases/test_case/P300/WEB"
script_file_list = [
                    "web_testlink_00_check_cluster_name.py",                              # 检查集群名称
                    "web_testlink_01_check_home_stat_node_num.py",                        # 检查首页几点状态
                    "web_testlink_02_check_resource_count.py",                            # 检查集群资源数
                    "web_testlink_03_check_cluster_performance.py",                       # 检查集群性能
                    "web_testlink_04_check_node_operation_info.py",                       # 检查几点运维信息
                    "web_testlink_05_check_node_operation_inside_info.py",                # 检查节点基本信息
                    "web_testlink_06_check_node_operation_inside_network_info.py",        # 检查网络设备
                    "web_testlink_07_check_node_operation_inside_storage_media_info.py",  # 检查存储介质
                    "web_testlink_1-1-1-41_cluster_start_down.py",      # 集群启停
                    # "web_testlink_1-1-1-43.py",                       # 管理ip修改
                    "web_testlink_1-1-1-44_update_data_ip.py",          # 数据ip修改(包含43)
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
        if rc == 0:
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
