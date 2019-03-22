#!/bin/sh
#
# Date:     2016-08-03
# Author:   Wang Xiao (wangxiaob@sugon.com)
#

source ./config.sh

acc_mask_all='rwpxdDaARWcCoSeE'

# ensure the existence of the following users on server side
# username1='$username1'
# username2='$username2'
# username3='$username3'
username1=$1
username2=$2
username3=$3  # changed by zhanghan 20181126
groupname1=$4
groupname2=$5
groupname3=$6
nfs_serv_ip=$7
nfs_serv_exp_path=$8
nfs_cli_mnt_path=$9   # add by zhanghan 20181127

# [START]: runing testcases
cd $nfs_cli_mnt_path
rm -rf d f
total=0
pass=0
fail=0

# DAC-STUC-NFSD-001
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-001
# ������Ŀ  : DAC-1.0-002-001
# ��������  : ͨ��NFS�ͻ��˴������ļ�ʱ�޳�ʼAdv ACL
# �������  : ���ļ���Ŀ¼�޿ɼ̳�ACEs
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´����ļ��ĸ�Ŀ¼�޿ɼ̳�ACEs��
#             3.�´����ļ�modeΪ644��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡ�ļ�f��Adv ACL��
# Ԥ�ڽ��  : ������ļ�f��modeת����Adv ACL���նˣ���������,
#             owner@:rwp--DaARWcCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��21��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full f")
result=$(echo $ret) # get pure string
expect='f: owner@:rwp--DaARWcCoS--::allow everyone@:r-----a-R-c--S--::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-001] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-001] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-002
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-002
# ������Ŀ  : DAC-1.0-002-001
# ��������  : ͨ��NFS�ͻ��˴�����Ŀ¼ʱ�޳�ʼAdv ACL
# �������  : ��Ŀ¼��Ŀ¼�޿ɼ̳�ACEs
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´���Ŀ¼�ĸ�Ŀ¼�޿ɼ̳�ACEs��
#             3.�´���Ŀ¼modeΪ755��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡĿ¼d��Adv ACL��
# Ԥ�ڽ��  : �����Ŀ¼d��modeת����Adv ACL���նˣ��������£�
#             owner@:rwpxdDaARWcCoS--::allow
#             everyone@:r--x--a-R-c--S--::allow
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��21��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full d")
result=$(echo $ret) # get pure string
expect='d: owner@:rwpxdDaARWcCoS--::allow everyone@:r--x--a-R-c--S--::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-002] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-002] ERROR!' >> $ELOG
    let fail+=1
fi
rmdir d

