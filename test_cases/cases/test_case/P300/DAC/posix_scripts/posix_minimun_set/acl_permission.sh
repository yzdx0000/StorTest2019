#!/bin/bash

source ./acl_common.sh
# dir=$mnt/perm_dir
dir=$1/perm_dir  # changed by zhanghan 20181126
data="abc1234567890"


#/*****************************************************************************
# �������  : DAC-STUC-CLIENT-074
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ����Ż�ȥ����������õ�Ȩ��
# ��������  : ����ʹ��chmod������Ȩ��01
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��chmod���ļ�f0��Ȩ��λ����Ϊ:0644
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ�ж�����
#             7�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0644
#             2����f0�Բ�������0
#             3����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-075
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ����Ż�ȥ����������õ�Ȩ��
# ��������  : ����ʹ��chmod������Ȩ��02
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:r--"
#             3��ʹ��chmod���ļ�f0��Ȩ��λ����Ϊ:0664
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��5��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-076
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ����Ż�ȥ����������õ�Ȩ��
# ��������  : ����ʹ��chmod������Ȩ��03
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���´����ļ�����modeΪ0644
#             3���ͻ��˴��ڶ���û�����
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��chmod���ļ�f0��Ȩ��λ����Ϊ:0664
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������0
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-077
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��01
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::r--"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ�ж�����
#             7�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0644
#             2����f0����������0
#             3����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-078
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��02
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:r--"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rw-"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-079
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��03
# �������  : �����ļ��û�u1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����û�u1��
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��u1����:"user:u1:rw-"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rwx"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0674
#             2����f0д��������0
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��4��6��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-080
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��04
# �������  : �����ļ�������g1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����ļ�������
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1������g1
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g1����:"group:g1:r--"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rw-"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-081
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��05
# �������  : �����ļ�������g1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����ļ�������
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1������g1
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g1����:"group:g1:rw-"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::r--"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0644
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-082
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��06
# �������  : �����ļ�������g1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л����ļ�������
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1������g1
# ��    ��  :
# ִ�в���  : 1���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g1����:"group:g1:rw-"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rwx"
#             4���л����û�u1
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0674
#             2����f0д��������0
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-083
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��07
# �������  : �����ļ���������дȨ�ޣ��л����������������û�
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1��u2������g1
# ��    ��  :
# ִ�в���  : 1���л����û�u1
#             2���ڿͻ��˴����ļ�f0
#             3���л����û�u2
#             4��ʹ��stat�鿴�ļ�f0��mode
#             5�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0644
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-084
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��08
# �������  : �����ļ���������дȨ�ޣ��л����������������û�
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1��u2������g1
# ��    ��  :
# ִ�в���  : 1���л����û�u1
#             2���ڿͻ��˴����ļ�f0
#             3��ʹ��chmod���ļ�mode��Ϊ: 664
#             3���л����û�u2
#             4��ʹ��stat�鿴�ļ�f0��mode
#             5�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������0
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-085
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��09
# �������  : �����ļ�������g1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л���g1���������û�
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1��u2������g1
# ��    ��  :
# ִ�в���  : 1���л����û�u1
#             2���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g1����:"group:g1:r--"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rw-"
#             4���л����û�u2
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0664
#             2����f0д��������1(Permission denied)
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
# �������  : DAC-STUC-CLIENT-086
# ������Ŀ  : 1��POSIX����ʹ��Ȩ��λ�����Ȩ��
#             2����Ȩ��λ���ͨ��ʱ�Ż�ȥ����������õ�Ȩ��
#             3��֧��POSIX rwxȨ�����
# ��������  : ֧������ACEȨ��10
# �������  : �����ļ�������g1��дȨ�ޣ�������Ȩ��mode��дȨ�ޣ��л���g1���������û�
#             ����ļ�mode��ִ���ļ���д����
# Ԥ������  : 1�����ص�parastor�ļ�ϵͳ֧��posix acl
#             2���ͻ��˴��ڶ���û�����
#             3���´����ļ�����modeΪ0644
#             4���û�u1��u2������g1,u2������g2
#
# ��    ��  :
# ִ�в���  : 1���л����û�u1
#             2���ڿͻ��˴����ļ�f0
#             2��ʹ��setfacl�����ļ�f0��g2����:"group:g2:rw-"
#             3��ʹ��setfacl�����ļ�f0��mask����:"mask::rwx"
#             4���л����û�u2
#             5��ʹ��stat�鿴�ļ�f0��mode
#             6�����ļ�f0ִ��д����
# Ԥ�ڽ��  : 1���ļ�f0��modeΪ:0674
#             2����f0д��������0
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��8��2��
#    ��    ��   : wangsen
#    �޸�����   : �������
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
