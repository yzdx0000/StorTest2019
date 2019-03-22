# 用例编号  : DAC-STUC-SMBD-015
# 测试项目  : DAC-1.0-003-004
# 用例标题  : 对windows权限位的支持005
# 用例简介  : 支持文件夹删除权限设置允许；测试文件夹删除操作成功
# 预置条件  : 创建文件夹，文件夹删除权限未设置
# 输    入  : 设置文件夹删除权限允许
# 执行步骤  : 1.以用户administrator挂载网盘，创建文件夹dir1、子文件夹dir1_c1和子
#               文件file1
#             2.添加文件夹dir1用户u1，设置文件夹dir1用户u1的删除、删除子文件夹和
#               文件权限允许
#             3.以用户u1挂载网盘，删除dir1下面的dir1_c1和file1
#             4.删除dir1
# 预期结果  : 3、4操作成功
# 后置条件  : 文件夹dir1的u1用户的删除、删除子文件夹和文件权限位被设置允许
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 邸忠辉<dizhh@sugon.com>
#    修改内容   : 系统测试用例
#注：删除需要ReadData ReadAttributes权限


$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$testcase ="DAC-STUC-SMBD-015"
$dir_path = $net_driver_path+$testcase

#step 1 mkdir 
Remove-Item -Path $dir_path -Force -recurse 
mkdir $dir_path

#step 2 set acl

#删除everyone
$objGroup = "everyone"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl = Get-Acl $dir_path
$objAcl.RemoveAccessRule($objAce)

#设置administrator
$objGroup = $ad_set+"\administrator"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
#文件夹、子文件夹和文件
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)

#删除Domain Users
$objGroup = $ad_set+"\Domain Users"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.RemoveAccessRule($objAce)

#设置U1删除权限
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"DeleteSubdirectoriesAndFiles, Delete,ReadAttributes,WrietAttributes"
#文件夹、子文件夹和文件
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none

$objType=[System.Security.AccessControl.AccessControlType]::Allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)
Set-Acl -Path $dir_path -Aclobject $objAcl

#在dir1下面创建文件file1、子文件夹dir_sub1
$file_path=$dir_path+"\file.txt"
echo "test" > $file_path
$dir_sub= $dir_path+"\dir_sub1"
mkdir $dir_sub
