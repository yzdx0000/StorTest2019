# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import get_config
import log
import prepare_clean
import remote
import nas_common

##########################################################################
#
# Author: zhanghan
# date 2018-11-22
# @summary：
#    posix客户端权限测试：对文件进行chattr +i操作，检验文件权限；原P200测试用例23-0-8-9。
# @steps:
#    脚本运行前准备工作：a) 配置访问管理，包括访问区、Local认证服务器；并将相关信息写入配置文件
#                        b) posix客户端授权并手动挂载，并将相应信息写入配置文件
#
#    1、获取节点信息:posix客户端ip、posix客户端挂载路径；
#    2、创建测试目录并将权限修改为777；
#    3、测试主体，对文件进行chattr +i操作，检验文件权限；
#
# @changelog：
##########################################################################

#################### 全局变量 ####################
FILE_NAME = os.path.splitext(os.path.basename(__file__))[
    0]                 # 本脚本名字
FILE_NAME = FILE_NAME.replace('-', '_')
posix_file_dir = "posix_dir" + FILE_NAME


def case():
    log.info("1> 获取节点信息")

    client_ip = get_config.get_client_ip()
    log.info("posix client ip is: %s" % client_ip)

    # posix客户端需要预先手动挂载，且挂载目录需要与卷名称相同
    posix_mount_path = get_config.get_one_mount_path()
    log.info("posix_mount_path is: %s" % posix_mount_path)

    posix_file_location = os.path.join(posix_mount_path, posix_file_dir)
    log.info("posix_file_location is: %s" % posix_file_location)

    log.info("2> 创建测试目录")
    rc = common.command(
        "ssh %s \"mkdir %s\"" %
        (client_ip, posix_file_location))
    common.judge_rc(rc, 0, "mkdir posix_file_location failed")
    rc = common.command(
        "ssh %s \"chmod %s %s\"" %
        (client_ip, "777", posix_file_location))
    common.judge_rc(rc, 0, "chmod posix_file_location failed")

    log.info("3> 测试主体：对文件进行chown操作，检验文件权限")
    log.info("3-1> 创建测试文件并设置权限644")
    testfile = 'file_' + FILE_NAME
    cmd = "ssh %s \"cd %s;touch %s;chmod 644 %s\" " % (
        client_ip, posix_file_location, testfile, testfile)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "touch testfile failed")
    log.info("3-2> 修改文件的attr, chattr +i")
    cmd = "ssh %s \"cd %s;chattr +i %s\"" % (
        client_ip, posix_file_location, testfile)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "chattr failed")
    log.info("3-3> 对文件进行追加写操作")
    echo_content = "hello, world"
    cmd = "ssh %s \"cd %s;echo %s >> %s\"" % (
        client_ip, posix_file_location, echo_content, testfile)
    rc = common.command(cmd)
    common.judge_rc_unequal(
        rc, 0, "user root, echo >> success, the attr dosen't take effect")
    log.info("3-4> 对文件进行删除操作")
    cmd = "ssh %s \"cd %s;rm -fr %s\"" % (client_ip,
                                          posix_file_location, testfile)
    rc = common.command(cmd)
    common.judge_rc_unequal(
        rc, 0, "rm file success, the attr dosen't take effect")
    log.info("3-5> 修改文件的attr, chattr -i")
    cmd = "ssh %s \"cd %s;chattr -i %s\"" % (
        client_ip, posix_file_location, testfile)
    rc = common.command(cmd)
    common.judge_rc(rc, 0, "chattr failed")
    log.info("3-6> 对文件进行追加写操作")
    cmd = "ssh %s \"cd %s;echo %s >> %s\"" % (
        client_ip, posix_file_location, echo_content, testfile)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "user root, echo >> failed, the attr dosen't take effect")
    log.info("3-7> 对文件进行删除操作")
    cmd = "ssh %s \"cd %s;rm -fr %s\"" % (client_ip,
                                          posix_file_location, testfile)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "rm file failed, the attr dosen't take effect")
    log.info("3-8> testfile权限检测成功，删除测试目录%s" % posix_file_location)
    cmd = "ssh %s \"rm -fr %s\"" % (client_ip, posix_file_location)
    rc = common.command(cmd)
    common.judge_rc(
        rc, 0, "rm posix_file_location %s failed" %
        posix_file_location)

    return


def main():
    prepare_clean.test_prepare(FILE_NAME)
    case()
    prepare_clean.test_clean(FILE_NAME)
    log.info('testcase %s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
