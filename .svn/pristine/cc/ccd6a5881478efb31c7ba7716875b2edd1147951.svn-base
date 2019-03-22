#-*-coding:utf-8 -*
import os

import utils_path
import common
import quota_common
import nas_common
import log
import prepare_clean


FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字


def case():
    """
    authou:liyi
    date:2018-10-05
    description:创建配额用户和用户组
    :return:
    """
    log.info("1> 创建访问分区")
    node_ids = nas_common.get_node_ids()
    pscli_info = nas_common.create_access_zone(node_ids=node_ids, name=quota_common.QUOTA_ACCESS_ZONE)
    common.judge_rc(pscli_info['err_no'], 0, "create_access_zone failed")
    access_zone_id = pscli_info['result']
    log.info("2> 启动nas")
    pscli_info = nas_common.enable_nas(access_zone_id=access_zone_id)
    common.judge_rc(pscli_info['err_no'], 0, "enable_nas failed")
    pscli_info = nas_common.get_access_zones(ids=access_zone_id)
    auth_provider_id = pscli_info["result"]["access_zones"][0]["auth_provider_id"]
    log.info("3> 创建用户组")
    pscli_info = nas_common.create_auth_group(auth_provider_id=auth_provider_id, name=quota_common.QUOTA_GROUP)
    primary_group_id = pscli_info['result']
    log.info("4> 创建用户")
    log.info("4.1> 创建用户:quota_user")
    nas_common.create_auth_user(auth_provider_id, quota_common.QUOTA_USER, '111111', primary_group_id)
    log.info("4.2> 创建用户:quota_other_user")
    nas_common.create_auth_user(auth_provider_id, quota_common.QUOTA_OTHER_USER, '111111', primary_group_id)

    return


def main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    case()
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
