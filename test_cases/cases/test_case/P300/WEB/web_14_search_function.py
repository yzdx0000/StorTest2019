# -*-coding:utf-8 -*

import os
import random

import utils_path
import log
import common
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----界面搜索功能
# 脚本作者：duyuli
# 日期：2018-12-18
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
# 节点运维搜索相关
name_value = "vm102"
healthy_state_value = random.choice(["abnormal", "normal", "abnormal", "unknown"])
running_state_value = random.choice(["normal", "maintaining", "deleting", "reinstalling", "shutdown", "maintaining",
                                     "prepare_maintaining", "prepare_online", "zombie", "unknown"])
# 任务概览搜索相关
type_value = random.choice(["JOB_ENGINE_REPAIR", "JOB_ENGINE_REBUILD", "JOB_ENGINE_BALANCE", "JOB_ENGINE_CONCHK",
                            "JOB_ENGINE_BBS", "JOB_ENGINE_RMFS", "JOB_ENGINE_SNAPSHOT_REVERT", "JOB_ENGINE_DIRQUOTA",
                            "JOB_ENGINE_RMSTOREPOOL"])
state_value = random.choice(["JOB_ENGINE_WAIT", "JOB_ENGINE_ACTIVE", "JOB_ENGINE_PAUSE"])
priority_value = str(random.randrange(11))
impact_value = random.choice(["HIGH", "MIDDLE", "LOW"])
result_value = random.choice(["0", "-1"])


def case():
    driver = web_common.init_web_driver()

    obj_web_node = web_common.Node_Operation(driver)
    obj_web_job = web_common.Job_Manage(driver)
    obj_web_params = web_common.Params_Config(driver)
    obj_web_nodepool = web_common.Node_Pool(driver)
    obj_web_storage_pool = web_common.Storage_Pool(driver)

    # 节点运维界面按名称、健康状态、运行状态搜索功能
    obj_web_node.search_function_for_node_operation(search_option="name",
                                                    name_value=name_value)
    obj_web_node.search_function_for_node_operation(search_option="healthy_state",
                                                    healthy_state_value=healthy_state_value)
    obj_web_node.search_function_for_node_operation(search_option="running_state",
                                                    running_state_value=running_state_value)

    # 任务概览界面按任务名称、运行状态、优先级、影响度搜索功能
    obj_web_job.search_function_for_job_overview(search_option="type", type_value=type_value)
    obj_web_job.search_function_for_job_overview(search_option="state", state_value=state_value)
    obj_web_job.search_function_for_job_overview(search_option="priority", priority_value=priority_value)
    obj_web_job.search_function_for_job_overview(search_option="impact", impact_value=impact_value)

    # 任务配置界面按任务名称、运行状态、优先级、影响度搜索功能
    obj_web_job.search_function_for_job_config(search_option="type", type_value=type_value)
    obj_web_job.search_function_for_job_config(search_option="state", state_value=state_value)
    obj_web_job.search_function_for_job_config(search_option="priority", priority_value=priority_value)
    obj_web_job.search_function_for_job_config(search_option="impact", impact_value=impact_value)

    # 历史任务界面按名称、执行结果搜索功能
    obj_web_job.search_function_for_job_history(search_option="type", type_value=type_value)
    obj_web_job.search_function_for_job_history(search_option="result", result_value=result_value)

    # 参数配置界面按名称搜索功能
    obj_web_params.search_function_for_params_config(name="name", name_value="时间")

    # 节点池界面按名称、冗余配比、节点列表、备注搜索
    obj_web_nodepool.search_function_for_node_pool(search_option="name", name_value="node_pools")
    obj_web_nodepool.search_function_for_node_pool(search_option="redundancy_ratio", redundancy_ratio_value="4+2:1")
    obj_web_nodepool.search_function_for_node_pool(search_option="nodelist", nodelist_value="vm151")
    obj_web_nodepool.search_function_for_node_pool(search_option="remark", remark_value="111")

    # 存储池界面按名称、服务类型搜索
    obj_web_storage_pool.search_function_for_storage_pool(search_option="name", name_value="shared")
    obj_web_storage_pool.search_function_for_storage_pool(search_option="type", type_value="FILE")

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
