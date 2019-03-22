# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：创建5万条同时含inode、用户和用户组的配额，用户和用户组
#         名称使用同一个
#######################################################

import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log
import shell
import get_config
import json


def quota_main():
    # 创建用户和用户组
    quota_common.preparing_zone_nas()
    auth_provider_id = quota_common.get_auth_provider_id_with_access_zone_name(quota_common.QUOTA_ACCESS_ZONE)
    quota_common.create_designated_quota_user_and_group_new(quota_common.NOTE_IP_1, auth_provider_id)
    count = 16666

    for i in range(1, count + 1):
        dir = "%s%s" % (quota_common.QUOTA_PATH, i)
        print dir
        quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)

        quota_dir = os.path.basename(dir)
        rc, pscli_info = quota_common.create_one_quota('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir),
                                                       filenr_quota_cal_type='QUOTA_LIMIT',
                                                       filenr_hard_threshold=500,
                                                       filenr_soft_threshold=100,
                                                       filenr_grace_time=1,
                                                       filenr_suggest_threshold=10,
                                                       logical_quota_cal_type='QUOTA_LIMIT',
                                                       logical_hard_threshold=81920,
                                                       logical_soft_threshold=16384,
                                                       logical_grace_time=1,
                                                       logical_suggest_threshold=4096)
        common.judge_rc(rc, 0, "create_one_quota failed")

        rc, pscli_info = quota_common.create_one_quota('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir),
                                                       auth_provider_id=auth_provider_id,
                                                       filenr_quota_cal_type='QUOTA_LIMIT',
                                                       filenr_hard_threshold=500,
                                                       filenr_soft_threshold=100,
                                                       filenr_grace_time=1,
                                                       filenr_suggest_threshold=10,
                                                       logical_quota_cal_type='QUOTA_LIMIT',
                                                       logical_hard_threshold=81920,
                                                       logical_soft_threshold=16384,
                                                       logical_grace_time=1,
                                                       logical_suggest_threshold=4096,
                                                       user_type=quota_common.TYPE_USER,
                                                       user_or_group_name=quota_common.QUOTA_USER)
        common.judge_rc(rc, 0, 'create_one_quota failed')
        rc, pscli_info = quota_common.create_one_quota('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir),
                                                       auth_provider_id=auth_provider_id,
                                                       filenr_quota_cal_type='QUOTA_LIMIT',
                                                       filenr_hard_threshold=500,
                                                       filenr_soft_threshold=100,
                                                       filenr_grace_time=1,
                                                       filenr_suggest_threshold=10,
                                                       logical_quota_cal_type='QUOTA_LIMIT',
                                                       logical_hard_threshold=81920,
                                                       logical_soft_threshold=16384,
                                                       logical_grace_time=1,
                                                       logical_suggest_threshold=4096,
                                                       user_type=quota_common.TYPE_GROUP,
                                                       user_or_group_name=quota_common.QUOTA_GROUP)
        common.judge_rc(rc, 0, 'create_one_quota failed')

    return


class Quota_Class_quota_test_2():
    def quota_method_quota_test_2(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    #    print "__file__ = %s" %__file__
    #    print "__name__ = %s" %__name__
    common.case_main(quota_main)
