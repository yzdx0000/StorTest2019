# -*-coding:utf-8 -*

#######################################################
# 脚本作者：姜晓光
# 脚本说明：反复创建删除10条配额
#######################################################

import os
import time

import utils_path
import common
import quota_common


def quota_main():
    count = 10

    while 1:
        for i in range(1, count + 1):
            dir = "/mnt/parastor/quota_test_dir%s" % i
            print dir
            quota_common.creating_dir(quota_common.CLIENT_IP_1, dir)

            quota_dir = os.path.basename(dir)
            rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, quota_dir)),
                                                             auth_provider_id=1,
                                                             filenr_quota_cal_type='QUOTA_LIMIT',
                                                             filenr_hard_threshold=2000)
            common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

        time.sleep(10)

        quota_common.delete_all_quota_config()


class Quota_Class_quota_test():
    def quota_method_quota_test(self):
        common.case_main(quota_main)


if __name__ == '__main__':
    common.case_main(quota_main)