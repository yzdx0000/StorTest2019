# 用例编号  : DAC-STUC-SMBD-022
# 测试项目  : DAC-1.0-003-005
# 用例标题  : 对windows权限类型支持001
# 用例简介  : 支持文件夹遍历文件夹权限设置拒绝；测试文件夹遍历文件夹操作失败
# 预置条件  : 创建文件夹，文件夹遍历文件夹权限未设置
# 输    入  : 设置文件夹遍历文件夹权限拒绝
# 执行步骤  : 1.以用户administrator挂载网盘，创建文件夹dir1
#             2.添加文件夹dir1用户u1，设置文件夹dir1用户u1的遍历文件夹权限拒绝
#             3.以用户u1挂载网盘，cd进入文件夹
# 预期结果  : 进入文件夹操作失败
# 后置条件  : 文件夹dir1的u1用户的遍历文件夹权限位被设置拒绝
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 邸忠辉<dizhh@sugon.com>
#    修改内容   : 系统测试用例
#注traverse属性windows不支持拒绝
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$testcase ="DAC-STUC-SMBD-022"
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


#set U1 遍历文件夹权限 拒绝
$objGroup =  $ad_set+$test_user_u1
#$colRights = [System.Security.AccessControl.FileSystemRights]"ExecuteFile,Read"
$colRights = [System.Security.AccessControl.FileSystemRights]"ExecuteFile"
#只有该文件夹
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Deny
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl

#在dir下面创建文件file1
$file_path= $dir_path+"\file1.txt"
echo "test" > $file_path

$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"Read"
#只有该文件夹
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl_file = Get-Acl $file_path
$objAcl_file.AddAccessRule($objAce)

Set-Acl -Path $file_path -Aclobject $objAcl_file 


