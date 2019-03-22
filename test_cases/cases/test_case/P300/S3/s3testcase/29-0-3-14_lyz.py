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
# date 2018-11-19
# @summary：
#    用非法accountid创建证书
# @steps:
#    创建账户，用正确的accountid给账户添加证书，用错误的accountid给账户添加证书
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL_LST = []
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
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

    log.info("2> 给账户添加正确的certificate")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "add certificate failed!!!")

    log.info("3> 用错误的accounid给账户添加certificate")
    change = account_id[0]
    # accountidti替换一位字符
    if change == 'a':
        account_id1 = 'b' + account_id[1:]
    else:
        account_id1 = 'a' + account_id[1:]
    # accountid2比accountid多一位
    account_id2 = account_id+'1'
    # accountid3比accountid少一位
    account_id3 = account_id[:-1]
    rc, certificate_id, certificate = s3_common.add_certificate(account_id1)
    common.judge_rc_unequal(rc, 0, "add certificate use wrong accountid success,that's wrong!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id2)
    common.judge_rc_unequal(rc, 0, "add certificate use wrong accountid success,that's wrong!!!")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id3)
    common.judge_rc_unequal(rc, 0, "add certificate use wrong accountid success,that's wrong!!!")


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
