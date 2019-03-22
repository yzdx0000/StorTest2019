﻿<#*****************************************************************************
 用例编号  : DAC-STUC-SMBD-040
 测试项目  : DAC-1.0-003-007
 用例标题  : 对windows权限主体的支持001
 用例简介  : 设置CREATOR OWNER主体的权限，使用用户创建文件，并验证权限
 预置条件  : 1.系统已经开启高级权限控制
             2.系统使用AD作为用户服务器
             3.在windows上创建测试目录
             4.设置测试目录CREATOR OWNER主体的权限为只读
 输    入  : 使用u1用户创建子文件，并对其进行读写操作
 执行步骤  : 1.在windows上创建测试目录d1
             2.对d1添加高级权限，设置主体为CREATOR OWNER，权限只读，仅子文件及文件夹
               为确保用户可在该目录下创建文件，应增加everyone，完全控制，只有该文件夹
             3.使用u1用户登录Windows系统并挂载文件系统
             4.创建子文件file.txt，并对其进行读写操作
 预期结果  : u1用户对文件file.txt可读，写被拒绝
 后置条件  : 文件file.txt的权限列表中存在对u1用户的权限设置项

 修改历史  :
  1.日    期   : 2016年3月30日
    作    者   : 金顺 <jinshun@sugon.com>
    修改内容   : 系统测试用例

*****************************************************************************#>
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$st_case="DAC-STUC-SMBD-040"
$dir_path=$net_driver_path+$st_case

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

#2.delete other objAce;
$e_id="everyone"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"none"
$objAce_1=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)
$e_id=$ad_set+"\Domain Users"
$objAce_2=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#3.CREATOR OWNER
$e_id="CREATOR OWNER"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Read"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"InheritOnly"
$objAce_3=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#set the acl to object. 
$objAcl=Get-Acl $dir_path
$objAcl.AddAccessRule($objAce_0)
$objAcl.AddAccessRule($objAce_1)
$objAcl.RemoveAccessRule($objAce_2)
$objAcl.AddAccessRule($objAce_3)
Set-Acl -Path $dir_path -Aclobject $objAcl