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
# 用例编号  : DAC-STUC-NFSD-001
# 测试项目  : DAC-1.0-002-001
# 用例标题  : 通过NFS客户端创建新文件时无初始Adv ACL
# 用例简介  : 新文件父目录无可继承ACEs
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建文件的父目录无可继承ACEs；
#             3.新创建文件mode为644。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_getadvacl获取文件f的Adv ACL。
# 预期结果  : 输出由文件f的mode转化的Adv ACL到终端，内容如下,
#             owner@:rwp--DaARWcCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月21日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-002
# 测试项目  : DAC-1.0-002-001
# 用例标题  : 通过NFS客户端创建新目录时无初始Adv ACL
# 用例简介  : 新目录父目录无可继承ACEs
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建目录的父目录无可继承ACEs；
#             3.新创建目录mode为755。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_getadvacl获取目录d的Adv ACL。
# 预期结果  : 输出由目录d的mode转化的Adv ACL到终端，内容如下，
#             owner@:rwpxdDaARWcCoS--::allow
#             everyone@:r--x--a-R-c--S--::allow
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月21日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-003
# 测试项目  : DAC-1.0-002-001
# 用例标题  : 通过NFS客户端创建新文件时有初始Adv ACL
# 用例简介  : 继承的初始Adv ACL的权限掩码未超出创建掩码允许的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建文件的父目录有可继承ACEs；
#             3.新创建文件mode为644。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               可继承ACE，"dac_setadvacl -s everyone@:r:fdi:allow d"；
#             3.在目录d内创建新文件f；
#             4.在NAS节点私有客户端通过实用工具dac_getadvacl获取文件f的Adv ACL。
# 预期结果  : 输出由目录d继承来的文件f的初始Adv ACL到终端，内容如下(由mode 444转
#             换得到)，
#             owner@:r-----aAR-cCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月21日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-004
# 测试项目  : DAC-1.0-002-001
# 用例标题  : 通过NFS客户端创建新文件时有初始Adv ACL
# 用例简介  : 继承的初始Adv ACL的权限掩码超出创建掩码允许的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建文件的父目录有可继承ACEs；
#             3.新创建文件mode为644。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               可继承ACE，"dac_setadvacl -s everyone@:rwp:fdi:allow d"；
#             3.在目录d内创建新文件f；
#             4.在NAS节点私有客户端通过实用工具dac_getadvacl获取文件f的Adv ACL。
# 预期结果  : 输出由目录d继承来的文件f的初始Adv ACL到终端，内容如下(由mode 666转
#             换得到)，
#             owner@:rwp--DaARWcCoS--::allow
#             everyone@:rwp--DaARWc--S--::allow
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月21日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-005
# 测试项目  : DAC-1.0-002-001
# 用例标题  : 通过NFS客户端创建新目录时有初始Adv ACL
# 用例简介  : 继承的初始Adv ACL的权限掩码未超出创建掩码允许的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建目录的父目录有可继承ACEs；
#             3.新创建目录mode为755。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               可继承ACE，"dac_setadvacl -s everyone@:r:fdi:allow d"；
#             3.在目录d内创建空目录dd；
#             4.在NAS节点私有客户端通过实用工具dac_getadvacl获取目录dd的Adv ACL。
# 预期结果  : 输出由目录d继承来的目录dd的初始Adv ACL到终端，内容如下，
#             owner@:r-----aAR-cCoS--::allow
#             group@:r-----a-R-c--S--::allow
#             everyone@:r-----a-R-c--S--::allow
#             owner@:r-----aAR-cCoS--:fdi:allow
#             group@:r-----a-R-c--S--:fdi:allow
#             everyone@:r-----a-R-c--S--:fdi:allow
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月21日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-006
# 测试项目  : DAC-1.0-002-002
# 用例标题  : 通过NFS客户端设置文件模式
# 用例简介  :
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录；
#             2.新创建文件模式为644。
# 输    入  : 文件要设置的新模式
# 执行步骤  : 1.在NFS客户端挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:rwpxD::allow f"；
#             3.在NFS客户端通过chmod设置文件f模式为400。
# 预期结果  : 文件f模式变为400
# 后置条件  : 文件f的Adv ACL权限掩码变为，
#             owner:raARcCoS:mask
#             group:acS:mask
#             other:acS:mask
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#   修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-009
# 测试项目  : DAC-1.0-002-005
# 用例标题  : 通过NFS客户端设置文件POSIX ACL
# 用例简介  : NFSD将POSIX ACL转成Adv ACL，要设置的Adv ACL能等价推出一套mode
# 预置条件  : 1.NFSv3挂载ParaStor导出目录；
#             2.新创建文件模式为644。
# 输    入  : 文件要设置的POSIX ACL
# 执行步骤  : 1.在NFS客户端挂载点内创建新文件f；
#             2.在NFS客户端通过系统工具setfacl向文件f添加一条POSIX ACE，例如
#               "setfacl -m u::rwx f"；
#             3.在NAS节点私有客户端通过实用工具dac_getadvacl获取文件f的Adv ACL。
# 预期结果  : 文件f的Adv ACL是由其mode(744)转化得出，内容为，
#             owner@:rwpx-DaARWcCoS--::allow
#             everyone@:r-----a-R-c--S--::allow
# 后置条件  : 文件f的mode变为744
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-010
# 测试项目  : DAC-1.0-002-005
# 用例标题  : 通过NFS客户端设置文件POSIX ACL
# 用例简介  : NFSD将POSIX ACL转成Adv ACL，要设置的Adv ACL不能等价推出一套mode
# 预置条件  : 1.NFSv3挂载ParaStor导出目录；
#             2.新创建文件模式为644。
# 输    入  : 文件要设置的POSIX ACL
# 执行步骤  : 1.在NFS客户端挂载点内创建新文件f；
#             2.在NFS客户端通过系统工具setfacl向文件f添加一条POSIX ACE，例如
#               "setfacl -m u:wx:rw f"；
#             3.在NAS节点私有客户端通过实用工具dac_getadvacl获取文件f的Adv ACL。
# 预期结果  : 文件f的Adv ACL内容为，
#             flags:0x20
#             owner@:rwp--DaARWcCoS--::allow
#             user:$username1:rwp--DaARWc--S--::allow
#             group@:r-----a-R-c--S--::allow
#             everyone@:r-----a-R-c--S--::allow
# 后置条件  : 文件f的mode变为664
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-011
# 测试项目  : DAC-1.0-002-006
# 用例标题  : 通过NFS客户端获取文件POSIX ACL
# 用例简介  :
# 预置条件  : 1.NFSv3挂载ParaStor导出目录；
#             2.新创建文件模式为644。
# 输    入  :
# 执行步骤  : 1.在NFS客户端挂载点内创建新文件f；
#             2.在NFS客户端通过系统工具getfacl获取文件f的POSIX ACL。
# 预期结果  : 文件f的POSIX ACL内容为，
#             user::rw
#             group::r
#             other::r
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-012
# 测试项目  : DAC-1.0-002-007
# 用例标题  : 允许NFS用户读取文件数据
# 用例简介  : 设置允许读取文件数据的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f，写入部分数据；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:r::allow f"，
#               允许NFS用户$username2读取文件f的数据；
#             4.以用户$username2挂载NFS，通过cat命令获取文件f内容。
# 预期结果  : 用户$username2可以成功获取文件的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-014
# 测试项目  : DAC-1.0-002-007
# 用例标题  : 拒绝NFS用户读取文件数据
# 用例简介  : 设置拒绝读取文件数据的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f，写入部分数据；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:r::deny f"，
#               拒绝NFS用户$username2读取文件f的数据；
#             3.以用户$username2挂载NFS，通过cat命令获取文件f内容。
# 预期结果  : 用户$username2无法获取文件的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-015
# 测试项目  : DAC-1.0-002-007
# 用例标题  : 拒绝NFS用户读取文件数据
# 用例简介  : 未设置允许/拒绝读取文件数据的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f，写入部分数据；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#             3.以用户$username2挂载NFS，通过cat命令获取文件f内容。
# 预期结果  : 用户$username2无法获取文件的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-016
# 测试项目  : DAC-1.0-002-008
# 用例标题  : 允许NFS用户修改文件数据
# 用例简介  : 设置允许修改文件数据的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#            3.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:w::allow f"，
#               允许NFS用户$username2修改文件f的数据；
#             4.以用户$username2挂载NFS，通过echo向文件f写入数据，"echo wx > f"。
# 预期结果  : 用户$username2可以成功写入数据到文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#   作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-017
# 测试项目  : DAC-1.0-002-008
# 用例标题  : 拒绝NFS用户修改文件数据
# 用例简介  : 设置拒绝修改文件数据的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:w::deny f"，
#               拒绝NFS用户$username2修改文件f的数据；
#             3.以用户$username2挂载NFS，通过echo向文件f写入数据，"echo wx > f"。
# 预期结果  : 用户$username2无法写入数据到文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-018
# 测试项目  : DAC-1.0-002-008
# 用例标题  : 拒绝NFS用户修改文件数据
# 用例简介  : 未设置允许/拒绝修改文件数据的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#             3.以用户$username2挂载NFS，通过echo向文件f写入数据，"echo wx > f"。
# 预期结果  : 用户$username2无法写入数据到文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-022
# 测试项目  : DAC-1.0-002-010
# 用例标题  : 允许NFS用户执行文件
# 用例简介  : 设置允许执行文件的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#              ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#              ACE，"dac_setadvacl -m USER:$username2:rx::allow f"，
#              允许NFS用户$username2执行文件f；
#            4.以用户$username2挂载NFS，执行文件f，"./f"。
# 预期结果  : 用户$username2可以成功执行文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-023
# 测试项目  : DAC-1.0-002-010
# 用例标题  : 拒绝NFS用户执行文件
# 用例简介  : 设置拒绝执行文件的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:x::deny f"，
#               拒绝NFS用户$username2执行文件；
#             3.以用户$username2挂载NFS，执行文件f，"./f"。
# 预期结果  : 用户$username2无法执行文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-024
# 测试项目  : DAC-1.0-002-010
# 用例标题  : 拒绝NFS用户执行文件
# 用例简介  : 未设置允许/拒绝执行文件的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow f"，清除所有人的权限；
#             3.以用户$username2挂载NFS，执行文件f。
# 预期结果  : 用户$username2无法执行文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-031
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 允许NFS用户删除文件
# 用例简介  : 设置文件允许删除的权限，父目录拒绝删除子文件的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录d的权限；
#            3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::deny d"，
#               拒绝NFS用户$username2删除目录d的子文件；
#             4.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::allow f"，
#               允许NFS用户$username2删除文件f；
#             5.以用户$username2挂载NFS，进入目录d，通过命令rm删除文件f。
# 预期结果  : 用户$username2可以成功删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-032
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 允许NFS用户删除文件
# 用例简介  : 设置文件拒绝删除的权限，父目录允许删除子文件的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录d的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::allow d"，
#               允许NFS用户$username2删除目录d的子文件；
#             4.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::deny f"，
#               拒绝NFS用户$username2删除文件f；
#             5.以用户$username2挂载NFS，进入目录d，通过命令rm删除文件f。
# 预期结果  : 用户$username2可以成功删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-033
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 允许NFS用户删除文件
# 用例简介  : 1.设置文件的父目录的粘住位S_ISVTX；
#             2.NFS用户$username2对文件的父目录有写权限，且是父目录的所有者。
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录d的权限；
#             3.通过chmod设置目录d的粘住位，"chmod o+t d"；
#             4.通过chmod设置所有人对目录d有写权限，"chmod a+w d"；
#             5.通过chown设置目录d的所有者为$username2，"chown $username2 d"；
#             6.以用户$username2挂载NFS，进入目录d，通过命令rm删除文件f。
# 预期结果  : 用户$username2可以成功删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-034
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 允许NFS用户删除文件
# 用例简介  : 1.未设置文件允许/拒绝删除的权限和父目录允许/拒绝删除子文件的权限；
#             2.设置父目录允许添加文件的权限。
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#              所有人仅允许进入目录d的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:w::allow d"，
#               允许NFS用户$username2向目录d添加文件；
#             4.以用户$username2挂载NFS，进入目录d，通过命令rm删除文件f。
# 预期结果  : 用户$username2可以成功删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-035
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 拒绝NFS用户删除文件
# 用例简介  : 设置文件拒绝删除的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向文件f添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::deny f"，
#               拒绝NFS用户$username2删除文件f；
#             3.以用户$username2挂载NFS，通过命令rm删除文件f。
# 预期结果  : 用户$username2无法删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-036
# 测试项目  : DAC-1.0-002-013
# 用例标题  : 拒绝NFS用户删除文件
# 用例简介  : 未设置文件允许/拒绝删除的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.以用户$username2挂载NFS，通过命令rm删除文件f。
# 预期结果  : 用户$username2无法删除文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-049
# 测试项目  : DAC-1.0-002-017
# 用例标题  : 允许NFS用户列出目录内容
# 用例简介  : 设置允许列出目录内容的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在d内创建若干文件；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow d"，清除所有人的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:r::allow d"，
#               允许NFS用户$username2列出目录d的内容；
#             4.以用户$username2挂载NFS，通过ls列出目录d内容，"ls d"。
# 预期结果  : 用户$username2可以成功列出目录的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-050
# 测试项目  : DAC-1.0-002-017
# 用例标题  : 拒绝NFS用户列出目录内容
# 用例简介  : 设置拒绝列出目录内容的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在d内创建若干文件；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:r::deny d"，
#               拒绝NFS用户$username2列出目录d的内容；
#             3.以用户$username2挂载NFS，通过ls列出目录d内容，"ls d"。
# 预期结果  : 用户$username2无法列出目录的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-051
# 测试项目  : DAC-1.0-002-017
# 用例标题  : 拒绝NFS用户列出目录内容
# 用例简介  : 未设置允许/拒绝列出目录内容的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在d内创建若干文件；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow d"，清除所有人的权限；
#             3.以用户$username2挂载NFS，通过ls列出目录d内容，"ls d"。
# 预期结果  : 用户$username2无法列出目录的内容
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-052
# 测试项目  : DAC-1.0-002-018
# 用例标题  : 允许NFS用户向目录中添加文件
# 用例简介  : 设置允许向目录中添加文件的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:w::allow d"，
#               允许NFS用户$username2向目录d中添加文件；
#             3.以用户$username2挂载NFS，进入目录d，通过touch添加文件f。
# 预期结果  : 用户$username2可以成功向目录中添加文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-053
# 测试项目  : DAC-1.0-002-018
# 用例标题  : 拒绝NFS用户向目录中添加文件
# 用例简介  : 设置拒绝向目录中添加文件的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:w::deny d"，
#               拒绝NFS用户$username2向目录d中添加文件；
#             3.以用户$username2挂载NFS，进入目录d，通过touch添加文件f。
# 预期结果  : 用户$username2无法向目录中添加文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-054
# 测试项目  : DAC-1.0-002-018
# 用例标题  : 拒绝NFS用户向目录中添加文件
# 用例简介  : 未设置允许/拒绝向目录中添加文件的权限，缺省拒绝
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.以用户$username2挂载NFS，进入目录d，通过touch添加文件f。
# 预期结果  : 用户$username2无法向目录中添加文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-055
# 测试项目  : DAC-1.0-002-019
# 用例标题  : 允许NFS用户在目录中添加子目录
# 用例简介  : 设置允许在目录中添加子目录的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:p::allow d"，
#               允许NFS用户$username2在目录d中添加子目录；
#             3.以用户$username2挂载NFS，进入目录d，通过mkdir添加子目录dd。
# 预期结果  : 用户$username2可以成功在目录中添加子目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-056
# 测试项目  : DAC-1.0-002-019
# 用例标题  : 拒绝NFS用户在目录中添加子目录
# 用例简介  : 设置拒绝在目录中添加子目录的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:p::deny d"，
#               拒绝NFS用户$username2在目录d中添加子目录；
#             3.以用户$username2挂载NFS，进入目录d，通过mkdir添加子目录dd。
# 预期结果  : 用户$username2无法在目录中添加子目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-057
# 测试项目  : DAC-1.0-002-019
# 用例标题  : 拒绝NFS用户在目录中添加子目录
# 用例简介  : 未设置允许/拒绝在目录中添加子目录的权限，缺省拒绝
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.以用户$username2挂载NFS，进入目录d，通过mkdir添加子目录dd。
# 预期结果  : 用户$username2无法在目录中添加子目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-058
# 测试项目  : DAC-1.0-002-020
# 用例标题  : 允许NFS用户遍历/查找目录
# 用例简介  : 设置允许遍历/查找目录的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow d"，清除所有人的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:x::allow d"，
#               允许NFS用户$username2遍历/查找目录d；
#             4.以用户$username2挂载NFS，通过cd进入目录d。
# 预期结果  : 用户$username2可以成功进入目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-059
# 测试项目  : DAC-1.0-002-020
# 用例标题  : 拒绝NFS用户遍历/查找目录
# 用例简介  : 设置拒绝遍历/查找目录的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:x::deny d"，
#               拒绝NFS用户$username2遍历/查找目录d；
#             3.以用户$username2挂载NFS，通过cd进入目录d。
# 预期结果  : 用户$username2无法进入目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-060
# 测试项目  : DAC-1.0-002-020
# 用例标题  : 拒绝NFS用户遍历/查找目录
# 用例简介  : 未设置允许/拒绝遍历/查找目录的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:::allow d"，清除所有人的权限；
#             3.以用户$username2挂载NFS，通过cd进入目录d。
# 预期结果  : 用户$username2无法进入目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-061
# 测试项目  : DAC-1.0-002-021
# 用例标题  : 允许NFS用户删除目录子文件
# 用例简介  : 设置允许删除目录子文件的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::allow d"，
#               允许NFS用户$username2删除目录d的子文件/子目录；
#             3.以用户$username2挂载NFS，进入目录d，通过rm命令删除文件f。
# 预期结果  : 用户$username2可以成功删除目录子文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-062
# 测试项目  : DAC-1.0-002-021
# 用例标题  : 拒绝NFS用户删除目录子文件
# 用例简介  : 设置拒绝删除目录子文件的权限
# 预置条件  : 1.NFSv3/NFSv4挂载ParaStor导出目录
#             2.新创建目录初始模式755
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在d内创建新文件f；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::deny d"，
#               拒绝NFS用户$username2删除目录d的子文件/子目录；
#             3.以用户$username2挂载NFS，进入目录d，通过rm命令删除文件f。
# 预期结果  : 用户$username2无法删除目录子文件
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-069
# 测试项目  : DAC-1.0-002-024
# 用例标题  : 允许NFS用户删除目录
# 用例简介  : 设置目录允许删除的权限，父目录拒绝删除子目录的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建子目录dd；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录d的权限；
#            3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::deny d"，
#               拒绝NFS用户$username2删除目录d的子目录；
#             4.在NAS节点私有客户端通过实用工具dac_setadvacl向目录dd添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::allow dd"，
#               允许NFS用户$username2删除目录dd；
#             5.以用户$username2挂载NFS，进入目录d，通过命令rmdir删除目录dd。
# 预期结果  : 用户$username2可以成功删除目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-070
# 测试项目  : DAC-1.0-002-024
# 用例标题  : 允许NFS用户删除目录
# 用例简介  : 设置目录拒绝删除的权限，父目录允许删除子目录的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建子目录dd；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录的权限；
#             3.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:d::allow d"，
#               允许NFS用户$username2删除目录d的子目录；
#             4.在NAS节点私有客户端通过实用工具dac_setadvacl向目录dd添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::deny dd"，
#               拒绝NFS用户$username2删除目录dd；
#             5.以用户$username2挂载NFS，进入目录d，通过命令rmdir删除目录dd。
# 预期结果  : 用户$username2可以成功删除目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-071
# 测试项目  : DAC-1.0-002-024
# 用例标题  : 允许NFS用户删除目录
# 用例简介  : 1.设置目录的父目录的粘住位S_ISVTX；
#             2.NFS用户$username2对目录的父目录有写权限，且是父目录的所有者。
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点内创建空目录d，在目录d内创建子目录dd；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -s everyone@:x::allow d"，
#               所有人仅允许进入目录的权限；
#             3.通过chmod设置目录d的粘住位，"chmod o+t d"；
#             4.通过chmod设置所有人对目录d有写权限，"chmod a+w d"；
#             5.通过chown设置目录d的所有者为$username2，"chown $username2 d"；
#             6.以用户$username2挂载NFS，进入目录d，通过命令rmdir删除目录dd。
# 预期结果  : 用户$username2可以成功删除目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-072
# 测试项目  : DAC-1.0-002-024
# 用例标题  : 拒绝NFS用户删除目录
# 用例简介  : 设置目录拒绝删除的权限
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建空目录d；
#             2.在NAS节点私有客户端通过实用工具dac_setadvacl向目录d添加一条
#               ACE，"dac_setadvacl -m USER:$username2:D::deny d"，
#               拒绝NFS用户$username2删除目录d；
#             3.以用户$username2挂载NFS，通过命令rmdir删除目录d。
# 预期结果  : 用户$username2无法删除目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-073
# 测试项目  : DAC-1.0-002-024
# 用例标题  : 拒绝NFS用户删除目录
# 用例简介  : 未设置目录允许/拒绝删除的权限，缺省拒绝
# 预置条件  : NFSv3/NFSv4挂载ParaStor导出目录
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建空目录d；
#             2.以用户$username2挂载NFS，通过命令rmdir删除目录d。
# 预期结果  : 用户$username2无法删除目录
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-001
# 测试项目  :
# 用例标题  : 检查特殊主体所有者权限
# 用例简介  : 拒绝所有者读数据权限，读取失败
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 owner@:r::deny；
#             3.以用户$username1在NFS客户端执行cat f。
# 预期结果  : 用户$username1无法获取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-002
# 测试项目  :
# 用例标题  : 检查特殊主体所有者权限
# 用例简介  : 允许所有者读数据权限，读取成功
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 owner@:r::allow；
#             3.以用户$username1在NFS客户端执行cat f。
# 预期结果  : 用户$username1成功读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-003
# 测试项目  :
# 用例标题  : 检查特殊主体所有组权限
# 用例简介  : 拒绝所有组读数据权限，读取失败
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 group@:r::deny；
#             3.以用户$username1在NFS客户端执行cat f。
# 预期结果  : 用户$username1无法读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-004
# 测试项目  :
# 用例标题  : 检查特殊主体所有组权限
# 用例简介  : 允许所有组读数据权限，读取成功
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 group@:r::allow；
#             3.以用户$username1在NFS客户端执行cat f。
# 预期结果  : 用户$username1成功读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-005
# 测试项目  :
# 用例标题  : 检查特殊主体Everyone权限
# 用例简介  : 拒绝Everyone读数据权限，读取失败
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 everyone@:r::deny；
#             3.以用户$username2在NFS客户端执行cat f。
# 预期结果  : 用户$username2无法读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-006
# 测试项目  :
# 用例标题  : 检查特殊主体Everyone权限
# 用例简介  : 允许Everyone读数据权限，读取成功
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 everyone@:r::allow；
#             3.以用户$username2在NFS客户端执行cat f。
# 预期结果  : 用户$username2成功读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
# 用例编号  : DAC-STUC-NFSD-EXT-007
# 测试项目  :
# 用例标题  : 用户属于多个用户组
# 用例简介  : 用户$username1为所有者，用户$username2属于组$username2、$username3
# 预置条件  :
# 输    入  :
# 执行步骤  : 1.以用户$username1挂载NFS，在挂载点创建新文件f；
#             2.在私有客户端设置f的Adv ACL为 G:$username2:r::allow,G:$username3:w::allow,everyone@:rw::deny；
#             3.以用户$username2在NFS客户端执行cat f。
# 预期结果  : 用户$username1成功读取文件数据
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年9月1日
#    作    者   : 王潇 <wangxiaob@sugon.com>
#    修改内容   : 设计用例
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
