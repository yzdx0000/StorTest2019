# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    用邮箱查询执行账户的信息
# @steps:
#    创建账户，创建5个证书，用邮箱获取账户信息
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL_LST = []
ACCOUNT_EMAIL = FILE_NAME+ "@sugon.com"
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

    log.info("3> 查询指定账户的信息")
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    common.judge_rc(rc, 0, "add certificate failed!!!")




def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)