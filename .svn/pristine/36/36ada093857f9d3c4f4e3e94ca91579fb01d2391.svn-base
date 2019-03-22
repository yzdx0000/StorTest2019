#!/usr/bin/python
# -*-coding:utf-8 -*
import os
import string
import utils_path
import common
import s3_common
import log
import prepare_clean
import result
####################################################################################
#
# Author: liuping,已通
# date 2018-12-27
# @summary：
#    账户名称命名规则
# @steps:
#    1、创建账户；
#    2、账户名称中包含特殊字符
#    3、以特殊字符作为首字母
#    4、账户名长度最小是1，最大是64
#    5、清理环境
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"


def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


def case():

    puncchars = string.punctuation
    puncchar_lst = []
    for puncchar in puncchars:
        puncchar_lst.append(puncchar)
    puncchar_lst.append(' ')
    allowchars_lst = ['+', '=', ',', '.', '@', '_', '-']

    for puncchar in  puncchar_lst:
        log.info("1> 账户名称中含有特殊字符%s" % puncchar)
        account_name = FILE_NAME + "\\" + puncchar + "account1"
        log.info("创建账户%s" % account_name)
        rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
        if puncchar not in allowchars_lst:
            if rc == 0:
                judge_result(-1, FILE_NAME)
                common.judge_rc_unequal(rc, 0, "When %s in accountname,create account succeed,it is wrong" % puncchar)
            else:
                log.info("When %s in accountname,create account failed,it is right" % puncchar)
        else:
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "When %s in accountname,create account failed,it is wrong" % puncchar)
            log.info("When %s in accountname,create account succeed,it is right" % puncchar)

            log.info("Check if account %s exists after the account is created successfully" % account_name)
            rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)

            log.info("Delete account when account %s exists." % account_name)
            rc, stdout = common.delete_account(account_id=account_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)

    startchar_lst = ['a','1'] + allowchars_lst
    for startchar in startchar_lst:
        log.info("2> 账户名称以字符%s作为开头" % startchar)
        account_name = startchar + FILE_NAME
        log.info("创建账户%s" % account_name)
        rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
        if startchar == '.':
            if rc == 0:
                judge_result(-1, FILE_NAME)
                common.judge_rc_unequal(rc, 0, "when accountname starts with %s,create account succeed,"
                                               "it is wrong" % startchar)
            log.info("when accountname starts with %s,create account failed,it is right" % startchar)
        else:
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "when accountname starts with %s,create account failed,"
                                       "it is wrong" % startchar)
            log.info("when accountname starts with %s,create account succeed,it is right" % startchar)

            log.info("Check if account %s exists after the account is created successfully" % account_name)
            rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)

            log.info("Delete account when account %s exists." % account_name)
            rc, stdout = common.delete_account(account_id=account_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)

    log.info("3> 账户名称最小为1个字符，最大是64个字符")
    account_name_lst = [ ' ', 'z ', FILE_NAME + 'a'* (63 -len(FILE_NAME)), FILE_NAME + 'a'* (64 -len(FILE_NAME)),
                        FILE_NAME + 'a' * (65 - len(FILE_NAME))]
    for account_name in account_name_lst:
        rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
        if account_name == ' ':
            if rc == 0:
                judge_result(-1, FILE_NAME)
                common.judge_rc_unequal(rc, 0, "when the length is 0.create account succeed,it is wrong")
        elif account_name != ' ' and len(account_name) <= 64:
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "the length of accountname is [1,64],create account failed,it is wrong")
            rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)
            rc, stdout = common.delete_account(account_id=account_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)
        else:
            if rc == 0:
                rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
                judge_result(rc, FILE_NAME)
                stdout = common.json_loads(stdout)
                account_name = stdout['result']['account_name']
                if len(account_name) != 64:
                    judge_result(-1, FILE_NAME)
                    common.judge_rc(-1, 0, "the length of accountname is 65,create account succeed,it is wrong")
                rc, stdout = s3_common.find_account(ACCOUNT_EMAIL)
                judge_result(rc, FILE_NAME)
                common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)
                rc, stdout = common.delete_account(account_id=account_id)
                judge_result(rc, FILE_NAME)
                common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)

    log.info('%s success!' % FILE_NAME)
    result.result(FILE_NAME, 0)


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL], env_check=False)
    case()
    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s finish!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)