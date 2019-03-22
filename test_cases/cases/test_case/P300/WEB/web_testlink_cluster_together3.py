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
# 函数功能：界面自动化-----多测试用例集合测试
# 脚本作者：duyuli
# 日期：2018-12-25
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
script_path = "/home/StorTest/test_cases/cases/test_case/P300/WEB"
script_file_list = [
                    "web_testlink_1-1-1-46_uninstall_gui.py",      # 卸载gui
                    "web_testlink_1-1-1-45_uninstall.py",             # 存储系统卸载
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
