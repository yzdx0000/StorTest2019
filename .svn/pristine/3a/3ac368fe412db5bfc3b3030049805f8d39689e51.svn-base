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
#    非法 accountid删除账户
# @steps:
#    创建账户
#    用非法accounid删除账户
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
ACCOUNT_EMAIL_LST = []
ACCOUNT_EMAIL_LST.append(ACCOUNT_EMAIL)
log.info('ACCOUNT_EMAIL_LST is %s' %ACCOUNT_EMAIL_LST)


def case():
    global ACCOUNT_EMAIL
    account_name = FILE_NAME + '_account'
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "add account failed!!!")
    """检查账户是否存在"""
    rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
    common.judge_rc(rc, 0, "find account %s failed!!!" % ACCOUNT_EMAIL)

    log.info("1> 用错误的accountid删除账户")
    change = account_id[0]
    # accountidti替换一位字符
    if change == 'a':
        account_id1 = 'b' + account_id[1:]
    else:
        account_id1 = 'a' + account_id[1:]
    # accountid2比accountid多一位
    account_id2 = account_id + '1'
    # accountid3比accountid少一位
    account_id3 = account_id[:-1]
    rc, out = s3_common.del_account(account_id1)
    common.judge_rc_unequal(rc, 0, "delete account %s use wrong accountid %s success ,that is worng!!!"
                    % (ACCOUNT_EMAIL, account_id1))
    rc, out = s3_common.del_account(account_id2)
    common.judge_rc_unequal(rc, 0, "delete account %s use wrong accountid %s success ,that is worng!!!"
                            % (ACCOUNT_EMAIL, account_id2))
    rc, out = s3_common.del_account(account_id3)
    common.judge_rc_unequal(rc, 0, "delete account %s use wrong accountid %s success ,that is worng!!!"
                            % (ACCOUNT_EMAIL, account_id3))

def main():
    prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
    case()
    prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)