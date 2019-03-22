# -*-coding:utf-8 -*
import os
import time
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean
import tool_use

#######################################################
# 函数功能：界面自动化-----多测试用例集合测试
# 脚本作者：duyuli
# 日期：2018-12-25
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
script_path = "/home/StorTest/test_cases/cases/test_case/P300/WEB"
script_file_list = [
                    "web_testlink_1-1-1-1_install_gui.py",                 # 安装gui
                    "web_testlink_1-1-1-4_5_install.py",                   # 部署3节点集群
                    "web_testlink_1-1-1-6_create_node_pool.py",            # 批量节点池（4+2:1）
                    "web_testlink_1-1-1-11_create_storage_part_disk.py",   # 创建存储池（部分盘，物理机）
                    "web_testlink_1-1-1-12_create_storage_all_disk.py",    # 创建存储池(1个)
                    "web_testlink_1-1-1-25_for_three_node.py"              # 创建文件系统(2个)
                    ]
def case():
    # 如果是虚拟机，去掉1个用例
    vir_pyh = get_config.get_web_machine()
    if vir_pyh == "vir":
        script_file_list.remove("web_testlink_1-1-1-11_create_storage_part_disk.py")

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