# DAC-STUC-NFSD-003
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-003
# ������Ŀ  : DAC-1.0-002-001
# ��������  : ͨ��NFS�ͻ��˴������ļ�ʱ�г�ʼAdv ACL
# �������  : �̳еĳ�ʼAdv ACL��Ȩ������δ�����������������Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´����ļ��ĸ�Ŀ¼�пɼ̳�ACEs��
#             3.�´����ļ�modeΪ644��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               �ɼ̳�ACE��"dac_setadvacl -s everyone@:r:fdi:allow d"��
#             3.��Ŀ¼d�ڴ������ļ�f��
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡ�ļ�f��Adv ACL��
# Ԥ�ڽ��  : �����Ŀ¼d�̳������ļ�f�ĳ�ʼAdv ACL���նˣ���������(��mode 444ת
#             ���õ�)��
#             owner@:r-----aAR-cCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��21��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:r:fdi:allow d"
touch d/f
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full d/f")
result=$(echo $ret) # get pure string
expect='d/f: owner@:r-----aAR-cCoS--::allow everyone@:r-----a-R-c--S--::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-003] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-003] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-004
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-004
# ������Ŀ  : DAC-1.0-002-001
# ��������  : ͨ��NFS�ͻ��˴������ļ�ʱ�г�ʼAdv ACL
# �������  : �̳еĳ�ʼAdv ACL��Ȩ�����볬���������������Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´����ļ��ĸ�Ŀ¼�пɼ̳�ACEs��
#             3.�´����ļ�modeΪ644��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               �ɼ̳�ACE��"dac_setadvacl -s everyone@:rwp:fdi:allow d"��
#             3.��Ŀ¼d�ڴ������ļ�f��
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡ�ļ�f��Adv ACL��
# Ԥ�ڽ��  : �����Ŀ¼d�̳������ļ�f�ĳ�ʼAdv ACL���նˣ���������(��mode 666ת
#             ���õ�)��
#             owner@:rwp--DaARWcCoS--::allow
#             everyone@:rwp--DaARWc--S--::allow
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��21��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:rwp:fdi:allow d"
touch d/f
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full d/f")
result=$(echo $ret) # get pure string
expect='d/f: owner@:rwp--DaARWcCoS--::allow everyone@:rwp--DaARWc--S--::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-004] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-004] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-005
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-005
# ������Ŀ  : DAC-1.0-002-001
# ��������  : ͨ��NFS�ͻ��˴�����Ŀ¼ʱ�г�ʼAdv ACL
# �������  : �̳еĳ�ʼAdv ACL��Ȩ������δ�����������������Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´���Ŀ¼�ĸ�Ŀ¼�пɼ̳�ACEs��
#             3.�´���Ŀ¼modeΪ755��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               �ɼ̳�ACE��"dac_setadvacl -s everyone@:r:fdi:allow d"��
#             3.��Ŀ¼d�ڴ�����Ŀ¼dd��
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡĿ¼dd��Adv ACL��
# Ԥ�ڽ��  : �����Ŀ¼d�̳�����Ŀ¼dd�ĳ�ʼAdv ACL���նˣ��������£�
#             owner@:r-----aAR-cCoS--::allow
#             group@:r-----a-R-c--S--::allow
#             everyone@:r-----a-R-c--S--::allow
#             owner@:r-----aAR-cCoS--:fdi:allow
#             group@:r-----a-R-c--S--:fdi:allow
#             everyone@:r-----a-R-c--S--:fdi:allow
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��21��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:r:fdi:allow d"
mkdir d/dd
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full d/dd")
result=$(echo $ret) # get pure string
expect='d/dd: owner@:r-----aAR-cCoS--::allow group@:r-----a-R-c--S--::allow everyone@:r-----a-R-c--S--::allow owner@:r-----aAR-cCoS--:fdi:allow group@:r-----a-R-c--S--:fdi:allow everyone@:r-----a-R-c--S--:fdi:allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-005] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-005] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-006
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-006
# ������Ŀ  : DAC-1.0-002-002
# ��������  : ͨ��NFS�ͻ��������ļ�ģʽ
# �������  :
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼��
#             2.�´����ļ�ģʽΪ644��
# ��    ��  : �ļ�Ҫ���õ���ģʽ
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:rwpxD::allow f"��
#             3.��NFS�ͻ���ͨ��chmod�����ļ�fģʽΪ400��
# Ԥ�ڽ��  : �ļ�fģʽ��Ϊ400
# ��������  : �ļ�f��Adv ACLȨ�������Ϊ��
#             owner:raARcCoS:mask
#             group:acS:mask
#             other:acS:mask
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#   �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:rwpxD::allow f"
chmod 400 f
result=$(ls -l f | awk '{print $1}')
expect='-r--------'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-006] mode check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-006] ERROR!' >> $ELOG
    let fail+=1
fi
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --raw f")
result=$(echo $ret) # get pure string
expect='f: flags:mw owner:r-----aAR-cCoS--::mask group:------a---c--S--::mask other:------a---c--S--::mask everyone@:rwpx-D----------::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-006] acl check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-006] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-009
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-009
# ������Ŀ  : DAC-1.0-002-005
# ��������  : ͨ��NFS�ͻ��������ļ�POSIX ACL
# �������  : NFSD��POSIX ACLת��Adv ACL��Ҫ���õ�Adv ACL�ܵȼ��Ƴ�һ��mode
# Ԥ������  : 1.NFSv3����ParaStor����Ŀ¼��
#             2.�´����ļ�ģʽΪ644��
# ��    ��  : �ļ�Ҫ���õ�POSIX ACL
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ������ļ�f��
#             2.��NFS�ͻ���ͨ��ϵͳ����setfacl���ļ�f���һ��POSIX ACE������
#               "setfacl -m u::rwx f"��
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡ�ļ�f��Adv ACL��
# Ԥ�ڽ��  : �ļ�f��Adv ACL������mode(744)ת���ó�������Ϊ��
#             owner@:rwpx-DaARWcCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# ��������  : �ļ�f��mode��Ϊ744
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
setfacl -m u::rwx f
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full f")
result=$(echo $ret) # get pure string
expect='f: owner@:rwpx-DaARWcCoS--::allow everyone@:r-----a-R-c--S--::allow'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-009] acl check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-009] ERROR!' >> $ELOG
    let fail+=1
