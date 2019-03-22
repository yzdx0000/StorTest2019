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
#    验证非法邮箱创建用户
# @steps:
#    用五种不同的错误邮箱创建账户，验证创建失败
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
    account_name = FILE_NAME + '_account'
    log.info("1> 用错误的邮箱值创建账户")
    ACCOUNT_EMAIL1 = FILE_NAME
    ACCOUNT_EMAIL2 = FILE_NAME + "@"
    ACCOUNT_EMAIL3 = FILE_NAME + "@sugon"
    ACCOUNT_EMAIL4 = "@sugon.com"
    ACCOUNT_EMAIL5 = FILE_NAME + "@sugon.com*？"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL1, 0)
    common.judge_rc_unequal(rc, 0, "add account %s use wrong quota %s success,that's wrong!!!" % ( ACCOUNT_EMAIL1, 0))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL2, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL2, 0))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL3, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL3, 0))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL4, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL4, 0))
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL5, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL5, 0))
    log.info("2> 用正确的邮箱值创建账户")
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "add certificate failed!!!")
    """检查账户是否存在"""
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)

