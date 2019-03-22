#!/bin/sh
#
# Date:     2016-08-02
# Author:   Wang Xiao (wangxiaob@sugon.com)
#

source ./config.sh

acc_mask_all='rwpxdDaARWcCoS'

# ensure the existence of the following users on server side
# username1='u1'
# username2='u2'
# username3='u3'
username1=$1
username2=$2
username3=$3  # changed by zhanghan 20181126
nfs_serv_ip=$4
nfs_serv_exp_path=$5
nfs_cli_mnt_path=$6  # add by zhanghan 20181127

# server clean and config
ssh $nfs_serv_ip "cd $nfs_serv_exp_path;
                  rm -rf d1 d2 d3;
                  mkdir d1 d2 d3;
                  dac_setadvacl -s owner@:$acc_mask_all:fd:allow,everyone@:x::allow d1;
                  dac_setadvacl -m U:$username1:$acc_mask_all:fd:deny d1;
                  dac_setadvacl -m U:$username2:r::allow d1;
                  dac_setadvacl -m U:$username2:rwpxdD:fdi:deny d1;
                  dac_setadvacl -m U:$username3:raRc:fdi:allow d1;
                  dac_setadvacl -m U:$username3:r::deny d1;
                  dac_setadvacl -m U:$username3:wpdD:fdi:deny d1;
                  touch d1/f1 d1/f2 d1/f3;
                  dac_setadvacl -s owner@:$acc_mask_all:fd:allow,everyone@:x::allow d2;
                  dac_setadvacl -m U:$username1:wpaARWc:fdi:allow d2;
                  dac_setadvacl -m U:$username1:r::deny d2;
                  dac_setadvacl -m U:$username1:rxdD:fdi:deny d2;
                  dac_setadvacl -m U:$username2:r::allow d2;
                  dac_setadvacl -m U:$username2:wpaARWc:fdi:allow d2;
                  dac_setadvacl -m U:$username2:rdD:fdi:deny d2;
                  dac_setadvacl -m U:$username3:$acc_mask_all:fd:allow d2;
                  touch d2/f1 d2/f2 d2/f3;
                  dac_setadvacl -s owner@:$acc_mask_all:fd:allow,everyone@:x::allow d3;
                  dac_setadvacl -m U:$username1:dD:fdi:allow d3;
                  dac_setadvacl -m U:$username1:r::deny d3;
                  dac_setadvacl -m U:$username1:rwpAW:fdi:deny d3;
                  dac_setadvacl -m U:$username2:r::allow d3;
                  dac_setadvacl -m U:$username2:dD:fdi:allow d3;
                  dac_setadvacl -m U:$username2:rwpAW:fdi:deny d3;
                  dac_setadvacl -m U:$username3:rdDaRc:fdi:allow d3;
                  dac_setadvacl -m U:$username3:r::deny d3;
                  dac_setadvacl -m U:$username3:wpAW:fdi:deny d3;
                  touch d3/f1 d3/f2 d3/f3"

# [START]: runing testcases
cd $nfs_cli_mnt_path
total=0
pass=0
fail=0

# testcase1
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u1操作目录d1
# 执行步骤  : 1. 以用户u1在NFS客户端执行ls d1；
#             2. 以用户u1在NFS客户端执行cat d1/f1；
#             3. 以用户u1在NFS客户端执行echo 'sugon' > d1/f1；
#             4. 以用户u1在NFS客户端执行rm -f d1/f1；
# 预期结果  : 1. 用户u1无法列出目录内容d1；
#             2. 用户u1无法读取文件d1/f1；
#             3. 用户u1无法写入文件d1/f1；
#             4. 用户u1无法删除文件d1/f1；
su $username1 -c 'ls d1'
if [ $? != 0 ]; then
    echo "[TC1] $username1 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'cat d1/f1'
if [ $? != 0 ]; then
    echo "[TC1] $username1 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c "echo 'sugon' > d1/f1"
if [ $? != 0 ]; then
    echo "[TC1] $username1 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'rm -f d1/f1'