fi
result=$(ls -l f | awk '{print $1}')
expect='-rwxr--r--'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-009] mode check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-009] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-010
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-010
# ������Ŀ  : DAC-1.0-002-005
# ��������  : ͨ��NFS�ͻ��������ļ�POSIX ACL
# �������  : NFSD��POSIX ACLת��Adv ACL��Ҫ���õ�Adv ACL���ܵȼ��Ƴ�һ��mode
# Ԥ������  : 1.NFSv3����ParaStor����Ŀ¼��
#             2.�´����ļ�ģʽΪ644��
# ��    ��  : �ļ�Ҫ���õ�POSIX ACL
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ������ļ�f��
#             2.��NFS�ͻ���ͨ��ϵͳ����setfacl���ļ�f���һ��POSIX ACE������
#               "setfacl -m u:wx:rw f"��
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_getadvacl��ȡ�ļ�f��Adv ACL��
# Ԥ�ڽ��  : �ļ�f��Adv ACL����Ϊ��
#             flags:0x20
#             owner@:rwp--DaARWcCoS--::allow
#             user:$username1:rwp--DaARWc--S--::allow
#             group@:r-----a-R-c--S--::allow
#             everyone@:r-----a-R-c--S--::allow
# ��������  : �ļ�f��mode��Ϊ664
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch ff
setfacl -m u:$username1:rw ff
ret=$(ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_getadvacl --full ff")
result=$(echo $ret) # get pure string
#the next sentence add by zhanghan***************
echo $result
result=`echo $result | cut -d : -f 2-`
#echo "after change the format of result"
#echo $result
#echo "delete all the space od result"
result=`echo $result | sed s/[[:space:]]//g`
#echo $result
#*******************
expect="owner@:rwp--DaARWcCoS--::allow user:$username1:rwp--DaARWc--S--::allow group@:r-----a-R-c--S--::allow everyone@:r-----a-R-c--S--::allow"
expect=`echo $expect | sed s/[[:space:]]//g`
#echo $expect
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-010] acl check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-010] ERROR!' >> $ELOG
    let fail+=1
fi
result=$(ls -l ff | awk '{print $1}')
expect='-rw-rw-r--+'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-010] mode check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-010] ERROR!' >> $ELOG
    let fail+=1
fi
#rm -f f

# DAC-STUC-NFSD-011
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-011
# ������Ŀ  : DAC-1.0-002-006
# ��������  : ͨ��NFS�ͻ��˻�ȡ�ļ�POSIX ACL
# �������  :
# Ԥ������  : 1.NFSv3����ParaStor����Ŀ¼��
#             2.�´����ļ�ģʽΪ644��
# ��    ��  :
# ִ�в���  : 1.��NFS�ͻ��˹��ص��ڴ������ļ�f��
#             2.��NFS�ͻ���ͨ��ϵͳ����getfacl��ȡ�ļ�f��POSIX ACL��
# Ԥ�ڽ��  : �ļ�f��POSIX ACL����Ϊ��
#             user::rw
#             group::r
#             other::r
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ret=$(getfacl f | grep -v '#')
result=$(echo $ret) # get pure string
expect='user::rw- group::r-- other::r--'
if [ "$result" == "$expect" ]; then
    echo "[DAC-STUC-NFSD-011] acl check pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-011] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-012
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-012
# ������Ŀ  : DAC-1.0-002-007
# ��������  : ����NFS�û���ȡ�ļ�����
# �������  : ���������ȡ�ļ����ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��д�벿�����ݣ�
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:r::allow f"��
#               ����NFS�û�$username2��ȡ�ļ�f�����ݣ�
#             4.���û�$username2����NFS��ͨ��cat�����ȡ�ļ�f���ݡ�
# Ԥ�ڽ��  : �û�$username2���Գɹ���ȡ�ļ�������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:r::allow f"
su $username2 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-012] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-012] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-013 (Ignore)
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:x::allow f"
su $username2 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-013] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-013] ACCESS deny READ! Ignore this case.' >> $LOG
fi
rm -f f

