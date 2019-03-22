<#*****************************************************************************
 用例编号  : DAC-STUC-SMBD-053
 测试项目  : DAC-1.0-003-011
 用例标题  : ACL检查算法003
 用例简介  : 文件同时拥有用户u1的继承与非继承高级权限，使用u1对文件进行操作
 预置条件  : 1. 系统已经开启高级权限控制
             2. 文件具有继承ACE对u1用户拒绝写操作
             3. 添加文件ACE对u1用户允许写操作
 输    入  : 使用u1用户对文件进行读操作
 执行步骤  : 1. 确保开启高级权限控制
             2. 添加文件父目录ACE对用户u1拒绝写操作并应用于子文件
             3. 添加文件ACE对用户u1允许写操作
             4. 使用u1用户登录Windows系统并挂载文件系统
             5. 对文件进行写操作
 预期结果  : u1用户可以写文件
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

$st_case="DAC-STUC-SMBD-053"
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

#if directroy exsited, delete it.
Remove-Item -Path $dir_path -Force -Recurse
mkdir $dir_path

#=====set parent directory acl=====
#1.administrator full contorl;
$e_id=$ad_set+"\administrator"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"FullControl"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_0=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#2.u1 denied Write
$e_id=$ad_set+$test_user_u1
$e_type=[System.Security.AccessControl.AccessControlType]"deny"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Write"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"InheritOnly"
$objAce_1=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#3.everyone allow Read
$e_id="everyone"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Read"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_2=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#set the acl to object. 
$objAcl=Get-Acl $dir_path
$objAcl.AddAccessRule($objAce_0)
$objAcl.AddAccessRule($objAce_1)
$objAcl.AddAccessRule($objAce_2)
Set-Acl -Path $dir_path -Aclobject $objAcl

#创建文件file.txt
New-Item $file_path -Force -ItemType file

#=====set file acl=====
#1.u1 allow Write
$e_id=$ad_set+$test_user_u1
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Write"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"none"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_3=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#set the acl to object. 
$objAcl=Get-Acl $file_path
$objAcl.AddAccessRule($objAce_3)
Set-Acl -Path $file_path -Aclobject $objAcl
