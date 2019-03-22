#!/bin/bash

source ./acl_common.sh
# dir=$mnt/chmod_test  
dir=$1/chmod_test  # changed by zhanghan 20181126

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-068
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位01
# 用例简介  : 创建文件，chmod改变mode，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用chmod改变文件权限位:0666
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rw-
#             group::rw-
#             other::rw-
#             2、文件f0的mode为0666
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test1()
{
    f=f1
    touch $1/$f
    chmod 666 $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0666 ]
    then
        echo "chmod_test1 test faild:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rw-"
    ace_check $1 $f 5 "group::rw-"
    ace_check $1 $f 6 "other::rw-"

    echo "chmod_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-069
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位02
# 用例简介  : 创建文件，chmod改变mode，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rwx"
#             3、使用stat查看文件f0的mode
#             2、使用chmod改变文件权限位:0446
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::r--
#             user:u1:rwx    #effective:r--
#             group::r--
#             maks::r--
#             other::rw-
#             2、文件f0的mode为0674
#             3、文件f0的mode为0446
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test2()
{
    f=f2
    touch $1/$f
    setfacl -m user:u1:rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "chmod_test2 test faild:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    chmod 446 $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0446 ]
    then
        echo "chmod_test2 test faild:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::r--"
    ace_check $1 $f 5 "user:u1:rwx#effective:r--"
    ace_check $1 $f 6 "group::r--"
    ace_check $1 $f 7 "mask::r--"
    ace_check $1 $f 8 "other::rw-"

    echo "chmod_test2 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-070
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建文件的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位03
# 用例简介  : 创建文件，chmod改变mode，检查文件的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用stat查看文件f0的mode
#             2、使用chmod改变文件权限位:0777
#             3、使用getfacl查看文件f0的acl
#             4、使用stat查看文件f0的mode
# 预期结果  : 1、文件f0的acl为:
#             user::rwx
#             user:u1:rw-
#             group::r--
#             maks::rwx
#             other::rwx
#             2、文件f0的mode为0664
#             3、文件f0的mode为0777
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test3()
{
    f=f3
    touch $1/$f
    setfacl -m user:u1:rw- $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0664 ]
    then
        echo "chmod_test3 test faild:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    chmod 777 $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0777 ]
    then
        echo "chmod_test3 test faild:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $f 4 "user::rwx"
    ace_check $1 $f 5 "user:u1:rw-"
    ace_check $1 $f 6 "group::r--"
    ace_check $1 $f 7 "mask::rwx"
    ace_check $1 $f 8 "other::rwx"

    echo "chmod_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-071
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位04
# 用例简介  : 创建目录，chmod改变mode，检查目录的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用chmod改变文件权限位:0644
#             4、使用getfacl查看目录d0的acl
#             5、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rw-
#             group::r--
#             other::r--
#             2、目录d0的mode为0644
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test4()
{
    d=dir4
    mkdir $1/$d
    chmod -x $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "chmod_test4 test faild:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rw-"
    ace_check $1 $d 5 "group::r--"
    ace_check $1 $d 6 "other::r--"

    echo "chmod_test4 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-072
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位05
# 用例简介  : 创建目录，chmod改变mode，检查目录的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的g1主体:"group:g1:rwx"
#             3、使用setfacl设置目录d0的继承u1主体:"default:user:u1:rwx"
#             4、使用chmod改变文件权限位:0644
#             5、使用getfacl查看目录d0的acl
#             6、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rw-
#             group::r-x         #effective:r--
#             group:g1:rwx       #effective:r--
#             mask::r--
#             other::r--
#             default:user:rwx
#             default:user:u1:rwx
#             default:group::r-x
#             default:mask::rwx
#             default:other::r-x
#             2、目录d0的mode为0644
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test5()
{
    d=dir5
    mkdir $1/$d
    setfacl -m group:g1:rwx $1/$d
    setfacl -d -m user:u1:rwx $1/$d
    chmod 644 $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0644 ]
    then
        echo "chmod_test5 test faild:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rw-"
    ace_check $1 $d 5 "group::r-x#effective:r--"
    ace_check $1 $d 6 "group:g1:rwx#effective:r--"
    ace_check $1 $d 7 "mask::r--"
    ace_check $1 $d 8 "other::r--"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:user:u1:rwx"
    ace_check $1 $d 11 "default:group::r-x"
    ace_check $1 $d 12 "default:mask::rwx"
    ace_check $1 $d 13 "default:other::r-x"

    echo "chmod_test5 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-073
# 测试项目  : 1、chmod改变文件权限位，更改对应的acl
#             2、创建目录的mode受可继承acl以及系统umask影响
# 用例标题  : 支持使用chmod设置权限位06
# 用例简介  : 创建目录，chmod改变mode，检查目录的acl和mode
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的g1主体:"group:g1:r-x"
#             3、使用setfacl设置目录d0的继承u1主体:"default:user:u1:r--"
#             4、使用chmod改变文件权限位:0777
#             5、使用getfacl查看目录d0的acl
#             6、使用stat查看目录d0的mode
# 预期结果  : 1、目录d0的acl为:
#             user::rwx
#             group::r-x
#             group:g1:r-x
#             mask::rwx
#             other::rwx
#             default:user:rwx
#             default:user:u1:r--
#             default:group::r-x
#             default:mask::r-x
#             default:other::r-x
#             2、目录d0的mode为0777
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月3日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
chmod_test6()
{
    d=dir6
    mkdir $1/$d
    setfacl -m group:g1:r-x $1/$d
    setfacl -d -m user:u1:r-- $1/$d
    chmod 777 $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0777 ]
    then
        echo "chmod_test6 test faild:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    ace_check $1 $d 4 "user::rwx"
    ace_check $1 $d 5 "group::r-x"
    ace_check $1 $d 6 "group:g1:r-x"
    ace_check $1 $d 7 "mask::rwx"
    ace_check $1 $d 8 "other::rwx"
    ace_check $1 $d 9 "default:user::rwx"
    ace_check $1 $d 10 "default:user:u1:r--"
    ace_check $1 $d 11 "default:group::r-x"
    ace_check $1 $d 12 "default:mask::r-x"
    ace_check $1 $d 13 "default:other::r-x"

    echo "chmod_test6 test finish!" >> $LOG
}


chmod_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
    fi

    echo -e "---------- chmod test start ----------" >> $LOG

    chmod_test1 $dir
    chmod_test2 $dir
    chmod_test3 $dir
    chmod_test4 $dir
    chmod_test5 $dir
    chmod_test6 $dir

    echo -e "---------- chmod test finish ----------\n" >> $LOG
}

chmod_test