# DAC-STUC-NFSD-014
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-014
# ������Ŀ  : DAC-1.0-002-007
# ��������  : �ܾ�NFS�û���ȡ�ļ�����
# �������  : ���þܾ���ȡ�ļ����ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��д�벿�����ݣ�
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:r::deny f"��
#               �ܾ�NFS�û�$username2��ȡ�ļ�f�����ݣ�
#             3.���û�$username2����NFS��ͨ��cat�����ȡ�ļ�f���ݡ�
# Ԥ�ڽ��  : �û�$username2�޷���ȡ�ļ�������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:r::deny f"
su $username2 -c 'cat f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-014] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-014] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-015
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-015
# ������Ŀ  : DAC-1.0-002-007
# ��������  : �ܾ�NFS�û���ȡ�ļ�����
# �������  : δ��������/�ܾ���ȡ�ļ����ݵ�Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��д�벿�����ݣ�
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#             3.���û�$username2����NFS��ͨ��cat�����ȡ�ļ�f���ݡ�
# Ԥ�ڽ��  : �û�$username2�޷���ȡ�ļ�������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
su $username2 -c 'cat f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-015] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-015] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-016
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-016
# ������Ŀ  : DAC-1.0-002-008
# ��������  : ����NFS�û��޸��ļ�����
# �������  : ���������޸��ļ����ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#            3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:w::allow f"��
#               ����NFS�û�$username2�޸��ļ�f�����ݣ�
#             4.���û�$username2����NFS��ͨ��echo���ļ�fд�����ݣ�"echo wx > f"��
# Ԥ�ڽ��  : �û�$username2���Գɹ�д�����ݵ��ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#   ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:w::allow f"
su $username2 -c 'echo sugon > f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-016] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-016] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-017
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-017
# ������Ŀ  : DAC-1.0-002-008
# ��������  : �ܾ�NFS�û��޸��ļ�����
# �������  : ���þܾ��޸��ļ����ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:w::deny f"��
#               �ܾ�NFS�û�$username2�޸��ļ�f�����ݣ�
#             3.���û�$username2����NFS��ͨ��echo���ļ�fд�����ݣ�"echo wx > f"��
# Ԥ�ڽ��  : �û�$username2�޷�д�����ݵ��ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:w::deny f"
su $username2 -c 'echo sugon > f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-017] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-017] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-018
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-018
# ������Ŀ  : DAC-1.0-002-008
# ��������  : �ܾ�NFS�û��޸��ļ�����
# �������  : δ��������/�ܾ��޸��ļ����ݵ�Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#             3.���û�$username2����NFS��ͨ��echo���ļ�fд�����ݣ�"echo wx > f"��
# Ԥ�ڽ��  : �û�$username2�޷�д�����ݵ��ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
su $username2 -c 'echo sugon > f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-018] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-018] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-022
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-022
# ������Ŀ  : DAC-1.0-002-010
# ��������  : ����NFS�û�ִ���ļ�
# �������  : ��������ִ���ļ���Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#              ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#              ACE��"dac_setadvacl -m USER:$username2:rx::allow f"��
#              ����NFS�û�$username2ִ���ļ�f��
#            4.���û�$username2����NFS��ִ���ļ�f��"./f"��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ִ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:rx::allow f"
su $username2 -c './f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-022] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-022] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-023
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-023
# ������Ŀ  : DAC-1.0-002-010
# ��������  : �ܾ�NFS�û�ִ���ļ�
# �������  : ���þܾ�ִ���ļ���Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:x::deny f"��
#               �ܾ�NFS�û�$username2ִ���ļ���
#             3.���û�$username2����NFS��ִ���ļ�f��"./f"��
# Ԥ�ڽ��  : �û�$username2�޷�ִ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:x::deny f"
su $username2 -c './f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-023] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-023] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-024
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-024
# ������Ŀ  : DAC-1.0-002-010
# ��������  : �ܾ�NFS�û�ִ���ļ�
# �������  : δ��������/�ܾ�ִ���ļ���Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow f"����������˵�Ȩ�ޣ�
#             3.���û�$username2����NFS��ִ���ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷�ִ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
touch f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow f"
su $username2 -c './f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-024] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-024] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-031
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-031
# ������Ŀ  : DAC-1.0-002-013
# ��������  : ����NFS�û�ɾ���ļ�
# �������  : �����ļ�����ɾ����Ȩ�ޣ���Ŀ¼�ܾ�ɾ�����ļ���Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼d��Ȩ�ޣ�
#            3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::deny d"��
#               �ܾ�NFS�û�$username2ɾ��Ŀ¼d�����ļ���
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::allow f"��
#               ����NFS�û�$username2ɾ���ļ�f��
#             5.���û�$username2����NFS������Ŀ¼d��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::deny d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::allow d/f"
su $username2 -c 'cd d; rm -f f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-031] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-031] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-032
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-032
# ������Ŀ  : DAC-1.0-002-013
# ��������  : ����NFS�û�ɾ���ļ�
# �������  : �����ļ��ܾ�ɾ����Ȩ�ޣ���Ŀ¼����ɾ�����ļ���Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼d��Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::allow d"��
#               ����NFS�û�$username2ɾ��Ŀ¼d�����ļ���
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::deny f"��
#               �ܾ�NFS�û�$username2ɾ���ļ�f��
#             5.���û�$username2����NFS������Ŀ¼d��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::deny d/f"
su $username2 -c 'cd d; rm -f f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-032] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-032] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-033
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-033
# ������Ŀ  : DAC-1.0-002-013
# ��������  : ����NFS�û�ɾ���ļ�
# �������  : 1.�����ļ��ĸ�Ŀ¼��ճסλS_ISVTX��
#             2.NFS�û�$username2���ļ��ĸ�Ŀ¼��дȨ�ޣ����Ǹ�Ŀ¼�������ߡ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼d��Ȩ�ޣ�
#             3.ͨ��chmod����Ŀ¼d��ճסλ��"chmod o+t d"��
#             4.ͨ��chmod���������˶�Ŀ¼d��дȨ�ޣ�"chmod a+w d"��
#             5.ͨ��chown����Ŀ¼d��������Ϊ$username2��"chown $username2 d"��
#             6.���û�$username2����NFS������Ŀ¼d��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
chmod o+t d
chmod a+w d
chown $username2 d
su $username2 -c 'cd d; rm -f f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-033] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-033] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-034
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-034
# ������Ŀ  : DAC-1.0-002-013
# ��������  : ����NFS�û�ɾ���ļ�
# �������  : 1.δ�����ļ�����/�ܾ�ɾ����Ȩ�޺͸�Ŀ¼����/�ܾ�ɾ�����ļ���Ȩ�ޣ�
#             2.���ø�Ŀ¼��������ļ���Ȩ�ޡ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#              �����˽��������Ŀ¼d��Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:w::allow d"��
#               ����NFS�û�$username2��Ŀ¼d����ļ���
#             4.���û�$username2����NFS������Ŀ¼d��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:w::allow d"
su $username2 -c 'cd d; rm -f f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-034] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-034] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-035
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-035
# ������Ŀ  : DAC-1.0-002-013
# ��������  : �ܾ�NFS�û�ɾ���ļ�
# �������  : �����ļ��ܾ�ɾ����Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl���ļ�f���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::deny f"��
#               �ܾ�NFS�û�$username2ɾ���ļ�f��
#             3.���û�$username2����NFS��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::deny d/f"
su $username2 -c 'cd d; rm -f f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-035] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-035] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-036
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-036
# ������Ŀ  : DAC-1.0-002-013
# ��������  : �ܾ�NFS�û�ɾ���ļ�
# �������  : δ�����ļ�����/�ܾ�ɾ����Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.���û�$username2����NFS��ͨ������rmɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷�ɾ���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��23��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
su $username2 -c 'cd d; rm -f f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-036] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-036] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-049
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-049
# ������Ŀ  : DAC-1.0-002-017
# ��������  : ����NFS�û��г�Ŀ¼����
# �������  : ���������г�Ŀ¼���ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����d�ڴ��������ļ���
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow d"����������˵�Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:r::allow d"��
#               ����NFS�û�$username2�г�Ŀ¼d�����ݣ�
#             4.���û�$username2����NFS��ͨ��ls�г�Ŀ¼d���ݣ�"ls d"��
# Ԥ�ڽ��  : �û�$username2���Գɹ��г�Ŀ¼������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f1 d/f2
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:r::allow d"
su $username2 -c 'ls d'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-049] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-049] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-050
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-050
# ������Ŀ  : DAC-1.0-002-017
# ��������  : �ܾ�NFS�û��г�Ŀ¼����
# �������  : ���þܾ��г�Ŀ¼���ݵ�Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����d�ڴ��������ļ���
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:r::deny d"��
#               �ܾ�NFS�û�$username2�г�Ŀ¼d�����ݣ�
#             3.���û�$username2����NFS��ͨ��ls�г�Ŀ¼d���ݣ�"ls d"��
# Ԥ�ڽ��  : �û�$username2�޷��г�Ŀ¼������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f1 d/f2
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:r::deny d"
su $username2 -c 'ls d'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-050] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-050] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-051
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-051
# ������Ŀ  : DAC-1.0-002-017
# ��������  : �ܾ�NFS�û��г�Ŀ¼����
# �������  : δ��������/�ܾ��г�Ŀ¼���ݵ�Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����d�ڴ��������ļ���
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow d"����������˵�Ȩ�ޣ�
#             3.���û�$username2����NFS��ͨ��ls�г�Ŀ¼d���ݣ�"ls d"��
# Ԥ�ڽ��  : �û�$username2�޷��г�Ŀ¼������
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f1 d/f2
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow d"
su $username2 -c 'ls d'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-051] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-051] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-052
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-052
# ������Ŀ  : DAC-1.0-002-018
# ��������  : ����NFS�û���Ŀ¼������ļ�
# �������  : ����������Ŀ¼������ļ���Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:w::allow d"��
#               ����NFS�û�$username2��Ŀ¼d������ļ���
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��touch����ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ���Ŀ¼������ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:w::allow d"
su $username2 -c 'cd d; touch f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-052] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-052] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-053
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-053
# ������Ŀ  : DAC-1.0-002-018
# ��������  : �ܾ�NFS�û���Ŀ¼������ļ�
# �������  : ���þܾ���Ŀ¼������ļ���Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:w::deny d"��
#               �ܾ�NFS�û�$username2��Ŀ¼d������ļ���
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��touch����ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷���Ŀ¼������ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:w::deny d"
su $username2 -c 'cd d; touch f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-053] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-053] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-054
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-054
# ������Ŀ  : DAC-1.0-002-018
# ��������  : �ܾ�NFS�û���Ŀ¼������ļ�
# �������  : δ��������/�ܾ���Ŀ¼������ļ���Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.���û�$username2����NFS������Ŀ¼d��ͨ��touch����ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷���Ŀ¼������ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
su $username2 -c 'cd d; touch f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-054] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-054] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-055
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-055
# ������Ŀ  : DAC-1.0-002-019
# ��������  : ����NFS�û���Ŀ¼�������Ŀ¼
# �������  : ����������Ŀ¼�������Ŀ¼��Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:p::allow d"��
#               ����NFS�û�$username2��Ŀ¼d�������Ŀ¼��
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��mkdir�����Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2���Գɹ���Ŀ¼�������Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:p::allow d"
su $username2 -c 'cd d; mkdir dd'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-055] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-055] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-056
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-056
# ������Ŀ  : DAC-1.0-002-019
# ��������  : �ܾ�NFS�û���Ŀ¼�������Ŀ¼
# �������  : ���þܾ���Ŀ¼�������Ŀ¼��Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:p::deny d"��
#               �ܾ�NFS�û�$username2��Ŀ¼d�������Ŀ¼��
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��mkdir�����Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2�޷���Ŀ¼�������Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:p::deny d"
su $username2 -c 'cd d; mkdir dd'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-056] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-056] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-057
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-057
# ������Ŀ  : DAC-1.0-002-019
# ��������  : �ܾ�NFS�û���Ŀ¼�������Ŀ¼
# �������  : δ��������/�ܾ���Ŀ¼�������Ŀ¼��Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.���û�$username2����NFS������Ŀ¼d��ͨ��mkdir�����Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2�޷���Ŀ¼�������Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
su $username2 -c 'cd d; mkdir dd'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-057] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-057] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-058
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-058
# ������Ŀ  : DAC-1.0-002-020
# ��������  : ����NFS�û�����/����Ŀ¼
# �������  : �����������/����Ŀ¼��Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow d"����������˵�Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:x::allow d"��
#               ����NFS�û�$username2����/����Ŀ¼d��
#             4.���û�$username2����NFS��ͨ��cd����Ŀ¼d��
# Ԥ�ڽ��  : �û�$username2���Գɹ�����Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:x::allow d"
su $username2 -c 'cd d'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-058] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-058] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-059
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-059
# ������Ŀ  : DAC-1.0-002-020
# ��������  : �ܾ�NFS�û�����/����Ŀ¼
# �������  : ���þܾ�����/����Ŀ¼��Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:x::deny d"��
#               �ܾ�NFS�û�$username2����/����Ŀ¼d��
#             3.���û�$username2����NFS��ͨ��cd����Ŀ¼d��
# Ԥ�ڽ��  : �û�$username2�޷�����Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:x::deny d"
su $username2 -c 'cd d'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-059] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-059] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-060
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-060
# ������Ŀ  : DAC-1.0-002-020
# ��������  : �ܾ�NFS�û�����/����Ŀ¼
# �������  : δ��������/�ܾ�����/����Ŀ¼��Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:::allow d"����������˵�Ȩ�ޣ�
#             3.���û�$username2����NFS��ͨ��cd����Ŀ¼d��
# Ԥ�ڽ��  : �û�$username2�޷�����Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:::allow d"
su $username2 -c 'cd d'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-060] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-060] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-061
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-061
# ������Ŀ  : DAC-1.0-002-021
# ��������  : ����NFS�û�ɾ��Ŀ¼���ļ�
# �������  : ��������ɾ��Ŀ¼���ļ���Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::allow d"��
#               ����NFS�û�$username2ɾ��Ŀ¼d�����ļ�/��Ŀ¼��
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��rm����ɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ��Ŀ¼���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::allow d"
su $username2 -c 'cd d; rm -f f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-061] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-061] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-062
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-062
# ������Ŀ  : DAC-1.0-002-021
# ��������  : �ܾ�NFS�û�ɾ��Ŀ¼���ļ�
# �������  : ���þܾ�ɾ��Ŀ¼���ļ���Ȩ��
# Ԥ������  : 1.NFSv3/NFSv4����ParaStor����Ŀ¼
#             2.�´���Ŀ¼��ʼģʽ755
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����d�ڴ������ļ�f��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::deny d"��
#               �ܾ�NFS�û�$username2ɾ��Ŀ¼d�����ļ�/��Ŀ¼��
#             3.���û�$username2����NFS������Ŀ¼d��ͨ��rm����ɾ���ļ�f��
# Ԥ�ڽ��  : �û�$username2�޷�ɾ��Ŀ¼���ļ�
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
touch d/f
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::deny d"
su $username2 -c 'cd d; rm -f f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-062] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-062] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-069
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-069
# ������Ŀ  : DAC-1.0-002-024
# ��������  : ����NFS�û�ɾ��Ŀ¼
# �������  : ����Ŀ¼����ɾ����Ȩ�ޣ���Ŀ¼�ܾ�ɾ����Ŀ¼��Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ�����Ŀ¼dd��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼d��Ȩ�ޣ�
#            3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::deny d"��
#               �ܾ�NFS�û�$username2ɾ��Ŀ¼d����Ŀ¼��
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼dd���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::allow dd"��
#               ����NFS�û�$username2ɾ��Ŀ¼dd��
#             5.���û�$username2����NFS������Ŀ¼d��ͨ������rmdirɾ��Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ��Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
mkdir d/dd
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::deny d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::allow d/dd"
su $username2 -c 'cd d; rmdir dd'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-069] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-069] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-070
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-070
# ������Ŀ  : DAC-1.0-002-024
# ��������  : ����NFS�û�ɾ��Ŀ¼
# �������  : ����Ŀ¼�ܾ�ɾ����Ȩ�ޣ���Ŀ¼����ɾ����Ŀ¼��Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ�����Ŀ¼dd��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼��Ȩ�ޣ�
#             3.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:d::allow d"��
#               ����NFS�û�$username2ɾ��Ŀ¼d����Ŀ¼��
#             4.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼dd���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::deny dd"��
#               �ܾ�NFS�û�$username2ɾ��Ŀ¼dd��
#             5.���û�$username2����NFS������Ŀ¼d��ͨ������rmdirɾ��Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ��Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
mkdir d/dd
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:d::allow d"
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::deny d/dd"
su $username2 -c 'cd d; rmdir dd'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-070] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-070] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-071
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-071
# ������Ŀ  : DAC-1.0-002-024
# ��������  : ����NFS�û�ɾ��Ŀ¼
# �������  : 1.����Ŀ¼�ĸ�Ŀ¼��ճסλS_ISVTX��
#             2.NFS�û�$username2��Ŀ¼�ĸ�Ŀ¼��дȨ�ޣ����Ǹ�Ŀ¼�������ߡ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص��ڴ�����Ŀ¼d����Ŀ¼d�ڴ�����Ŀ¼dd��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -s everyone@:x::allow d"��
#               �����˽��������Ŀ¼��Ȩ�ޣ�
#             3.ͨ��chmod����Ŀ¼d��ճסλ��"chmod o+t d"��
#             4.ͨ��chmod���������˶�Ŀ¼d��дȨ�ޣ�"chmod a+w d"��
#             5.ͨ��chown����Ŀ¼d��������Ϊ$username2��"chown $username2 d"��
#             6.���û�$username2����NFS������Ŀ¼d��ͨ������rmdirɾ��Ŀ¼dd��
# Ԥ�ڽ��  : �û�$username2���Գɹ�ɾ��Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
mkdir d/dd
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:x::allow d"
chmod o+t d
chmod a+w d
chown $username2 d
su $username2 -c 'cd d; rmdir dd'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-071] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-071] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-072
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-072
# ������Ŀ  : DAC-1.0-002-024
# ��������  : �ܾ�NFS�û�ɾ��Ŀ¼
# �������  : ����Ŀ¼�ܾ�ɾ����Ȩ��
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴����Ŀ¼d��
#             2.��NAS�ڵ�˽�пͻ���ͨ��ʵ�ù���dac_setadvacl��Ŀ¼d���һ��
#               ACE��"dac_setadvacl -m USER:$username2:D::deny d"��
#               �ܾ�NFS�û�$username2ɾ��Ŀ¼d��
#             3.���û�$username2����NFS��ͨ������rmdirɾ��Ŀ¼d��
# Ԥ�ڽ��  : �û�$username2�޷�ɾ��Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
mkdir d/dd
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -m U:$username2:D::deny d"
su $username2 -c 'cd d; rmdir dd'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-072] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-072] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-073
#/*****************************************************************************
# �������  : DAC-STUC-NFSD-073
# ������Ŀ  : DAC-1.0-002-024
# ��������  : �ܾ�NFS�û�ɾ��Ŀ¼
# �������  : δ����Ŀ¼����/�ܾ�ɾ����Ȩ�ޣ�ȱʡ�ܾ�
# Ԥ������  : NFSv3/NFSv4����ParaStor����Ŀ¼
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴����Ŀ¼d��
#             2.���û�$username2����NFS��ͨ������rmdirɾ��Ŀ¼d��
# Ԥ�ڽ��  : �û�$username2�޷�ɾ��Ŀ¼
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��24��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
#
#*****************************************************************************/
mkdir d
mkdir d/dd
su $username2 -c 'rmdir d/dd'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-073] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-073] ERROR!' >> $ELOG
    let fail+=1
