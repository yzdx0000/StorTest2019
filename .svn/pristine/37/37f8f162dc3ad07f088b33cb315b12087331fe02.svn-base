# -*-coding:utf-8 -*

import os
import utils_path

import log
import common
import web_common
import prepare_clean


#######################################################
# 函数功能：界面自动化-----检查所有事件界面搜索功能
# 脚本作者：duyuli
# 日期：2018-12-14
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
nis_name = "nis_server"
nis_name_update = "nis_update"
start_time = "2018-01-14 00:00:00"


def case():
    driver = web_common.init_web_driver()

    obj_web_alarm_events = web_common.Alarms_Events(driver)

    # 获取当前集群时间
    cluster_time_now = obj_web_alarm_events.get_cluster_time()

    # 按 时间+描述 搜索
    obj_web_alarm_events.all_events_search_function(happen_time="custom",
                                                    desc_or_level="desc",
                                                    start_time=start_time,
                                                    end_time=cluster_time_now,
                                                    description="网口链接异常")

    # 按 时间+级别 搜索
    obj_web_alarm_events.all_events_search_function(happen_time="custom",
                                                    desc_or_level="level",
                                                    start_time=start_time,
                                                    end_time=cluster_time_now,
                                                    level="0")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
