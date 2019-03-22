#!/bin/bash

source ./acl_common.sh
# dir=$mnt/inherit_test
dir=$1/inherit_test  # changed by zhanghan 20181126

#/*****************************************************************************
# �������  : DAC-STUC-CLIENT-038
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ����ļ�ʱ��Ŀ¼�޿ɼ̳е�acl��
#             ��Ҫmode
#             2�������ļ���mode��ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL01
# �������  : ���޿ɼ̳�acl�ĸ�Ŀ¼�´����ļ�������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���������ļ�����Ŀ¼�޿ɼ̳е�ACL
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2����Ŀ¼dir�ڴ����ļ�f0
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             group::r--
#             other::r--
#             2���ļ�f0��modeΪ0644
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-039
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ���Ŀ¼ʱ��Ŀ¼�޿ɼ̳е�acl��
#             ��Ҫmode
#             2������Ŀ¼��mode��ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL02
# �������  : ���޿ɼ̳�acl�ĸ�Ŀ¼�´���Ŀ¼�����Ŀ¼��acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��������Ŀ¼����Ŀ¼�޿ɼ̳е�ACL
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2����Ŀ¼dir�ڴ���Ŀ¼d0
#             3��ʹ��getfacl�鿴Ŀ¼d0��acl
#             4��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
#             user::rwx
#             group::r-x
#             other::r-x
#             2��Ŀ¼d0��modeΪ0755
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-040
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ����ļ�ʱ��Ŀ¼�пɼ̳е�acl��
#             �ļ��̳и�Ŀ¼�ɼ̳е�acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL03
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´����ļ�������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:mask::rwx"
#             3����Ŀ¼dir�ڴ����ļ�f0
#             4��ʹ��getfacl�鿴�ļ�f0��acl
#             5��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             group::r-x           #effective:r--
#             mask::rw-
#             other::r--
#             2���ļ�f0��modeΪ0664
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-041
# ������Ŀ  : 1����posix_acl���ص�˽�пͻ����ڴ���Ŀ¼ʱ��Ŀ¼�пɼ̳е�acl��
#             ��Ŀ¼�̳и�Ŀ¼�ɼ̳е�acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL04
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´���Ŀ¼�����Ŀ¼��acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����Ŀ¼�пɼ̳еĵ�acl
#             3���´���Ŀ¼����modeΪ0755
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:mask::rwx"
#             3����Ŀ¼dir�ڴ���Ŀ¼d0
#             4��ʹ��getfacl�鿴Ŀ¼d0��acl
#             5��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
#             user::rwx
#             group::r-x
#             mask::rwx
#             other::r-x
#             default:user::rwx
#             default:group::r-x
#             default:mask::rwx
#             default:other::r-x
#             2��Ŀ¼d0��modeΪ0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-042
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ����ļ�ʱ��Ŀ¼�пɼ̳е�acl��
#             �ļ��̳и�Ŀ¼�ɼ̳е�acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL04
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´����ļ�������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:user:u1:rwx"
#             3��ʹ��setfaclΪĿ¼dir���default acl:"default:group:g1:r-x"
#             4��ʹ��setfaclΪĿ¼dir���default acl:"default:mask::--x"
#             5����Ŀ¼dir�ڴ����ļ�f0
#             6��ʹ��getfacl�鿴�ļ�f0��acl
#             7��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             user:u1:rwx          #effective:---
#             group::r-x           #effective:---
#             group:g1:r-x         #effective:---
#             mask::---
#             other::r--
#             2���ļ�f0��modeΪ0604
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-043
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ���Ŀ¼ʱ��Ŀ¼�пɼ̳е�acl��
#             ��Ŀ¼�̳и�Ŀ¼�ɼ̳е�acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL05
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´�����Ŀ¼������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:user:u1:rwx"
#             3��ʹ��setfaclΪĿ¼dir���default acl:"default:group:g1:r-x"
#             4����Ŀ¼dir�ڴ���Ŀ¼d0
#             5��ʹ��getfacl�鿴Ŀ¼d0��acl
#             6��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
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
#             2��Ŀ¼d0��modeΪ0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-044
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ����ļ�ʱ��Ŀ¼�пɼ̳е�acl��
#             �ļ��̳и�Ŀ¼�ɼ̳е�acl
#             2�������ļ���mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL06
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´����ļ�������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:user:u1:rwx"
#             3��ʹ��setfaclΪĿ¼dir���default acl:"default:user:u2:r-x"
#             4��ʹ��setfaclΪĿ¼dir���default acl:"default:user:u3:rw-"
#             5��ʹ��setfaclΪĿ¼dir���default acl:"default:mask::r--"
#             6����Ŀ¼dir�ڴ����ļ�f0
#             7��ʹ��getfacl�鿴�ļ�f0��acl
#             8��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             user:u1:rwx          #effective:r--
#             user:u2:r-x          #effective:r--
#             user:u3:rw-          #effective:r--
#             group::r-x           #effective:r--
#             mask::r--
#             other::r--
#             2���ļ�f0��modeΪ0644
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-045
# ������Ŀ  : 1����posix_acl���صĿͻ����ڴ���Ŀ¼ʱ��Ŀ¼�пɼ̳е�acl��
#             ��Ŀ¼�̳и�Ŀ¼�ɼ̳е�acl
#             2������Ŀ¼��mode�ܿɼ̳�acl�Լ�ϵͳumaskӰ��
# ��������  : �����¶���̳пɼ̳�ACL07
# �������  : ���пɼ̳�acl�ĸ�Ŀ¼�´�����Ŀ¼������ļ���acl��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼dir
#             2��ʹ��setfaclΪĿ¼dir���default acl:"default:group:g1:rwx"
#             3��ʹ��setfaclΪĿ¼dir���default acl:"default:group:g2:r-x"
#             4��ʹ��setfaclΪĿ¼dir���default acl:"default:group:g3:--x"
#             5����Ŀ¼dir�ڴ���Ŀ¼d0
#             6��ʹ��getfacl�鿴Ŀ¼d0��acl
#             7��ʹ��stat�鿴Ŀ¼d0��mode
# Ԥ�ڽ��  : 1��Ŀ¼d0��aclΪ:
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
#             2��Ŀ¼d0��modeΪ0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��3��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