fi
rm -rf d

# DAC-STUC-NFSD-EXT-001
# �������  : DAC-STUC-NFSD-EXT-001
# ������Ŀ  :
# ��������  : �����������������Ȩ��
# �������  : �ܾ������߶�����Ȩ�ޣ���ȡʧ��
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ owner@:r::deny��
#             3.���û�$username1��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username1�޷���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s owner@:r::deny f"
su $username1 -c 'cat f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-001] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-001] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-002
# �������  : DAC-STUC-NFSD-EXT-002
# ������Ŀ  :
# ��������  : �����������������Ȩ��
# �������  : ���������߶�����Ȩ�ޣ���ȡ�ɹ�
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ owner@:r::allow��
#             3.���û�$username1��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username1�ɹ���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s owner@:r::allow f"
su $username1 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-002] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-002] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-003
# �������  : DAC-STUC-NFSD-EXT-003
# ������Ŀ  :
# ��������  : �����������������Ȩ��
# �������  : �ܾ������������Ȩ�ޣ���ȡʧ��
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ group@:r::deny��
#             3.���û�$username1��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username1�޷���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s group@:r::deny f"
su $username1 -c 'cat f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-003] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-003] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-004
# �������  : DAC-STUC-NFSD-EXT-004
# ������Ŀ  :
# ��������  : �����������������Ȩ��
# �������  : ���������������Ȩ�ޣ���ȡ�ɹ�
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ group@:r::allow��
#             3.���û�$username1��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username1�ɹ���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s group@:r::allow f"
su $username1 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-004] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-004] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-005
# �������  : DAC-STUC-NFSD-EXT-005
# ������Ŀ  :
# ��������  : �����������EveryoneȨ��
# �������  : �ܾ�Everyone������Ȩ�ޣ���ȡʧ��
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ everyone@:r::deny��
#             3.���û�$username2��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username2�޷���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:r::deny f"
su $username2 -c 'cat f'
if [ $? != 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-005] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-005] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-006
# �������  : DAC-STUC-NFSD-EXT-006
# ������Ŀ  :
# ��������  : �����������EveryoneȨ��
# �������  : ����Everyone������Ȩ�ޣ���ȡ�ɹ�
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ everyone@:r::allow��
#             3.���û�$username2��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username2�ɹ���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s everyone@:r::allow f"
su $username2 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-006] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-006] ERROR!' >> $ELOG
    let fail+=1
