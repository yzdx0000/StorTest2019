# 用例编号  : DAC-STUC-SMBD-032
# 测试项目  : DAC-1.0-003-005
# 用例标题  : 对windows权限类型支持011
# 用例简介  : 支持文件删除权限设置拒绝；测试文件删除操作失败
# 预置条件  : 创建文件，文件删除权限未设置
# 输    入  : 设置文件删除权限拒绝
# 执行步骤  : 1.以用户administrator挂载网盘，创建文件file1
#             2.添加文件file1用户u1，设置文件file1用户u1的删除权限拒绝
#             3.以用户u1挂载网盘，删除file1
# 预期结果  : 删除操作失败
# 后置条件  : 文件file1的u1用户的删除被设置拒绝
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 邸忠辉<dizhh@sugon.com>
#    修改内容   : 系统测试用例

$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$testcase ="DAC-STUC-SMBD-032"
$dir_path = $net_driver_path+$testcase

#step 1 mkdir 
Remove-Item -Path $dir_path -Force -recurse 
mkdir $dir_path
#创建子文件file1.txt
$file_path =$dir_path+"\file.txt"
echo $testcase > $file_path
 
#step 2 set acl

#删除everyone
$objGroup = "everyone"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl = Get-Acl $file_path
$objAcl.RemoveAccessRule($objAce)

#设置administrator
$objGroup = $ad_set+"\administrator"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
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

#设置u1 acl
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"DeleteSubdirectoriesAndFiles, Delete,ReadData"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Deny

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)
Set-Acl -Path $file_path -Aclobject $objAcl