if [ $? != 0 ]; then
    echo "[TC1] $username1 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase2
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u2操作目录d1
# 执行步骤  : 1. 以用户u2在NFS客户端执行ls d1；
#             2. 以用户u2在NFS客户端执行cat d1/f2；
#             3. 以用户u2在NFS客户端执行echo 'sugon' > d1/f2；
#             4. 以用户u2在NFS客户端执行rm -f d1/f2；
# 预期结果  : 1. 用户u2成列出目录内容d1；
#             2. 用户u2无法读取文件d1/f2；
#             3. 用户u2无法写入文件d1/f2；
#             4. 用户u2无法删除文件d1/f2；
su $username2 -c 'ls d1'
if [ $? == 0 ]; then
    echo "[TC2] $username2 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'cat d1/f2'
if [ $? != 0 ]; then
    echo "[TC2] $username2 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c "echo 'sugon' > d1/f2"
if [ $? != 0 ]; then
    echo "[TC2] $username2 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'rm -f d1/f2'
if [ $? != 0 ]; then
    echo "[TC2] $username2 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase3
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u3操作目录d1
# 执行步骤  : 1. 以用户u3在NFS客户端执行ls d1；
#             2. 以用户u3在NFS客户端执行cat d1/f3；
#             3. 以用户u3在NFS客户端执行echo 'sugon' > d1/f3；
#             4. 以用户u3在NFS客户端执行rm -f d1/f3；
# 预期结果  : 1. 用户u3无法列出目录内容d1；
#             2. 用户u3成功读取文件d1/f3；
#             3. 用户u3无法写入文件d1/f3；
#             4. 用户u3无法删除文件d1/f3；
su $username3 -c 'ls d1'
if [ $? != 0 ]; then
    echo "[TC3] $username3 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'cat d1/f3'
if [ $? == 0 ]; then
    echo "[TC3] $username3 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c "echo 'sugon' > d1/f3"
if [ $? != 0 ]; then
    echo "[TC3] $username3 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'rm -f d1/f3'
if [ $? != 0 ]; then
    echo "[TC3] $username3 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase4
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u1操作目录d2
# 执行步骤  : 1. 以用户u1在NFS客户端执行ls d2；
#             2. 以用户u1在NFS客户端执行cat d2/f1；
#             3. 以用户u1在NFS客户端执行echo 'sugon' > d2/f1；
#             4. 以用户u1在NFS客户端执行rm -f d2/f1；
# 预期结果  : 1. 用户u1无法列出目录内容d2；
#             2. 用户u1无法读取文件d2/f1；
#             3. 用户u1成功写入文件d2/f1；
#             4. 用户u1无法删除文件d2/f1；
su $username1 -c 'ls d2'
if [ $? != 0 ]; then
    echo "[TC4] $username1 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'cat d2/f1'
if [ $? != 0 ]; then
    echo "[TC4] $username1 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c "echo 'sugon' > d2/f1"
if [ $? == 0 ]; then
    echo "[TC4] $username1 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'rm -f d2/f1'
if [ $? != 0 ]; then
    echo "[TC4] $username1 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase5
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u2操作目录d2
# 执行步骤  : 1. 以用户u2在NFS客户端执行ls d2；
#             2. 以用户u2在NFS客户端执行cat d2/f2；
#             3. 以用户u2在NFS客户端执行echo 'sugon' > d2/f2；
#             4. 以用户u2在NFS客户端执行rm -f d2/f2；
# 预期结果  : 1. 用户u2成功列出目录内容d2；
#             2. 用户u2无法读取文件d2/f2；
#             3. 用户u2成功写入文件d2/f2；
#             4. 用户u2无法删除文件d2/f2；
su $username2 -c 'ls d2'
if [ $? == 0 ]; then
    echo "[TC5] $username2 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'cat d2/f2'
if [ $? != 0 ]; then
    echo "[TC5] $username2 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c "echo 'sugon' > d2/f2"
if [ $? == 0 ]; then
    echo "[TC5] $username2 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'rm -f d2/f2'