fi
rm -f f

# DAC-STUC-NFSD-EXT-007
# �������  : DAC-STUC-NFSD-EXT-007
# ������Ŀ  :
# ��������  : �û����ڶ���û���
# �������  : �û�$username1Ϊ�����ߣ��û�$username2������$username2��$username3
# Ԥ������  :
# ��    ��  :
# ִ�в���  : 1.���û�$username1����NFS���ڹ��ص㴴�����ļ�f��
#             2.��˽�пͻ�������f��Adv ACLΪ G:$username2:r::allow,G:$username3:w::allow,everyone@:rw::deny��
#             3.���û�$username2��NFS�ͻ���ִ��cat f��
# Ԥ�ڽ��  : �û�$username1�ɹ���ȡ�ļ�����
# ��������  :
#
# �޸���ʷ  :
#  1.��    ��   : 2016��9��1��
#    ��    ��   : ���� <wangxiaob@sugon.com>
#    �޸�����   : �������
su $username1 -c 'touch f'
ssh $nfs_serv_ip "usermod -a -G $groupname3 $username2" # $username2 belongs to groups $username2,$username3
ssh $nfs_serv_ip "cd $nfs_serv_exp_path; dac_setadvacl -s G:$groupname2:r::allow,G:$groupname3:w::allow,everyone@:rw::deny f"
su $username2 -c 'cat f'
if [ $? == 0 ]; then
    echo "[DAC-STUC-NFSD-EXT-007] pass." >> $LOG
    let pass+=1
else
    echo '[DAC-STUC-NFSD-EXT-007] ERROR!' >> $ELOG
    let fail+=1
fi
ssh $nfs_serv_ip "usermod -g $groupname2 $username2"
rm -f f

# [END]: all testcases successfully
let total=$pass+$fail
echo "All test cases done! [Total check: $total Pass: $pass Fail: $fail]" >> $LOG
