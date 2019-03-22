# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean

####################################################################################
#
# Author: liuyzhb
# date 2018-11-21
# @summary：
#    验证非法配额创建用户
# @steps:
#    用四种不同的错误quota值创建账户，验证创建失败
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
ACCOUNT_EMAIL_LST = []
ACCOUNT_EMAIL_LST.append(ACCOUNT_EMAIL)
log.info('ACCOUNT_EMAIL_LST is %s' % ACCOUNT_EMAIL_LST)


def case():
    global ACCOUNT_EMAIL
    log.info("1> 用错误的配额值创建账户")
    account_name = FILE_NAME + '_account'
    quota1 = -1
    quota2 = 'a'
    quota3 = '*￥'
    quota4 = 9999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999999
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, quota1)
    common.judge_rc_unequal(rc, 0, "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, quota1))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, quota2)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, quota2))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, quota3)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, quota3))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, quota4)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, quota4))
    """检查账户是否存在"""
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    common.judge_rc_unequal(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
