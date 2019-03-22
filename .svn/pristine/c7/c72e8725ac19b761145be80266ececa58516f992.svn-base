<#*****************************************************************************
  用例编号  : DAC-STUC-SMBD-045
 测试项目  : DAC-1.0-003-007
 用例标题  : 对windows权限主体的支持006
 用例简介  : 设置普通用户主体的权限，并验证其权限
 预置条件  : 1.系统已经开启高级权限控制
             2.系统使用AD作为用户服务器
             3.在windows上创建测试目录
             4.在测试目录中创建子文件
             5.在域中新建可用用户user1
 输    入  : 在windows上设置测试目录权限，user1用户对子文件进行读写操作
 执行步骤  : 1.在windows上创建测试目录d6
             2.创建子文件file.txt
             3.对d6添加高级权限，设置主体为user1，权限只读
             4.使用user1用户登录Windows系统并挂载文件系统
             5.对子文件file.txt进行读写操作
 预期结果  : 文件file.txt对user1用户为可读，写被拒绝
 后置条件  : 子文件file.txt的权限列表中存在user1的权限设置项

 修改历史  :
  1.日    期   : 2016年3月25日
    作    者   : 金顺 <jinshun@sugon.com>
    修改内容   : 系统测试用例



*****************************************************************************#>
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$st_case="DAC-STUC-SMBD-045"
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

#2.delete everyone 
$e_id="everyone"
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Read"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_1=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#3. user: u1, allow read and write
$e_id=$ad_set+$test_user_u1
$e_type=[System.Security.AccessControl.AccessControlType]"allow"
$e_mask=[System.Security.AccessControl.FileSystemRights]"Read,Write"
$e_flag=[System.Security.AccessControl.InheritanceFlags]"ObjectInherit,ContainerInherit"
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]"none"
$objAce_2=New-Object System.Security.AccessControl.FileSystemAccessRule($e_id,$e_mask,$e_flag,$PropagationFlag,$e_type)

#set the acl to object. 
$objAcl=Get-Acl $dir_path
$objAcl.AddAccessRule($objAce_0)
$objAcl.RemoveAccessRule($objAce_1)
$objAcl.AddAccessRule($objAce_2)
Set-Acl -Path $dir_path -Aclobject $objAcl

#创建文件file.txt
New-Item $file_path -Force -ItemType file