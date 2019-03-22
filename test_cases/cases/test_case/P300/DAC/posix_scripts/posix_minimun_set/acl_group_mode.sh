#!/bin/bash

source ./acl_common.sh
# dir=$mnt/group_mode_test
dir=$1/group_mode_test  # changed by zhanghan 20181126


#/*****************************************************************************
# �������  : DAC-STUC-CLIENT-087
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��01
# �������  : ����groupȨ�ޣ�����ļ�mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��group����:"group::rwx"
#             3��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : ���ص��ļ�f0��modeΪ:0674
#
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-088
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��02
# �������  : ����groupȨ�ޣ����Ŀ¼mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��setfacl����Ŀ¼d0��group����:"group::rwx"
#             3��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : ���ص�Ŀ¼d0��modeΪ:0775
#
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-089
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��03
# �������  : �����������Ȩ�ޣ�����mask�����дȨ�ޣ�����ļ�mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��group����:"group::rw-"
#             3��ʹ��stat�鿴�ļ�f0��mode
#             4��ʹ��setfacl�����ļ�f0��mask����:"mask::rwx"
#             5��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1����һ�η��ص��ļ�f0��modeΪ:0664
#             2���ڶ��η��ص�modeΪ0674
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-090
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��04
# �������  : �����������дȨ�ޣ�����mask�����Ȩ�ޣ����Ŀ¼mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��setfacl����Ŀ¼d0��group����:"group::rwx"
#             3��ʹ��stat�鿴Ŀ¼d0��mode
#             4��ʹ��setfacl����Ŀ¼d0��mask����:"mask::r--"
#             5��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1����һ�η��ص�Ŀ¼d0��modeΪ:0775
#             2���ڶ��η��ص�modeΪ0745
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-091
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��05
# �������  : �����������дȨ�ޣ�����mask�����Ȩ�ޣ�����ļ�mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3��ϵͳ���ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��setfacl�����ļ�f0��g1����:"group:g1:rwx"
#             4��ʹ��setfacl�����ļ�f0��mask����:"mask::---"
#             5��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : ���ص��ļ�f0��modeΪ:0604
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-092
# ������Ŀ  : 1��ʹ�ü��mask����Ϊ���������Ȩ��
#             2��֧��POSIX rwxȨ�����
# ��������  : ֧�����������������������Ȩ��06
# �������  : �����������дȨ�ޣ�����mask�����Ȩ�ޣ����Ŀ¼mdoe
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��setfacl����Ŀ¼d0��u1����:"user:u1:r--"
#             3��ʹ��setfacl����Ŀ¼d0��g1����:"group:g1:r-x"
#             4��ʹ��setfacl����Ŀ¼d0��mask����:"mask::rwx"
#             5��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : ���ص�Ŀ¼d0��modeΪ:0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
