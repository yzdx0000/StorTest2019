#!/bin/bash

source ./acl_common.sh
# dir=$mnt/group_mode_test
dir=$1/group_mode_test  # changed by zhanghan 20181126


#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-087
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限01
# 用例简介  : 设置group权限，检查文件mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的group主体:"group::rwx"
#             3、使用stat查看文件f0的mode
# 预期结果  : 返回的文件f0的mode为:0674
#
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test1()
{
    f=f1
    touch $1/$f
    setfacl -m group::rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "group_mode_test1 test fiald:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-088
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限02
# 用例简介  : 设置group权限，检查目录mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的group主体:"group::rwx"
#             3、使用stat查看目录d0的mode
# 预期结果  : 返回的目录d0的mode为:0775
#
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test2()
{
    d=d2
    mkdir $1/$d
    setfacl -m group::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "group_mode_test2 test fiald:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test2 test finish!" >> $LOG
}

##/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-089
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限03
# 用例简介  : 设置所有组读权限，设置mask主体读写权限，检查文件mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的group主体:"group::rw-"
#             3、使用stat查看文件f0的mode
#             4、使用setfacl设置文件f0的mask主体:"mask::rwx"
#             5、使用stat查看文件f0的mode
# 预期结果  : 1、第一次返回的文件f0的mode为:0664
#             2、第二次返回的mode为0674
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test3()
{
    f=f3
    touch $1/$f
    setfacl -m group::rw- $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0664 ]
    then
        echo "group_mode_test3 test fiald:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    setfacl -m mask::rwx $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0674 ]
    then
        echo "group_mode_test3 test fiald:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-090
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限04
# 用例简介  : 设置所有组读写权限，设置mask主体读权限，检查目录mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的group主体:"group::rwx"
#             3、使用stat查看目录d0的mode
#             4、使用setfacl设置目录d0的mask主体:"mask::r--"
#             5、使用stat查看目录d0的mode
# 预期结果  : 1、第一次返回的目录d0的mode为:0775
#             2、第二次返回的mode为0745
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test4()
{
    d=d4
    mkdir $1/$d
    setfacl -m group::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "group_mode_test4 test fiald:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    setfacl -m mask::r-- $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0745 ]
    then
        echo "group_mode_test4 test fiald:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test4 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-091
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限05
# 用例简介  : 设置所有组读写权限，设置mask主体读权限，检查文件mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用setfacl设置文件f0的g1主体:"group:g1:rwx"
#             4、使用setfacl设置文件f0的mask主体:"mask::---"
#             5、使用stat查看文件f0的mode
# 预期结果  : 返回的文件f0的mode为:0604
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test5()
{
    f=f5
    touch $1/$f
    setfacl -m user:u1:rw- $1/$f
    setfacl -m group:g1:rwx $1/$f
    setfacl -m mask::--- $1/$f
    clean_cache

    mode=`stat $1/$f | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0604 ]
    then
        echo "group_mode_test5 test fiald:" >> $ELOG
        echo "$1/$f mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test5 test finish!" >> $LOG
}


#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-092
# 测试项目  : 1、使用检查mask来作为所有组类的权限
#             2、支持POSIX rwx权限组合
# 用例标题  : 支持设置特殊主体所有组类的权限06
# 用例简介  : 设置所有组读写权限，设置mask主体读权限，检查目录mdoe
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建目录对象mode为0755
#             3、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的u1主体:"user:u1:r--"
#             3、使用setfacl设置目录d0的g1主体:"group:g1:r-x"
#             4、使用setfacl设置目录d0的mask主体:"mask::rwx"
#             5、使用stat查看目录d0的mode
# 预期结果  : 返回的目录d0的mode为:0775
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
group_mode_test6()
{
    d=d6
    mkdir $1/$d
    setfacl -m user:u1:r-- $1/$d
    setfacl -m group:g1:r-x $1/$d
    setfacl -m mask::rwx $1/$d
    clean_cache

    mode=`stat $1/$d | grep Uid | cut -d ' ' -f2 | cut -b 2-5`
    if [ $mode -ne 0775 ]
    then
        echo "group_mode_test6 test fiald:" >> $ELOG
        echo "$1/$d mode not equiv!!!, mode: $mode" >> $ELOG
    fi

    echo "group_mode_test6 test finish!" >> $LOG
}

group_mode_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
    fi

    echo -e "---------- group mode test start ----------" >> $LOG

    group_mode_test1 $dir
    group_mode_test2 $dir
    group_mode_test3 $dir
    group_mode_test4 $dir
    group_mode_test5 $dir
    group_mode_test6 $dir

    echo -e "---------- group mode test finish ----------\n" >> $LOG
}

group_mode_test
