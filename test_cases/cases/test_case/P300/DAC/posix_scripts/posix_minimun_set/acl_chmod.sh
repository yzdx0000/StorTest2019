#!/bin/bash

source ./acl_common.sh
# dir=$mnt/chmod_test  
dir=$1/chmod_test  # changed by zhanghan 20181126

#/*****************************************************************************
# �������  : DAC-STUC-CLIENT-068
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ01
# �������  : �����ļ���chmod�ı�mode������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��chmod�ı��ļ�Ȩ��λ:0666
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             group::rw-
#             other::rw-
#             2���ļ�f0��modeΪ0666
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-069
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ02
# �������  : �����ļ���chmod�ı�mode������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rwx"
#             3��ʹ��stat�鿴�ļ�f0��mode
#             2��ʹ��chmod�ı��ļ�Ȩ��λ:0446
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::r--
#             user:u1:rwx    #effective:r--
#             group::r--
#             maks::r--
#             other::rw-
#             2���ļ�f0��modeΪ0674
#             3���ļ�f0��modeΪ0446
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-070
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ03
# �������  : �����ļ���chmod�ı�mode������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��stat�鿴�ļ�f0��mode
#             2��ʹ��chmod�ı��ļ�Ȩ��λ:0777
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rwx
#             user:u1:rw-
#             group::r--
#             maks::rwx
#             other::rwx
#             2���ļ�f0��modeΪ0664
#             3���ļ�f0��modeΪ0777
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-071
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ04
# �������  : ����Ŀ¼��chmod�ı�mode�����Ŀ¼��acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��chmod�ı��ļ�Ȩ��λ:0644
#             4��ʹ��getfacl�鿴Ŀ¼d0��acl
#             5��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
#             user::rw-
#             group::r--
#             other::r--
#             2��Ŀ¼d0��modeΪ0644
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-072
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ05
# �������  : ����Ŀ¼��chmod�ı�mode�����Ŀ¼��acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��setfacl����Ŀ¼d0��g1����:"group:g1:rwx"
#             3��ʹ��setfacl����Ŀ¼d0�ļ̳�u1����:"default:user:u1:rwx"
#             4��ʹ��chmod�ı��ļ�Ȩ��λ:0644
#             5��ʹ��getfacl�鿴Ŀ¼d0��acl
#             6��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
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
#             2��Ŀ¼d0��modeΪ0644
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-073
# ������Ŀ  : 1��chmod�ı��ļ�Ȩ��λ�����Ķ�Ӧ��acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : ֧��ʹ��chmod����Ȩ��λ06
# �������  : ����Ŀ¼��chmod�ı�mode�����Ŀ¼��acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d0
#             2��ʹ��setfacl����Ŀ¼d0��g1����:"group:g1:r-x"
#             3��ʹ��setfacl����Ŀ¼d0�ļ̳�u1����:"default:user:u1:r--"
#             4��ʹ��chmod�ı��ļ�Ȩ��λ:0777
#             5��ʹ��getfacl�鿴Ŀ¼d0��acl
#             6��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
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
#             2��Ŀ¼d0��modeΪ0777
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
