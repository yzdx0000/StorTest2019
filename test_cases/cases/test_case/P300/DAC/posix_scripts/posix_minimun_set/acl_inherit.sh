#!/bin/bash

source ./acl_common.sh
# dir=$mnt/inherit_test
dir=$1/inherit_test  # changed by zhanghan 20181126

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-038
# 测试项目  : 1、以posix_acl挂载的客户端在创建文件时父目录无可继承的acl，
#             需要mode
#             2、创建文件的mode受系统umask影响
# 用例标题  : 创建新对象继承可继承ACL01
# 用例简介  : 在无可继承acl的父目录下创建文件，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、创建的文件对象父目录无可继承的ACL
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、在目录dir内创建文件f0
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             group::r--
#             other::r--
#             2、文件f0的mode为0644
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test1()
{
    f=f1
    touch $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "inherit_test1 test failed:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "group::r--"
    ace_check $1 $f 6 "other::r--"

    echo "inherit_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-039
# 测试项目  : 1、以posix_acl挂载的客户端在创建目录时父目录无可继承的acl，
#             需要mode
#             2、创建目录的mode受系统umask影响
# 用例标题  : 创建新对象继承可继承ACL02
# 用例简介  : 在无可继承acl的父目录下创建目录，检查目录的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、创建的目录对象父目录无可继承的ACL
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、在目录dir内创建目录d0
#             3、使用getfacl查看目录d0的acl
#             4、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rwx
#             group::r-x
#             other::r-x
#             2、目录d0的mode为0755
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test2()
{
    d=dir2
    mkdir $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0755 ]
    then
        echo "inherit_test2 test failed:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "other::r-x"

    echo "inherit_test2 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-040
# 测试项目  : 1、以posix_acl挂载的客户端在创建文件时父目录有可继承的acl，
#             文件继承父目录可继承的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL03
# 用例简介  : 在有可继承acl的父目录下创建文件，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:mask::rwx"
#             3、在目录dir内创建文件f0
#             4、使用getfacl查看文件f0的acl
#             5、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             group::r-x           #effective:r--
#             mask::rw-
#             other::r--
#             2、文件f0的mode为0664
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test3()
{
    d=$1/dir3
    mkdir $d
    setfacl -d -m mask::rwx $d
    clean_cache

    f=f1
    touch $d/$f
    sync

    mode=`stat $d/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0664 ]
    then
        echo "inherit_test3 test failed:" >> $ELOG
        echo "$d/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $f 4 "user::rw-"
    ace_check $d $f 5 "group::r-x#effective:r--"
    ace_check $d $f 6 "mask::rw-"
    ace_check $d $f 7 "other::r--"

    echo "inherit_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-041
# 测试项目  : 1、以posix_acl挂载的私有客户端在创建目录时父目录有可继承的acl，
#             新目录继承父目录可继承的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL04
# 用例简介  : 在有可继承acl的父目录下创建目录，检查目录的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象父目录有可继承的的acl
#             3、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:mask::rwx"
#             3、在目录dir内创建目录d0
#             4、使用getfacl查看目录d0的acl
#             5、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rwx
#             group::r-x
#             mask::rwx
#             other::r-x
#             default:user::rwx
#             default:group::r-x
#             default:mask::rwx
#             default:other::r-x
#             2、目录d0的mode为0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test4()
{
    d=$1/dir4
    mkdir $d
    setfacl -d -m mask::rwx $d
    clean_cache

    dd=dir1
    mkdir $d/$dd
    sync

    mode=`stat $d/$dd | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "inherit_test4 test failed:" >> $ELOG
        echo "$d/$dd mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $dd 4 "user::rwx"
    ace_check $d $dd 5 "group::r-x"
    ace_check $d $dd 6 "mask::rwx"
    ace_check $d $dd 7 "other::r-x"
    ace_check $d $dd 8 "default:user::rwx"
    ace_check $d $dd 9 "default:group::r-x"
    ace_check $d $dd 10 "default:mask::rwx"
    ace_check $d $dd 11 "default:other::r-x"

    echo "inherit_test4 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-042
# 测试项目  : 1、以posix_acl挂载的客户端在创建文件时父目录有可继承的acl，
#             文件继承父目录可继承的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL04
# 用例简介  : 在有可继承acl的父目录下创建文件，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:user:u1:rwx"
#             3、使用setfacl为目录dir添加default acl:"default:group:g1:r-x"
#             4、使用setfacl为目录dir添加default acl:"default:mask::--x"
#             5、在目录dir内创建文件f0
#             6、使用getfacl查看文件f0的acl
#             7、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             user:u1:rwx          #effective:---
#             group::r-x           #effective:---
#             group:g1:r-x         #effective:---
#             mask::---
#             other::r--
#             2、文件f0的mode为0604
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test5()
{
    d=$1/dir5
    mkdir $d
    setfacl -d -m user:u1:rwx $d
    setfacl -d -m group:g1:r-x $d
    setfacl -d -m mask::--x $d
    clean_cache

    f=f1
    touch $d/$f
    sync

    mode=`stat $d/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0604 ]
    then
        echo "inherit_test5 test failed:" >> $ELOG
        echo "$d/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $f 4 "user::rw-"
    ace_check $d $f 5 "user:u1:rwx#effective:---"
    ace_check $d $f 6 "group::r-x#effective:---"
    ace_check $d $f 7 "group:g1:r-x#effective:---"
    ace_check $d $f 8 "mask::---"
    ace_check $d $f 9 "other::r--"

    echo "inherit_test5 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-043
# 测试项目  : 1、以posix_acl挂载的客户端在创建目录时父目录有可继承的acl，
#             子目录继承父目录可继承的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL05
# 用例简介  : 在有可继承acl的父目录下创建子目录，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:user:u1:rwx"
#             3、使用setfacl为目录dir添加default acl:"default:group:g1:r-x"
#             4、在目录dir内创建目录d0
#             5、使用getfacl查看目录d0的acl
#             6、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rwx
#             user:u1:rwx
#             group::r-x
#             group:g1:r-x
#             mask::rwx
#             other::r-x
#             default:user::rwx
#             default:user:u1:rwx
#             default:group::r-x
#             default:group:g1:r-x
#             default:mask::rwx
#             default:other::r-x
#             2、目录d0的mode为0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test6()
{
    d=$1/dir6
    mkdir $d
    setfacl -d -m user:u1:rwx $d
    setfacl -d -m group:g1:r-x $d
    clean_cache

    dd=dir1
    mkdir $d/$dd
    sync

    mode=`stat $d/$dd | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "inherit_test6 test failed:" >> $ELOG
        echo "$d/$dd mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $dd 4 "user::rwx"
    ace_check $d $dd 5 "user:u1:rwx"
    ace_check $d $dd 6 "group::r-x"
    ace_check $d $dd 7 "group:g1:r-x"
    ace_check $d $dd 8 "mask::rwx"
    ace_check $d $dd 9 "other::r-x"
    ace_check $d $dd 10 "default:user::rwx"
    ace_check $d $dd 11 "default:user:u1:rwx"
    ace_check $d $dd 12 "default:group::r-x"
    ace_check $d $dd 13 "default:group:g1:r-x"
    ace_check $d $dd 14 "default:mask::rwx"
    ace_check $d $dd 15 "default:other::r-x"

    echo "inherit_test6 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-044
# 测试项目  : 1、以posix_acl挂载的客户端在创建文件时父目录有可继承的acl，
#             文件继承父目录可继承的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL06
# 用例简介  : 在有可继承acl的父目录下创建文件，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:user:u1:rwx"
#             3、使用setfacl为目录dir添加default acl:"default:user:u2:r-x"
#             4、使用setfacl为目录dir添加default acl:"default:user:u3:rw-"
#             5、使用setfacl为目录dir添加default acl:"default:mask::r--"
#             6、在目录dir内创建文件f0
#             7、使用getfacl查看文件f0的acl
#             8、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             user:u1:rwx          #effective:r--
#             user:u2:r-x          #effective:r--
#             user:u3:rw-          #effective:r--
#             group::r-x           #effective:r--
#             mask::r--
#             other::r--
#             2、文件f0的mode为0644
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test7()
{
    d=$1/dir7
    mkdir $d
    setfacl -d -m user:u1:rwx $d
    setfacl -d -m user:u2:r-x $d
    setfacl -d -m user:u3:rw- $d
    setfacl -d -m mask::r-- $d
    clean_cache

    f=f1
    touch $d/$f
    sync

    mode=`stat $d/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "inherit_test7 test failed:" >> $ELOG
        echo "$d/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $f 4 "user::rw-"
    ace_check $d $f 5 "user:u1:rwx#effective:r--"
    ace_check $d $f 6 "user:u2:r-x#effective:r--"
    ace_check $d $f 7 "user:u3:rw-#effective:r--"
    ace_check $d $f 8 "group::r-x#effective:r--"
    ace_check $d $f 9 "mask::r--"
    ace_check $d $f 10 "other::r--"

    echo "inherit_test7 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-045
# 测试项目  : 1、以posix_acl挂载的客户端在创建目录时父目录有可继承的acl，
#             子目录继承父目录可继承的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 创建新对象继承可继承ACL07
# 用例简介  : 在有可继承acl的父目录下创建子目录，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建目录dir
#             2、使用setfacl为目录dir添加default acl:"default:group:g1:rwx"
#             3、使用setfacl为目录dir添加default acl:"default:group:g2:r-x"
#             4、使用setfacl为目录dir添加default acl:"default:group:g3:--x"
#             5、在目录dir内创建目录d0
#             6、使用getfacl查看目录d0的acl
#             7、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rwx
#             group::r-x
#             group:g1:rwx
#             group:g2:r-x
#             group:g3:--x
#             mask::rwx
#             other::r-x
#             default:user::rwx
#             default:group::r-x
#             default:group:g1:rwx
#             default:group:g2:r-x
#             default:group:g3:--x
#             default:mask::rwx
#             default:other::r-x
#             2、目录d0的mode为0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
inherit_test8()
{
    d=$1/dir8
    mkdir $d
    setfacl -d -m group:g1:rwx $d
    setfacl -d -m group:g2:r-x $d
    setfacl -d -m group:g3:--x $d
    clean_cache
    dd=dir1
    mkdir $d/$dd
    sync

    mode=`stat $d/$dd | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "inherit_test8 test failed:" >> $ELOG
        echo "$d/$dd mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $d $dd 4 "user::rwx"
    ace_check $d $dd 5 "group::r-x"
    ace_check $d $dd 6 "group:g1:rwx"
    ace_check $d $dd 7 "group:g2:r-x"
    ace_check $d $dd 8 "group:g3:--x"
    ace_check $d $dd 9 "mask::rwx"
    ace_check $d $dd 10 "other::r-x"
    ace_check $d $dd 11 "default:user::rwx"
    ace_check $d $dd 12 "default:group::r-x"
    ace_check $d $dd 13 "default:group:g1:rwx"
    ace_check $d $dd 14 "default:group:g2:r-x"
    ace_check $d $dd 15 "default:group:g3:--x"
    ace_check $d $dd 16 "default:mask::rwx"
    ace_check $d $dd 17 "default:other::r-x"

    echo "inherit_test8 test finish!" >> $LOG
}

inherit_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
    fi

    echo -e "---------- inherit test start ----------" >> $LOG

    inherit_test1 $dir
    inherit_test2 $dir
    inherit_test3 $dir
    inherit_test4 $dir
    inherit_test5 $dir
    inherit_test6 $dir
    inherit_test7 $dir
    inherit_test8 $dir

    echo -e "---------- inherit test finish ----------\n" >> $LOG
}

inherit_test
