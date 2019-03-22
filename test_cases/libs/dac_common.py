#!/usr/bin/python
# -*- encoding=utf8 -*-
from random import choice

import os
import json
import shell
import time
import subprocess
import common
import log
import get_config
import sys
import traceback
import re
import tool_use


class Dac():
    '''
    DAC权限测试基础库函数
    '''

    def __init__(self):
        pass

    def set_xattr(self, target_ip, file_path, attr_type, key, value):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | attr_type | key | value |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 扩展属性类型 | 扩展属性的键 | 扩展属性的值 |
        | | 例如/mnt/parastor/test/file1 | security，trusted，user三者之一 | | |
        """
        cmd = 'ssh %s "setfattr -n \"%s.%s\" -v \'%s\' %s"' % (
            target_ip, attr_type, key, value, file_path)
        rc = common.command(cmd)

        return rc

    def set_xattrs(self, target_ip, file_path, attr_type, key_value_dict):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | attr_type | key_value_dict |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 扩展属性类型 | 扩展属性的“键-值对”组成的字典  |
        | | 例如/mnt/parastor/test/file1 | security，trusted，user三者之一 | | |
        """
        rc_final = 0
        rc_set_num = 0
        for key in key_value_dict:
            node_ip = target_ip
            cmd = "setfattr -n \"%s.%s\" -v \"%s\" %s" % \
                  (attr_type, key, key_value_dict[key], file_path)
            (rc, stdout) = common.run_command(node_ip, cmd)
            if rc != 0:
                if "Numerical result out of range" in stdout:
                    rc_final = 0
                    break
                elif "数值结果超出范围" in stdout:
                    rc_final = 0
                    break
                else:
                    rc_final = 1
                    break
            rc_set_num = rc_set_num + 1
        return (rc_final, rc_set_num)

    def get_xattr(self, target_ip, file_path):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 |
        | | 例如/mnt/parastor/test/file1 |
        """
        cmd = 'ssh %s "getfattr -m . -d --absolute-names %s"' % (
            target_ip, file_path)
        rc = common.command(cmd)

        return rc

    # 删除一条扩展属性

    def delete_xattr(self, target_ip, file_path, attr_type, key):
        """
        #执行：         #返回：三元素元组，第一个元素为返回值，第二个元素为标准输出，第三个元素为标准错误
        | test case | target_ip | file_path | attr_type | key |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 扩展属性类型 | 扩展属性的键 |
        | | 例如/mnt/parastor/test/file1 | security，trusted，user三者之一 | |
        """
        cmd = 'ssh %s "setfattr -x \"%s.%s\" %s"' % (
            target_ip, attr_type, key, file_path)
        rc = common.command(cmd)

        return rc

    # 设置一条acl权限

    def set_acl(self, target_ip, file_path, name, acl, type='user'):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | user | acl | type |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 待设置acl的主体 | 待设置acl的值 | 主体的类别 |
        | | 例如/mnt/parastor/test/file1 | 例如：du1/dws_00001 | 例如：rwx | user/group/other |
        """

        cmd = 'ssh %s "setfacl -m %s:%s:%s %s"' % (
            target_ip, type, name, acl, file_path)
        rc = common.command(cmd)

        return rc

    def set_acls(self, target_ip, file_path, user_list, acl, type='user'):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | user_list | acl | type |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 待设置acl的用户列表 | 待设置acl的值 | 主体的类别 |
        | | 例如/mnt/parastor/test/file1 | 例如：du1/dws_00001 | 例如：rwx | user/group/other |
        """
        node_ip = target_ip
        rc_final = 0
        rc_set_num = 0
        for user_tmp in user_list:
            cmd = "setfacl -m %s:%s:%s %s" % (
                type, user_tmp, acl, file_path)
            (rc, stdout) = common.run_command(node_ip, cmd)
            if rc != 0:
                if "Numerical result out of range" in stdout:
                    rc_final = 0
                    break
                elif "数值结果超出范围" in stdout:
                    rc_final = 0
                    break
                else:
                    rc_final = 1
                    break
            rc_set_num = rc_set_num + 1

        return (rc_final, rc_set_num)

    def set_acls_specified_times(
            self,
            target_ip,
            file_path,
            user_list,
            acl_list,
            type='user',
            times=100):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | user_list | acl_list | type | times |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 待设置acl的用户列表 | 待设置acl的列表 | 主体的类别 | 设置的次数 |
        | | 例如/mnt/parastor/test/file1 | 例如：du1/dws_00001 | 例如：["rwx", "rw", "---"] | user/group/other | 100 |
        """
        node_ip = target_ip
        rc_final = 0
        rc_set_num = 0
        for num in range(times):
            acl_current = choice(acl_list)
            for user_tmp in user_list:
                cmd = "setfacl -m %s:%s:%s %s" % (
                    type, user_tmp, acl_current, file_path)
                (rc, stdout) = common.run_command(node_ip, cmd)
                if rc != 0:
                    if "No space left on device" in stdout:
                        rc_final = 0
                        break
                    else:
                        rc_final = 1
                        break
                rc_set_num = rc_set_num + 1

        return (rc_final, rc_set_num)

    # 目录设置可继承的权限

    def set_dir_default_acls(
            self,
            target_ip,
            dir_path,
            user_list,
            acl,
            type='user'):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path | user_list | acl | type |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 | 待设置acl的用户列表 | 待设置acl的值 | 主体的类别 |
        | | 例如/mnt/parastor/test/file1 | 例如：du1/dws_00001 | 例如：rwx | user/group/other |
        """
        node_ip = target_ip
        rc_final = 0
        rc_set_num = 0
        for user_tmp in user_list:
            cmd = "setfacl -d -m %s:%s:%s %s" % (
                type, user_tmp, acl, dir_path)
            (rc, stdout) = common.run_command(node_ip, cmd)
            if rc != 0:
                if "No space left on device" in stdout:
                    rc_final = 0
                    break
                else:
                    rc_final = 1
                    break
            rc_set_num = rc_set_num + 1

        return (rc_final, rc_set_num)

    # 获取acl权限

    def get_acl(self, target_ip, file_path):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 |
        | | 例如/mnt/parastor/test/file1 |
        """
        cmd = 'ssh %s "getfacl --absolute-names %s"' % (target_ip, file_path)
        rc = common.command(cmd)

        return rc

    def delete_all_acl(self, target_ip, file_path):
        """
        #执行：         #返回：一对元组，第一个元素为返回值，第二个元素为返回内容
        | test case | target_ip | file_path |
        | nfs或者私有客户端ip | 客户端文件的绝对路径 |
        | | 例如/mnt/parastor/test/file1 |
        """
        cmd = 'ssh %s "setfacl -b %s"' % (target_ip, file_path)
        rc = common.command(cmd)

        return rc


if __name__ == "__main__":
    instance = Dac()
    # target_ip, file_path, attr_type, key_value_dict
    ip = "10.2.42.65"
    file_path = "/mnt/parastor/posix_dir23_0_6_1/testfile1"
    attr_type = "user"

    attr_key_pre = "key_"
    attr_num = 500
    attr_value = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                 "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa" \
                 "aaaaaaaaaaaaaaaaaaaaaaaaa"  # 200B
    attr_key_list = []
    attr_value_list = []

    for k_num in range(attr_num):
        attr_key_list.append(attr_key_pre + str(k_num))

    for v_num in range(len(attr_key_list)):
        attr_value_list.append(attr_value + str(v_num))
    key_value_dict = dict(zip(attr_key_list, attr_value_list))
    (rc_final, rc_set_num) = instance.set_xattrs(
        ip, file_path, attr_type, key_value_dict)
    print(
        "the final result, (rc_final, rc_set_num) is (%d, %d)" %
        (rc_final, rc_set_num))
