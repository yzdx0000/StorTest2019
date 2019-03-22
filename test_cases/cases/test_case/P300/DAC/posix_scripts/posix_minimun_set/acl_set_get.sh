#!/bin/bash

source ./acl_common.sh
# dir=$mnt/set_get_test
dir=$1/set_get_test  # changed by zhanghan 20181126

#/*****************************************************************************
# �������  : DAC-STUC-CLIENT-046
# ������Ŀ  : �ͻ�������������������
# ��������  : ֧������ACL01
# �������  : �ڿͻ���ʹ�ù��������ļ��������������壬������ý����mode
# Ԥ������  : ���ص�parastor�ļ�ϵͳ֧��posix acl
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��user��group��other����:
#             "user::rwx; group::rwx; other::rwx"
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��Ȩ��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rwx
#             group::rwx
#             other::rwx
#             2���ļ�f0��modeΪ0777
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-047
# ������Ŀ  : �ͻ�������mask����
# ��������  : ֧������ACL02
# �������  : �ڿͻ���ʹ�ù��������ļ���mask���壬������ý����mode
# Ԥ������  : ���ص�parastor�ļ�ϵͳ֧��posix acl
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��mask����:"mask::rwx"
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��Ȩ��mode
# Ԥ�ڽ��  : 1���ļ�f0��aclΪ:
#             user::rw-
#             group::r--
#             mask::rwx
#             other::r--
#             2���ļ�f0��modeΪ0674
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-048
# ������Ŀ  : �ͻ������������û�����
# ��������  : ֧������ACL03
# �������  : �ڿͻ���ʹ�ù��������ļ��������û����壬������ý����mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rwx"
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��Ȩ��mode
# Ԥ�ڽ��  : 1���ļ�f0��acl:
#             user::rw-
#             user:u1:rwx
#             group::r--
#             mask::rwx
#             other::r--
#             2���ļ�f0��modeΪ0674
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-049
# ������Ŀ  : �ͻ�����������������
# ��������  : ֧������ACL04
# �������  : �ڿͻ���ʹ�ù��������ļ������������壬������ý����mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g1����:"group:g1:rwx"
#             3��ʹ��getfacl�鿴�ļ�f0��acl
#             4��ʹ��stat�鿴�ļ�f0��Ȩ��mode
# Ԥ�ڽ��  : 1���ļ�f0��acl:
#             user::rw-
#             group::r--
#             group:g1:rwx
#             mask::rwx
#             other::r--
#             2���ļ�f0��modeΪ0674
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-050
# ������Ŀ  : ֧��POSIX��rwx���ֲ�ͬ���
# ��������  : ֧������ACL05
# �������  : �ڿͻ��˴���512���ļ������ղ�ͬ��rwx�������
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f1~f512
#             2��ʹ��setfacl���ղ�ͬ��rwx���������ļ�f1~f512��user��group��other����
#             3��ʹ��getfacl�鿴�ļ�f1~f512��acl
#             4��ʹ��stat�鿴�ļ�f1~f512��Ȩ��mode
#             (example: f1   user::---; group::---; other::---
#                       f2   user::---; group::---; other::--x
#                       f3   user::---; group::---; other::-w-
#                       ...
#                       f512 user::rwx; group::rwx; other::rwx
#             )
# Ԥ�ڽ��  : �ļ�f1~f512��user��group��other����Ȩ�������õ���ͬ
#
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-051
# ������Ŀ  : ֧��ɾ���ļ���ACL
# ��������  : ֧������ACL06
# �������  : �ڿͻ���ʹ�ù��������ļ���acl��Ȼ��ɾ����������ݼ���ʽ
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��setfaclɾ��POSIX_ACL
#             4��ʹ��getfacl��ȡ�ļ�f0��ACL
#             5��ʹ��stat�鿴�ļ�f0��mode
# Ԥ�ڽ��  : 1���ļ�f0��ACL���ݼ���ʽΪ:
#                user::rw-
#                group::r--
#                other::r--
#             2���ļ�f0 mode: 0644
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��6��1��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-052
# ������Ŀ  : ֧���޸��ļ���ACL���޸ĺ�ACL��ȷ
# ��������  : ֧������ACL07
# �������  : �ڿͻ���ʹ�ù��߻�ȡ�ļ���acl���޸�mask ace��������ݼ���ʽ
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1��g1����:
#             "user:u1:rw-","group:g1:rwx"
#             3��ʹ��getfacl�����ļ�f0��mask����:"mask::r--"
#             4��ʹ��getfacl��ȡ�ļ�f0��ACL
#             5��ʹ��stat����ļ�Ȩ��mode
#             6��ʹ��getfacl�����ļ�f0��mask����:"mask::rwx"
#             7��ʹ��getfacl��ȡ�ļ�f0��ACL
#             8��ʹ��stat����ļ�Ȩ��mode
# Ԥ�ڽ��  : 1���ļ�f0��ACL���ݼ���ʽΪ:
#                user::rw-
#                user:u1:rw-             #effective:r--
#                group::r--
#                group:g1:rwx            #effective:r--
#                mask::r--
#                other::r--
#             2���ļ�Ȩ��modeΪ: 0644
#             3���ļ�f0��ACL���ݼ���ʽΪ:
#                user::rw-
#                user:u1:rw-
#                group::r--
#                group:g1:rwx
#                mask::rwx
#                other::r--
#             4���ļ�Ȩ��modeΪ:0674
#
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��6��1��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-053
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL08
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�ļ̳�mask ace��Ȩ�޴�����Ч���������Ȩ��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1�ļ̳�mask����:"mask::rwx"
#             4��ʹ��getfacl��ȡĿ¼d1��ACL
#             5��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::rwx
#                default:group::r-x
#                default:mask::rwx
#                default:other::r-x
#             2��Ŀ¼d1��Ȩ��mode:0755
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��6��4��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-054
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL09
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�ļ̳�mask ace��Ȩ��С����Ч���������Ȩ��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1�ļ̳�mask����:"mask::r--"
#             4��ʹ��getfacl��ȡĿ¼d1��ACL
#             5��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::rwx
#                default:group::r-x          #effective:r--
#                default:mask::r--
#                default:other::r-x
#             2��Ŀ¼d1��Ȩ��mode:0755
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-055
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL10
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�������û�ace�����ü̳�group ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1��u1����:"user:u1:r-x"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�group����:"group::rwx"
#             4��ʹ��getfacl��ȡĿ¼d1��ACL
#             5��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
#                user::rwx
#                user:u1:r-x
#                group::r-x
#                mask::r-x
#                other::r-x
#                default:user::rwx
#                default:group::rwx
#                default:other::r-x
#             2��Ŀ¼d1��Ȩ��mode:0755
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-056
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL11
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�������û�ace�����ü̳������� ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1��u1����:"user:u1:rwx"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�g1����:"group:g1:r--"
#             4��ʹ��getfacl��ȡĿ¼d1��ACL
#             5��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
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
#             2��Ŀ¼d1��Ȩ��mode:0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-057
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL12
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�������û�ace�����ü̳������� ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1��u1����:"user:u1:rwx"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�g1����:"group:g1:rwx"
#             4��ʹ��setfacl����Ŀ¼d1��mask����:"mask::rw-"
#             5��ʹ��getfacl��ȡĿ¼d1��ACL
#             6��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
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
#             2��Ŀ¼d1��Ȩ��mode:0765
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-058
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL13
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�������û�ace�����ü̳������� ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1��u1����:"user:u1:rwx"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�g1����:"group:g1:rwx"
#             4��ʹ��setfacl����Ŀ¼d1�ļ̳�mask����:"mask::rw-"
#             5��ʹ��getfacl��ȡĿ¼d1��ACL
#             6��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
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
#             2��Ŀ¼d1��Ȩ��mode:0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-059
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL14
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�Ķ�������û�ace�����ü̳ж�������� ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1�ļ̳�u1����:"user:u1:rwx"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�u2����:"user:u2:rw-"
#             4��ʹ��setfacl����Ŀ¼d1�ļ̳�u3����:"user:u3:r-x"
#             5��ʹ��setfacl����Ŀ¼d1��g1����:"group:g1:r--"
#             6��ʹ��setfacl����Ŀ¼d1��g1����:"group:g2:-w-"
#             7��ʹ��setfacl����Ŀ¼d1��g1����:"group:g3:--x"
#             8��ʹ��getfacl��ȡĿ¼d1��ACL
#             9��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
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
#             2��Ŀ¼d1��Ȩ��mode:0775
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-060
# ������Ŀ  : ֧������Ŀ¼��ACL
# ��������  : ֧������ACL15
# �������  : �ڿͻ���ʹ�ù�������Ŀ¼�̳���������ace��
#             ���Ŀ¼��acl��Ȩ��mode
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´���Ŀ¼����modeΪ0755
#             3��ϵͳ���ڶ���û�����
#
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴���Ŀ¼d1
#             2��ʹ��setfacl����Ŀ¼d1�ļ̳�user����:"user::r--"
#             3��ʹ��setfacl����Ŀ¼d1�ļ̳�group����:"group::rwx"
#             4��ʹ��setfacl����Ŀ¼d1�ļ̳�other����:"other:::rwx"
#             5��ʹ��getfacl��ȡĿ¼d1��ACL
#             6��ʹ��stat�鿴Ŀ¼d1��mode
# Ԥ�ڽ��  : 1��Ŀ¼d1��ACL���ݼ���ʽΪ:
#                user::rwx
#                group::r-x
#                other::r-x
#                default:user::r--
#                default:group::rwx
#                default:other::rwx
#             2��Ŀ¼d1��Ȩ��mode:0755
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
