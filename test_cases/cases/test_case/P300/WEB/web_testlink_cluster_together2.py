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
                    # "web_testlink_1-1-1-8.py",                                # 扩容节点池
                    # "web_testlink_1-1-1-9.py",                                # 第二个节点池删除、扩容
                    "web_testlink_1-1-1-15_expand_node_pool_by_node.py",        # 扩容节点池（添加节点）(包括8、9、18)
                    "web_testlink_1-1-1-13_expand_storage.py",                  # 扩容文件存储池（扩容界面）
                    # "web_testlink_1-1-1-14.py",                               # 扩容文件存储池（添加磁盘）
                    "web_testlink_1-1-1-16_num2_storage_del_data_disk.py",      # 第二个存储池数据盘删除（包含14）
                    "web_testlink_1-1-1-17_num2_node_pool_del_shared_disk.py",  # 第二个节点池元数据盘删除
                    # "web_testlink_1-1-1-18.py",                               # 第三个存储池节点删除
                    "web_testlink_1-1-1-22_del_storage_pool.py",                # 所有存储池删除（包含27、28）
                    # "web_testlink_1-1-1-23.py",                               # 创建对象存储池(对象存储池无法删除，不作为循环跑)
                    "web_testlink_1-1-1-26_update_volume.py",                   # 修改文件系统（配额相关）
                    # "web_testlink_1-1-1-27.py",                               # 删除文件系统
                    # "web_testlink_1-1-1-28.py",                               # 第二个、第三个存储池文件系统的创建
                    "web_testlink_1-1-1-29_posix_multi_volume.py",              # 批量授权客户端（多个卷）
                    "web_testlink_1-1-1-30_posix_single_volume.py",             # 批量授权客户端（单个卷）
                    "web_testlink_1-1-1-31_posix_ip_multi_line.py",             # 单个卷，换行授权
                    "web_testlink_1-1-1-32_update_posix_auto_mount.py",         # 修改授权，取消、添加自动挂载
                    "web_testlink_1-1-1-33_num2_storage_volume_posix.py",       # 对第二个、第三存储池中的文件系统进行授权
                    "web_testlink_1-1-1-34_update_posix_by_ip.py",              # 修改授权（修改ip地址）
                    "web_testlink_1-1-1-35_update_posix_by_volume.py",          # 修改授权（修改卷）（包含36）
                    # "web_testlink_1-1-1-36.py",                               # 删除授权
                    "web_testlink_1-1-1-47_dir_quota.py",                       # 目录配额测试（有读写业务）
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
