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
# date 2018-011-20
# @summary：
#  用错误的邮箱查询执行账户的信息
# @steps:
#    s3的基础指令集包括：创建账户，给账户创建5个证书，用错误的邮箱查看执行账户的信息
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL_LST = []
ACCOUNT_EMAIL = FILE_NAME  + "@sugon.com"
ACCOUNT_EMAIL_LST.append(ACCOUNT_EMAIL)


def case():
    global ACCOUNT_EMAIL
    log.info("1> 创建账户")
    i = 0
    account_name = FILE_NAME + '_account_%d' % i
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "add account failed!!!")
    """检查账户是否存在"""
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    log.info("2> 给账户添加5个正确的certificate")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")

    log.info("3> 用错误的邮箱查询指定账户的信息")
    change = ACCOUNT_EMAIL[0:2]
    # accountidti替换一位字符
    if change == 'aa':
        ACCOUNT_EMAIL1 = 'no' + account_id[2:]
    else:
        ACCOUNT_EMAIL1 = 'aa' + account_id[2:]
    # accountid2比accountid多位几
    ACCOUNT_EMAIL2 = account_id + 'noexist'
    # accountid3比accountid少3位
    ACCOUNT_EMAIL3 = account_id[:-3]
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL1)
    common.judge_rc_unequal(rc, 0, "find account user wrong email success,that's wrong!!!")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL2)
    common.judge_rc_unequal(rc, 0, "find account user wrong email success,that's wrong!!!")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL3)
    common.judge_rc_unequal(rc, 0, "find account user wrong email success,that's wrong!!!")




def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
