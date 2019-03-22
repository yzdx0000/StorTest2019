#!/bin/bash

source ./acl_common.sh
# dir=$mnt/set_get_test
dir=$1/set_get_test  # changed by zhanghan 20181126

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-046
# 测试项目  : 客户端设置三种特殊主体
# 用例标题  : 支持设置ACL01
# 用例简介  : 在客户端使用工具设置文件的三种特殊主体，检查设置结果及mode
# 预置条件  : 挂载的parastor文件系统支持posix acl
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的user、group、other主体:
#             "user::rwx; group::rwx; other::rwx"
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的权限mode
# 预期结果  : 1、文件f0的acl为:
#             user::rwx
#             group::rwx
#             other::rwx
#             2、文件f0的mode为0777
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test1()
{
    f=f1
    touch $1/$f
    setfacl -m user::rwx $1/$f
    setfacl -m group::rwx $1/$f
    setfacl -m other::rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0777 ]
    then
        echo "set_get_test1 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rwx"
    ace_check $1 $f 5 "group::rwx"
    ace_check $1 $f 6 "other::rwx"

    echo "set_get_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-047
# 测试项目  : 客户端设置mask主体
# 用例标题  : 支持设置ACL02
# 用例简介  : 在客户端使用工具设置文件的mask主体，检查设置结果及mode
# 预置条件  : 挂载的parastor文件系统支持posix acl
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的mask主体:"mask::rwx"
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的权限mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             group::r--
#             mask::rwx
#             other::r--
#             2、文件f0的mode为0674
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test2()
{
    f=f2
    touch $1/$f
    setfacl -m mask::rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "set_get_test2 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "group::r--"
    ace_check $1 $f 6 "mask::rwx"
    ace_check $1 $f 7 "other::r--"

    echo "set_get_test2 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-048
# 测试项目  : 客户端设置其他用户主体
# 用例标题  : 支持设置ACL03
# 用例简介  : 在客户端使用工具设置文件的其他用户主体，检查设置结果及mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rwx"
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的权限mode
# 预期结果  : 1、文件f0的acl:
#             user::rw-
#             user:u1:rwx
#             group::r--
#             mask::rwx
#             other::r--
#             2、文件f0的mode为0674
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test3()
{
    f=f3
    touch $1/$f
    setfacl -m user:u1:rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "set_get_test3 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "user:u1:rwx"
    ace_check $1 $f 6 "group::r--"
    ace_check $1 $f 7 "mask::rwx"
    ace_check $1 $f 8 "other::r--"

    echo "set_get_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-049
# 测试项目  : 客户端设置其他组主体
# 用例标题  : 支持设置ACL04
# 用例简介  : 在客户端使用工具设置文件的其他组主体，检查设置结果及mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g1主体:"group:g1:rwx"
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的权限mode
# 预期结果  : 1、文件f0的acl:
#             user::rw-
#             group::r--
#             group:g1:rwx
#             mask::rwx
#             other::r--
#             2、文件f0的mode为0674
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test4()
{
    f=f4
    touch $1/$f
    setfacl -m group:g1:rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "set_get_test4 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "group::r--"
    ace_check $1 $f 6 "group:g1:rwx"
    ace_check $1 $f 7 "mask::rwx"
    ace_check $1 $f 8 "other::r--"

    echo "set_get_test4 test finish!" >> $LOG
}

__set_get_test5()
{
    for u1 in "r" "-"
    do
        for u2 in "w" "-"
        do
            for u3 in "x" "-"
            do
                for g1 in "r" "-"
                do
                    for g2 in "w" "-"
                    do
                        for g3 in "x" "-"
                        do
                            for o1 in "r" "-"
                            do
                                for o2 in "w" "-"
                                do
                                    for o3 in "x" "-"
                                    do
                                        f=f${u1}${u2}${u3}${g1}${g2}${g3}${o1}${o2}${o3}
                                        if [ $2 -eq 0 ]
                                        then
                                            touch $1/$f
                                            setfacl -m user::${u1}${u2}${u3} $1/$f
                                            setfacl -m group::${g1}${g2}${g3} $1/$f
                                            setfacl -m other::${o1}${o2}${o3} $1/$f
                                        else
                                            ace_check $1 $f 4 "user::${u1}${u2}${u3}"
                                            ace_check $1 $f 5 "group::${g1}${g2}${g3}"
                                            ace_check $1 $f 6 "other::${o1}${o2}${o3}"
                                        fi
                                    done
                                done
                            done
                        done
                    done
                done
            done
        done
    done
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-050
# 测试项目  : 支持POSIX的rwx各种不同组合
# 用例标题  : 支持设置ACL05
# 用例简介  : 在客户端创建512个文件，按照不同的rwx组合设置
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f1~f512
#             2、使用setfacl按照不同的rwx配置设置文件f1~f512的user、group、other主体
#             3、使用getfacl查看文件f1~f512的acl
#             4、使用stat查看文件f1~f512的权限mode
#             (example: f1   user::---; group::---; other::---
#                       f2   user::---; group::---; other::--x
#                       f3   user::---; group::---; other::-w-
#                       ...
#                       f512 user::rwx; group::rwx; other::rwx
#             )
# 预期结果  : 文件f1~f512的user、group、other主体权限与设置的相同
#
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test5()
{
    d=$1/d5
    mkdir $d

    __set_get_test5 $d 0

    clean_cache

    __set_get_test5 $d 1

    echo "set_get_test5 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-051
# 测试项目  : 支持删除文件的ACL
# 用例标题  : 支持设置ACL06
# 用例简介  : 在客户端使用工具设置文件的acl，然后删除，检查内容及格式
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用setfacl删除POSIX_ACL
#             4、使用getfacl获取文件f0的ACL
#             5、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的ACL内容及格式为:
#                user::rw-
#                group::r--
#                other::r--
#             2、文件f0 mode: 0644
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年6月1日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test6()
{
    f=f6
    touch $1/$f
    setfacl -m user:u1:rw- $1/$f
    sync
    setfacl -b $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "set_get_test6 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "group::r--"
    ace_check $1 $f 6 "other::r--"

    echo "set_get_test6 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-052
# 测试项目  : 支持修改文件的ACL，修改后ACL正确
# 用例标题  : 支持设置ACL07
# 用例简介  : 在客户端使用工具获取文件的acl，修改mask ace，检查内容及格式
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1和g1主体:
#             "user:u1:rw-","group:g1:rwx"
#             3、使用getfacl设置文件f0的mask主体:"mask::r--"
#             4、使用getfacl获取文件f0的ACL
#             5、使用stat检查文件权限mode
#             6、使用getfacl设置文件f0的mask主体:"mask::rwx"
#             7、使用getfacl获取文件f0的ACL
#             8、使用stat检查文件权限mode
# 预期结果  : 1、文件f0的ACL内容及格式为:
#                user::rw-
#                user:u1:rw-             #effective:r--
#                group::r--
#                group:g1:rwx            #effective:r--
#                mask::r--
#                other::r--
#             2、文件权限mode为: 0644
#             3、文件f0的ACL内容及格式为:
#                user::rw-
#                user:u1:rw-
#                group::r--
#                group:g1:rwx
#                mask::rwx
#                other::r--
#             4、文件权限mode为:0674
#
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年6月1日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test7()
{
    f=f7
    touch $1/$f
    setfacl -m user:u1:rw- $1/$f
    setfacl -m group:g1:rwx $1/$f
    setfacl -m mask::r-- $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "set_get_test7 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "user:u1:rw-#effective:r--"
    ace_check $1 $f 6 "group::r--"
    ace_check $1 $f 7 "group:g1:rwx#effective:r--"
    ace_check $1 $f 8 "mask::r--"
    ace_check $1 $f 9 "other::r--"

    setfacl -m mask::rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "set_get_test7 test failed: " >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "user:u1:rw-"
    ace_check $1 $f 6 "group::r--"
    ace_check $1 $f 7 "group:g1:rwx"
    ace_check $1 $f 8 "mask::rwx"
    ace_check $1 $f 9 "other::r--"

    echo "set_get_test7 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-053
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL08
# 用例简介  : 在客户端使用工具设置目录的继承mask ace，权限大于有效所有组类的权限
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的继承mask主体:"mask::rwx"
#             4、使用getfacl获取目录d1的ACL
#             5、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::rwx
#                default:group::r-x
#                default:mask::rwx
#                default:other::r-x
#             2、目录d1的权限mode:0755
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年6月4日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test8()
{
    d=d8
    mkdir $1/$d
    setfacl -d -m mask::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0755 ]
    then
        echo "set_get_test8 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "other::r-x"
    ace_check $1 $d 7 "default:user::rwx"
    ace_check $1 $d 8 "default:group::r-x"
    ace_check $1 $d 9 "default:mask::rwx"
    ace_check $1 $d 10 "default:other::r-x"

    echo "set_get_test8 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-054
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL09
# 用例简介  : 在客户端使用工具设置目录的继承mask ace，权限小于有效所有组类的权限
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的继承mask主体:"mask::r--"
#             4、使用getfacl获取目录d1的ACL
#             5、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::rwx
#                default:group::r-x          #effective:r--
#                default:mask::r--
#                default:other::r-x
#             2、目录d1的权限mode:0755
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test9()
{
    d=d9
    mkdir $1/$d
    setfacl -d -m mask::r-- $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0755 ]
    then
        echo "set_get_test9 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "other::r-x"
    ace_check $1 $d 7 "default:user::rwx"
    ace_check $1 $d 8 "default:group::r-x#effective:r--"
    ace_check $1 $d 9 "default:mask::r--"
    ace_check $1 $d 10 "default:other::r-x"

    echo "set_get_test9 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-055
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL10
# 用例简介  : 在客户端使用工具设置目录的其他用户ace；设置继承group ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的u1主体:"user:u1:r-x"
#             3、使用setfacl设置目录d1的继承group主体:"group::rwx"
#             4、使用getfacl获取目录d1的ACL
#             5、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                user:u1:r-x
#                group::r-x
#                mask::r-x
#                other::r-x
#                default:user::rwx
#                default:group::rwx
#                default:other::r-x
#             2、目录d1的权限mode:0755
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test10()
{
    d=d10
    mkdir $1/$d
    setfacl -m user:u1:r-x $1/$d
    setfacl -d -m group::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0755 ]
    then
        echo "set_get_test10 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "user:u1:r-x"
    ace_check $1 $d 6 "group::r-x"
    ace_check $1 $d 7 "mask::r-x"
    ace_check $1 $d 8 "other::r-x"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:group::rwx"
    ace_check $1 $d 11 "default:other::r-x"

    echo "set_get_test10 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-056
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL11
# 用例简介  : 在客户端使用工具设置目录的其他用户ace；设置继承其他组 ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的u1主体:"user:u1:rwx"
#             3、使用setfacl设置目录d1的继承g1主体:"group:g1:r--"
#             4、使用getfacl获取目录d1的ACL
#             5、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                user:u1:rwx
#                group::r-x
#                mask::rwx
#                other::r-x
#                default:user::rwx
#                default:group::r-x
#                default:group:g1:r--
#                default:mask::r-x
#                default:other::r-x
#             2、目录d1的权限mode:0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test11()
{
    d=d11
    mkdir $1/$d
    setfacl -m user:u1:rwx $1/$d
    setfacl -d -m group:g1:r-- $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "set_get_test11 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "user:u1:rwx"
    ace_check $1 $d 6 "group::r-x"
    ace_check $1 $d 7 "mask::rwx"
    ace_check $1 $d 8 "other::r-x"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:group::r-x"
    ace_check $1 $d 11 "default:group:g1:r--"
    ace_check $1 $d 12 "default:mask::r-x"
    ace_check $1 $d 13 "default:other::r-x"

    echo "set_get_test11 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-057
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL12
# 用例简介  : 在客户端使用工具设置目录的其他用户ace；设置继承其他组 ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的u1主体:"user:u1:rwx"
#             3、使用setfacl设置目录d1的继承g1主体:"group:g1:rwx"
#             4、使用setfacl设置目录d1的mask主体:"mask::rw-"
#             5、使用getfacl获取目录d1的ACL
#             6、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                user:u1:rwx         #effective:rw-
#                group::r-x          #effective:r--
#                mask::rw-
#                other::r-x
#                default:user::rwx
#                default:group::r-x
#                default:group:g1:rwx
#                default:mask::rwx
#                default:other::r-x
#             2、目录d1的权限mode:0765
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test12()
{
    d=d12
    mkdir $1/$d
    setfacl -m user:u1:rwx $1/$d
    setfacl -d -m group:g1:rwx $1/$d
    setfacl -m mask::rw- $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0765 ]
    then
        echo "set_get_test12 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "user:u1:rwx#effective:rw-"
    ace_check $1 $d 6 "group::r-x#effective:r--"
    ace_check $1 $d 7 "mask::rw-"
    ace_check $1 $d 8 "other::r-x"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:group::r-x"
    ace_check $1 $d 11 "default:group:g1:rwx"
    ace_check $1 $d 12 "default:mask::rwx"
    ace_check $1 $d 13 "default:other::r-x"

    echo "set_get_test12 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-058
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL13
# 用例简介  : 在客户端使用工具设置目录的其他用户ace；设置继承其他组 ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的u1主体:"user:u1:rwx"
#             3、使用setfacl设置目录d1的继承g1主体:"group:g1:rwx"
#             4、使用setfacl设置目录d1的继承mask主体:"mask::rw-"
#             5、使用getfacl获取目录d1的ACL
#             6、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                user:u1:rwx
#                group::r-x
#                mask::rwx
#                other::r-x
#                default:user::rwx
#                default:group::r-x      #effective:r--
#                default:group:g1:rwx    #effective:rw-
#                default:mask::rw-
#                default:other::r-x
#             2、目录d1的权限mode:0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test13()
{
    d=d13
    mkdir $1/$d
    setfacl -m user:u1:rwx $1/$d
    setfacl -d -m group:g1:rwx $1/$d
    setfacl -d -m mask::rw- $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "set_get_test13 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "user:u1:rwx"
    ace_check $1 $d 6 "group::r-x"
    ace_check $1 $d 7 "mask::rwx"
    ace_check $1 $d 8 "other::r-x"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:group::r-x#effective:r--"
    ace_check $1 $d 11 "default:group:g1:rwx#effective:rw-"
    ace_check $1 $d 12 "default:mask::rw-"
    ace_check $1 $d 13 "default:other::r-x"

    echo "set_get_test13 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-059
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL14
# 用例简介  : 在客户端使用工具设置目录的多个其他用户ace；设置继承多个其他组 ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的继承u1主体:"user:u1:rwx"
#             3、使用setfacl设置目录d1的继承u2主体:"user:u2:rw-"
#             4、使用setfacl设置目录d1的继承u3主体:"user:u3:r-x"
#             5、使用setfacl设置目录d1的g1主体:"group:g1:r--"
#             6、使用setfacl设置目录d1的g1主体:"group:g2:-w-"
#             7、使用setfacl设置目录d1的g1主体:"group:g3:--x"
#             8、使用getfacl获取目录d1的ACL
#             9、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                group::r-x
#                group:g1:r--
#                group:g2:-w-
#                group:g3:--x
#                mask::rwx
#                other::r-x
#                default:user::rwx
#                default:user:u1:rwx
#                default:user:u2:rw-
#                default:user:u3:r-x
#                default:group::r-x
#                default:mask::rwx
#                default:other::r-x
#             2、目录d1的权限mode:0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test14()
{
    d=d14
    mkdir $1/$d
    setfacl -d -m user:u1:rwx $1/$d
    setfacl -d -m user:u2:rw- $1/$d
    setfacl -d -m user:u3:r-x $1/$d
    setfacl -m group:g1:r-- $1/$d
    setfacl -m group:g2:-w- $1/$d
    setfacl -m group:g3:--x $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "set_get_test14 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "group:g1:r--"
    ace_check $1 $d 7 "group:g2:-w-"
    ace_check $1 $d 8 "group:g3:--x"
    ace_check $1 $d 9 "mask::rwx"
    ace_check $1 $d 10 "other::r-x"
    ace_check $1 $d 11 "default:user::rwx"
    ace_check $1 $d 12 "default:user:u1:rwx"
    ace_check $1 $d 13 "default:user:u2:rw-"
    ace_check $1 $d 14 "default:user:u3:r-x"
    ace_check $1 $d 15 "default:group::r-x"
    ace_check $1 $d 16 "default:mask::rwx"
    ace_check $1 $d 17 "default:other::r-x"

    echo "set_get_test14 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-060
# 测试项目  : 支持设置目录的ACL
# 用例标题  : 支持设置ACL15
# 用例简介  : 在客户端使用工具设置目录继承特殊主体ace，
#             检查目录的acl和权限mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
#
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d1
#             2、使用setfacl设置目录d1的继承user主体:"user::r--"
#             3、使用setfacl设置目录d1的继承group主体:"group::rwx"
#             4、使用setfacl设置目录d1的继承other主体:"other:::rwx"
#             5、使用getfacl获取目录d1的ACL
#             6、使用stat查看目录d1的mode
# 预期结果  : 1、目录d1的ACL内容及格式为:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::r--
#                default:group::rwx
#                default:other::rwx
#             2、目录d1的权限mode:0755
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
set_get_test15()
{
    d=d15
    mkdir $1/$d
    setfacl -d -m user::r-- $1/$d
    setfacl -d -m group::rwx $1/$d
    setfacl -d -m other::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0755 ]
    then
        echo "set_get_test15 test failed: " >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "other::r-x"
    ace_check $1 $d 7 "default:user::r--"
    ace_check $1 $d 8 "default:group::rwx"
    ace_check $1 $d 9 "default:other::rwx"

    echo "set_get_test15 test finish!" >> $LOG
}


set_get_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
    fi

    echo -e "---------- set_get test start ----------" >> $LOG

    set_get_test1 $dir
    set_get_test2 $dir
    set_get_test3 $dir
    set_get_test4 $dir
    set_get_test5 $dir
    set_get_test6 $dir
    set_get_test7 $dir
    set_get_test8 $dir
    set_get_test9 $dir
    set_get_test10 $dir
    set_get_test11 $dir
    set_get_test12 $dir
    set_get_test13 $dir
    set_get_test14 $dir
    set_get_test15 $dir

    echo -e "---------- set_get test finish ----------\n" >> $LOG
}

set_get_test