if [ $? != 0 ]; then
    echo "[TC5] $username2 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase6
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u3操作目录d2
# 执行步骤  : 1. 以用户u3在NFS客户端执行ls d2；
#             2. 以用户u3在NFS客户端执行cat d2/f3；
#             3. 以用户u3在NFS客户端执行echo 'sugon' > d2/f3；
#             4. 以用户u3在NFS客户端执行rm -f d2/f3；
# 预期结果  : 1. 用户u3成功列出目录内容d2；
#             2. 用户u3成功读取文件d2/f3；
#             3. 用户u3成功写入文件d2/f3；
#             4. 用户u3成功删除文件d2/f3；
su $username3 -c 'ls d2'
if [ $? == 0 ]; then
    echo "[TC6] $username3 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'cat d2/f3'
if [ $? == 0 ]; then
    echo "[TC6] $username3 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c "echo 'sugon' > d2/f3"
if [ $? == 0 ]; then
    echo "[TC6] $username3 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'rm -f d2/f3'
if [ $? == 0 ]; then
    echo "[TC6] $username3 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase7
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u1操作目录d3
# 执行步骤  : 1. 以用户u1在NFS客户端执行ls d3；
#             2. 以用户u1在NFS客户端执行cat d3/f1；
#             3. 以用户u1在NFS客户端执行echo 'sugon' > d3/f1；
#             4. 以用户u1在NFS客户端执行rm -f d3/f1；
# 预期结果  : 1. 用户u1无法列出目录内容d3；
#             2. 用户u1无法读取文件d3/f1；
#             3. 用户u1无法写入文件d3/f1；
#             4. 用户u1成功删除文件d3/f1；
su $username1 -c 'ls d3'
if [ $? != 0 ]; then
    echo "[TC7] $username1 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'cat d3/f1'
if [ $? != 0 ]; then
    echo "[TC7] $username1 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c "echo 'sugon' > d3/f1"
if [ $? != 0 ]; then
    echo "[TC7] $username1 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username1 -c 'rm -f d3/f1'
if [ $? == 0 ]; then
    echo "[TC7] $username1 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase8
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u2操作目录d3
# 执行步骤  : 1. 以用户u2在NFS客户端执行ls d3；
#             2. 以用户u2在NFS客户端执行cat d3/f2；
#             3. 以用户u2在NFS客户端执行echo 'sugon' > d3/f2；
#             4. 以用户u2在NFS客户端执行rm -f d3/f2；
# 预期结果  : 1. 用户u2成功列出目录内容d3；
#             2. 用户u2无法读取文件d3/f2；
#             3. 用户u2无法写入文件d3/f2；
#             4. 用户u2成功删除文件d3/f2；
su $username2 -c 'ls d3'
if [ $? == 0 ]; then
    echo "[TC8] $username2 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'cat d3/f2'
if [ $? != 0 ]; then
    echo "[TC8] $username2 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c "echo 'sugon' > d3/f2"
if [ $? != 0 ]; then
    echo "[TC8] $username2 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username2 -c 'rm -f d3/f2'
if [ $? == 0 ]; then
    echo "[TC8] $username2 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# testcase9
# 用例标题  : 国防科大POC用例
# 用例简介  : 用户u3操作目录d3
# 执行步骤  : 1. 以用户u3在NFS客户端执行ls d3；
#             2. 以用户u3在NFS客户端执行cat d3/f3；
#             3. 以用户u3在NFS客户端执行echo 'sugon' > d3/f3；
#             4. 以用户u3在NFS客户端执行rm -f d3/f3；
# 预期结果  : 1. 用户u3无法列出目录内容d3；
#             2. 用户u3成功读取文件d3/f3；
#             3. 用户u3无法写入文件d3/f3；
#             4. 用户u3成功删除文件d3/f3；
su $username3 -c 'ls d3'
if [ $? != 0 ]; then
    echo "[TC9] $username3 (L) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'cat d3/f3'
if [ $? == 0 ]; then
    echo "[TC9] $username3 (R) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c "echo 'sugon' > d3/f3"
if [ $? != 0 ]; then
    echo "[TC9] $username3 (W) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

su $username3 -c 'rm -f d3/f3'
if [ $? == 0 ]; then
    echo "[TC9] $username3 (D) perm check pass." >> $LOG
    let pass+=1
else
    echo 'Permission check result undesirable!' >> $ELOG
    let fail+=1
fi

# [END]: all testcases successfully
let total=$pass+$fail
echo "All test cases done! [Total check: $total Pass: $pass Fail: $fail]" >> $LOG
