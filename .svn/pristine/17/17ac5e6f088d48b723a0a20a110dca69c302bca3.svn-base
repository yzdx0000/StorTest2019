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
import random
####################################################################################
#
# Author: liuping,已通
# date 2018-12-27
# @summary：
#    账户邮箱是否符合要求
# @steps:
#    1、创建账户；
#    2、账户名称中包含特殊字符
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"

global account_name
def judge_result(rc, filename):
    if rc == 0:
        pass
    else:
        result.result(filename, -1)


def case():

    numchars = string.printable[:62]
    numchar_lst = []
    for numchar in  numchars:
        numchar_lst.append(numchar)
    allowchars_lst = ['_', '-'] + numchar_lst
    notallowchar_lst = []
    for str in string.printable[:-5]:
        if str not in allowchars_lst:
            notallowchar_lst.append(str)

    account_name = FILE_NAME + "_account1"

    log.info("1> 验证邮箱中必须包含@和.且不能以@作为开头，且@和.之间必须不能为空")
    email_lst = [FILE_NAME, '@' + FILE_NAME, '.' + FILE_NAME, '@.' + FILE_NAME, FILE_NAME + '@.'+ 'a',
                 FILE_NAME + '@'+'sugon.com']
    for email in email_lst:
        rc, account_id = s3_common.add_account(account_name, email, 0)
        if email.startswith('@') or ('@.' in email) or ('@' not in email) or ('.' not in email):
            if rc == 0:
                judge_result(-1, FILE_NAME)
                common.judge_rc_unequal(rc, 0, "when email is %s, create account succeed,it is wrong" % email)
        else:
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "when email is %s, create account failed,it is wrong" % email)
            rc, stdout = s3_common.find_account(email)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)

            rc, stdout = common.delete_account(account_id=account_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)

    log.info("2> 验证邮箱中每个段都符合命名规则")
    for notallowchar in notallowchar_lst:
        email = '\\' + notallowchar + '@' + '\\'+ notallowchar   + '.' + '\\' + notallowchar
        rc, stdout = s3_common.find_account(email)
        if rc == 0:
            pass
        else:
            rc, account_id = s3_common.add_account(account_name, email, 0)
            if rc == 0:
                judge_result(-1, FILE_NAME)
                common.judge_rc_unequal(rc, 0, "when %s in email,create "
                                               "account succeed,it is wrong" % notallowchar)

    allowchars_lst1 = ['0','a', 'A', '-', '_']
    for allowchar in allowchars_lst1:
        email = allowchar + '@' + allowchar + '.' + allowchar
        rc, stdout = s3_common.find_account(email)
        if rc == 0:
            pass
        else:
            rc, account_id = s3_common.add_account(account_name, email, 0)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "when %s in email, create account failed,it is wrong" % allowchar)
            rc, stdout = s3_common.find_account(email)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "find_account %s failed!!!" % account_name)

            rc, stdout = common.delete_account(account_id=account_id)
            judge_result(rc, FILE_NAME)
            common.judge_rc(rc, 0, "delete_account %s failed!!!" % account_name)

    log.info("3> 验证邮箱长度为5-64")
    email_lst = ['a@q.c',  'a'*53 + '@sugon.com',  'a'*54 + '@sugon.com' , 'a'*55 + '@sugon.com' ]
    for email in email_lst:
        rc, stdout = s3_common.find_account(email)
        if rc == 0:
            pass
        else:
            rc, account_id = s3_common.add_account(account_name, email, 0)
            if (len(email) < 5) or (len(email) > 64):
                if rc == 0:
                    judge_result(-1, FILE_NAME)
                    common.judge_rc_unequal(rc, 0, "when the length of email is %s, create "
                                           "account succeed,it is wrong" % len(email) )
            else:
                judge_result(rc, FILE_NAME)
                common.judge_rc(rc, 0, "when the length of email is %s, create "
                                               "account failed,it is wrong" % len(email))
                rc, stdout = s3_common.find_account(email)
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