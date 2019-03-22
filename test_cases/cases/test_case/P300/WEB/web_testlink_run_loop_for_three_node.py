# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----多用例循环跑
# 脚本作者：duyuli
# 日期：2018-12-27
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
script_path = "/home/StorTest/test_cases/cases/test_case/P300/WEB"
script_file_list = [
                    "web_testlink_for_three_node_1.py",   # 部署相关集合
                    "web_testlink_for_three_node_2.py",   # 扩容、修改、删除相关
                    "web_testlink_nas_together1.py",      # nas相关
                    "web_testlink_check_together1.py",    # 检查界面信息
                    "web_testlink_cluster_together3.py",  # 卸载集群
                   ]

def case():
    count = 100
    for i in range(count):
        log.info("##################### run for %s times #####################" % i)
        for script_file in script_file_list:
            log.info("start %s" % script_file)
            test_file_path = os.path.join(script_path, script_file)
            rc = os.system("python -u " + test_file_path)
            if 0 != rc:
                log.info("case %s failed" % script_file)
                raise Exception("unexpected result")
        count += 1
        log.info("############################################################")

def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
