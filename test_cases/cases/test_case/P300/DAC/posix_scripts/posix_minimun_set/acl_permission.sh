#!/bin/bash

source ./acl_common.sh
# dir=$mnt/perm_dir
dir=$1/perm_dir  # changed by zhanghan 20181126
data="abc1234567890"


#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-074
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过后才会去检查其他设置的权限
# 用例标题  : 可以使用chmod来设置权限01
# 用例简介  : 设置文件用户u1有写权限，所有组权限mode无写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用chmod将文件f0的权限位设置为:0644
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行读操作
#             7、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0644
#             2、对f0对操作返回0
#             3、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test1()
{
    f1=$1/f1
    touch $f1
    echo $data > $f1
    sync

    setfacl -m user:u1:rw- $f1
    chmod 644 $f1
    clean_cache

    mode=`su u1 -c "stat $f1 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0644 ]
    then
        echo "permission_test1 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "cat $f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test1 test failed: " >> $ELOG
        echo "read permission error!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f1" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test1 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-075
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过后才会去检查其他设置的权限
# 用例标题  : 可以使用chmod来设置权限02
# 用例简介  : 设置文件用户u1无写权限，所有组权限mode有写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:r--"
#             3、使用chmod将文件f0的权限位设置为:0664
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月5日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test2()
{
    f2=$1/f2
    touch $f2
    echo $data > $f2
    sync

    setfacl -m user:u1:r-- $f2
    chmod 664 $f2
    clean_cache

    mode=`su u1 -c "stat $f2 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test2 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f2" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test2 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test2 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-076
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过后才会去检查其他设置的权限
# 用例标题  : 可以使用chmod来设置权限03
# 用例简介  : 设置文件用户u1有写权限，所有组权限mode有写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、新创建文件对象mode为0644
#             3、客户端存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用chmod将文件f0的权限位设置为:0664
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回0
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test3()
{
    f3=$1/f3
    touch $f3
    echo $data > $f3
    sync

    setfacl -m user:u1:rw- $f3
    chmod 664 $f3
    clean_cache

    mode=`su u1 -c "stat $f3 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test3 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f3" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test3 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-077
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限01
# 用例简介  : 设置文件用户u1有写权限，所有组权限mode无写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用setfacl设置文件f0的mask主体:"mask::r--"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行读操作
#             7、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0644
#             2、对f0读操作返回0
#             3、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test4()
{
    f4=$1/f4
    touch $f4
    echo $data > $f4
    sync

    setfacl -m user:u1:rw- $f4
    setfacl -m mask::r-- $f4
    clean_cache

    mode=`su u1 -c "stat $f4 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0644 ]
    then
        echo "permission_test4 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "cat $f4" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test4 test failed: " >> $ELOG
        echo "read permission error!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f4" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test4 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test4 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-078
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限02
# 用例简介  : 设置文件用户u1无写权限，所有组权限mode有写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:r--"
#             3、使用setfacl设置文件f0的mask主体:"mask::rw-"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test5()
{
    f5=$1/f5
    touch $f5
    echo $data > $f5
    sync

    setfacl -m user:u1:r-- $f5
    setfacl -m mask::rw- $f5
    clean_cache

    mode=`su u1 -c "stat $f5 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test5 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f5" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test5 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test5 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-079
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限03
# 用例简介  : 设置文件用户u1有写权限，所有组权限mode有写权限，切换到用户u1下
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的u1主体:"user:u1:rw-"
#             3、使用setfacl设置文件f0的mask主体:"mask::rwx"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0674
#             2、对f0写操作返回0
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年4月6日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test6()
{
    f6=$1/f6
    touch $f6
    echo $data > $f6
    sync

    setfacl -m user:u1:rw- $f6
    setfacl -m mask::rwx $f6
    clean_cache

    mode=`su u1 -c "stat $f6 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0674 ]
    then
        echo "permission_test6 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f6" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test6 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test6 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-080
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限04
# 用例简介  : 设置文件所有组g1无写权限，所有组权限mode有写权限，切换到文件所有者
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1属于组g1
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g1主体:"group:g1:r--"
#             3、使用setfacl设置文件f0的mask主体:"mask::rw-"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test7()
{
    f7=$1/f7
    touch $f7
    echo $data > $f7
    sync

    setfacl -m group:g1:r-- $f7
    setfacl -m mask::rw- $f7
    clean_cache

    mode=`su u1 -c "stat $f7 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test7 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f7" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test7 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test7 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-081
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限05
# 用例简介  : 设置文件所有组g1有写权限，所有组权限mode无写权限，切换到文件所有者
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1属于组g1
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g1主体:"group:g1:rw-"
#             3、使用setfacl设置文件f0的mask主体:"mask::r--"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0644
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test8()
{
    f8=$1/f8
    touch $f8
    echo $data > $f8
    sync

    setfacl -m group:g1:rw- $f8
    setfacl -m mask::r-- $f8
    clean_cache

    mode=`su u1 -c "stat $f8 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0644 ]
    then
        echo "permission_test8 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f8" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test8 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test8 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-082
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限06
# 用例简介  : 设置文件所有组g1有写权限，所有组权限mode有写权限，切换到文件所有者
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1属于组g1
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g1主体:"group:g1:rw-"
#             3、使用setfacl设置文件f0的mask主体:"mask::rwx"
#             4、切换到用户u1
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0674
#             2、对f0写操作返回0
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test9()
{
    f9=$1/f9
    touch $f9
    echo $data > $f9
    sync

    setfacl -m group:g1:rw- $f9
    setfacl -m mask::rwx $f9
    clean_cache

    mode=`su u1 -c "stat $f9 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0674 ]
    then
        echo "permission_test9 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u1 -c "echo $data >> $f9" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test9 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test9 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-083
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限07
# 用例简介  : 设置文件所有组无写权限，切换到所有组中其他用户
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1，u2属于组g1
# 输    入  :
# 执行步骤  : 1、切换到用户u1
#             2、在客户端创建文件f0
#             3、切换到用户u2
#             4、使用stat查看文件f0的mode
#             5、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0644
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test10()
{
    f10=$1/f10
    su u1 -c "touch $f10"
    su u1 -c "echo $data > $f10"

    clean_cache

    mode=`su u2 -c "stat $f10 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0644 ]
    then
        echo "permission_test10 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u2 -c "echo $data >> $f10" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test10 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test10 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-084
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限08
# 用例简介  : 设置文件所有组无写权限，切换到所有组中其他用户
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1，u2属于组g1
# 输    入  :
# 执行步骤  : 1、切换到用户u1
#             2、在客户端创建文件f0
#             3、使用chmod将文件mode设为: 664
#             3、切换到用户u2
#             4、使用stat查看文件f0的mode
#             5、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回0
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test11()
{
    f11=$1/f11
    su u1 -c "touch $f11"
    su u1 -c "echo $data > $f11"

    su u1 -c "chmod 664 $f11"
    clean_cache

    mode=`su u2 -c "stat $f11 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test11 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u2 -c "echo $data >> $f11" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test11 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test11 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-085
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限09
# 用例简介  : 设置文件所有组g1无写权限，所有组权限mode有写权限，切换到g1组中其他用户
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1，u2属于组g1
# 输    入  :
# 执行步骤  : 1、切换到用户u1
#             2、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g1主体:"group:g1:r--"
#             3、使用setfacl设置文件f0的mask主体:"mask::rw-"
#             4、切换到用户u2
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0664
#             2、对f0写操作返回1(Permission denied)
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test12()
{
    f12=$1/f12
    su u1 -c "touch $f12"
    su u1 -c "echo $data > $f12"

    su u1 -c "setfacl -m group:g2:r-- $f12"
    su u1 -c "setfacl -m mask::rw- $f12"
    clean_cache

    mode=`su u2 -c "stat $f12 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0664 ]
    then
        echo "permission_test12 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u2 -c "echo $data >> $f12" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_test12 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test12 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-086
# 测试项目  : 1、POSIX首先使用权限位来检查权限
#             2、当权限位检查通过时才会去检查其他设置的权限
#             3、支持POSIX rwx权限组合
# 用例标题  : 支持设置ACE权限10
# 用例简介  : 设置文件所有组g1有写权限，所有组权限mode有写权限，切换到g1组中其他用户
#             检查文件mode，执行文件的写操作
# 预置条件  : 1、挂载的parastor文件系统支持posix acl
#             2、客户端存在多个用户和组
#             3、新创建文件对象mode为0644
#             4、用户u1、u2属于组g1,u2属于组g2
#
# 输    入  :
# 执行步骤  : 1、切换到用户u1
#             2、在客户端创建文件f0
#             2、使用setfacl设置文件f0的g2主体:"group:g2:rw-"
#             3、使用setfacl设置文件f0的mask主体:"mask::rwx"
#             4、切换到用户u2
#             5、使用stat查看文件f0的mode
#             6、对文件f0执行写操作
# 预期结果  : 1、文件f0的mode为:0674
#             2、对f0写操作返回0
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年8月2日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
permission_test13()
{
    f13=$1/f13
    su u1 -c "touch $f13"
    su u1 -c "echo $data > $f13"

    su u1 -c "setfacl -m group:g2:rw- $f13"
    su u1 -c "setfacl -m mask::rwx $f13"
    clean_cache

    mode=`su u2 -c "stat $f13 | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0674 ]
    then
        echo "permission_test13 test failed: " >> $ELOG
        echo "mode not equiv!!!" >> $ELOG
    fi

    su u2 -c "echo $data >> $f13" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_test13 test failed: " >> $ELOG
        echo "write permission error!!!" >> $ELOG
    fi

    echo "permission_test13 test finish!" >> $LOG
}

permission_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
        chmod 777 $dir
    fi

    echo -e "---------- permission test start ----------" >> $LOG
    # user check, chmod
    permission_test1 $dir
    permission_test2 $dir
    permission_test3 $dir
    # user check, posix aclfinish
    permission_test4 $dir
    permission_test5 $dir
    permission_test6 $dir
    # group check, posix acfinish
    permission_test7 $dir
    permission_test8 $dir
    permission_test9 $dir
    permission_test10 $dir
    permission_test11 $dir
    permission_test12 $dir
    permission_test13 $dir

    echo -e "---------- permission test finish -----------\n" >> $LOG
}

permission_test
