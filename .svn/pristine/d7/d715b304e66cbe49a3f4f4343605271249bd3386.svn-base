#设置读和执行权限
# 用例编号  : DAC-STUC-SMBD-027
# 测试项目  : DAC-1.0-003-005
# 用例标题  : 对windows权限类型支持006
# 用例简介  : 支持文件执行权限设置拒绝；测试文件执行操作失败
# 预置条件  : 可执行文件notepad.exe，其执行权限未设置
# 输    入  : 设置文件执行权限拒绝
# 执行步骤  : 1.以用户administrator挂载网盘，copy notepad.exe可执行文件到网盘
#             2.添加notepad.exe文件用户u1，设置notepad.exe用户u1的执行权限拒绝
#             3.以用户u1挂载网盘，执行notepad.exe
# 预期结果  : 执行操作失败
# 后置条件  : 文件notepad.exe的u1用户的执行权限被设置拒绝
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

$testcase ="DAC-STUC-SMBD-027"
$dir_path = $net_driver_path+$testcase

#step 1 mkdir and copy file
Remove-Item -Path $dir_path -Force -recurse 
mkdir $dir_path

copy-item $xmlpath\..\du.exe -destination $dir_path
$file_path = $dir_path+"\du.exe"

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

#设置 u1 acl
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"ReadAndExecute"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Deny

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)

Set-Acl -Path $file_path -Aclobject $objAcl




