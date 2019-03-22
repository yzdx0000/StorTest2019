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
#    验证非法账户名称创建用户
# @steps:
#    用三种不同的错误账户名称创建账户，验证创建失败
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
    account_name3 = 'aaaaaaaaabaaaaaaaaabaaaaaaaaabaaaaaaaaabaaaaaaaaabaaaaaaaaabaaaa5'
    account_name4 = 'shishi?'
    account_name5 = 'shishi%'
    log.info("1> 用错误的邮箱值创建账户")
    rc, account_id = s3_common.add_account(account_name3, ACCOUNT_EMAIL, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, 0))
    rc, account_id = s3_common.add_account(account_name4, ACCOUNT_EMAIL, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, 0))
    rc, account_id = s3_common.add_account(account_name5, ACCOUNT_EMAIL, 0)
    common.judge_rc_unequal(rc, 0,
                            "add account %s use wrong quota %s success,that's wrong!!!" % (ACCOUNT_EMAIL, 0))
    log.info("2> 用正确的账户名创建账户")
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
