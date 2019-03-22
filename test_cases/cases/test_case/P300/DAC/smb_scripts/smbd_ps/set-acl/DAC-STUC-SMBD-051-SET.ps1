<#*****************************************************************************
 用例编号  : DAC-STUC-SMBD-051
 测试项目  : DAC-1.0-003-011
 用例标题  : ACL检查算法001
 用例简介  : 对文件设置用户u1的高级权限，使用u1和u2分别对文件进行操作
 预置条件  : 1. 系统已经开启高级权限控制
             2. 设置文件ACL为对u1用户允许读操作
 输    入  : 分别使用u1和u2用户对文件进行读操作
 执行步骤  : 1. 确保开启高级权限控制
             2. 设置文件ACL为对用户u1允许读
             3. 使用u1用户登录Windows系统并挂载文件系统
             4. 对文件进行读操作
             5. 使用u2用户登录Windows系统并挂载文件系统
             6. 对文件进行读操作
 预期结果  : u1用户可以读文件，u2用户读文件被拒绝
 后置条件  :

 修改历史  :
  1.日    期   : 2016年3月24日
    作    者   : 王喆 <wangzhea@sugon.com>
    修改内容   : 设计用例

*****************************************************************************#>
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$st_case="DAC-STUC-SMBD-051"
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

#if directroy exsited, delete it.
Remove-Item -Path $dir_path -Force -Recurse
mkdir $dir_path
#创建文件file.txt
New-Item $file_path -Force -ItemType file

#=====set file acl=====
#1.administrator full contorl;
$e_id=$ad_set+"\administrator"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"FullControl"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"none"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_0=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#2. user u1 allow read
$e_id=$ad_set+$test_user_u1
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Read"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"none"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_1=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#3.delete everyone
$e_id="everyone"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"FullControl"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"none"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_2=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#set the acl to object. 
$objAcl=Get-Acl $file_path
$objAcl.AddAccessRule($objAce_0)
$objAcl.AddAccessRule($objAce_1)
$objAcl.RemoveAccessRule($objAce_2)
Set-Acl -Path $file_path -Aclobject $objAcl

