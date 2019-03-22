# 用例编号  : DAC-STUC-SMBD-034
# 测试项目  : DAC-1.0-003-006
# 用例标题  : 对windows目录权限应用方式的支持002
# 用例简介  : 支持文件夹"此文件夹、子文件夹和文件"权限应用方式的设置；该文件夹设
#             置权限，子文件和子文件夹继承
#             该文件夹的该权限
# 预置条件  : 创建文件夹、子文件及子文件夹
# 输    入  : 设置文件夹写权限，权限应用方式为"此文件夹、子文件夹和文件"
# 执行步骤  : 1.以用户administrator挂载网盘，创建文件夹dir1
#             2.添加文件夹dir1用户u1，设置文件夹dir1用户u1的写权限，权限应用方式
#               为"此文件夹、子文件夹和文件
#             3.创建dir1的子文件夹dir2和子文件file1
#             4.以用户u1挂载网盘，创建dir1子文件file2，创建dir2子文件file3，写dir
#               子文件file1
# 预期结果  : 步骤4创建file2、file3及写file1操作成功
# 后置条件  :
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

$testcase ="DAC-STUC-SMBD-034"
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


#set U1 文件夹权限允许
$objGroup =  $ad_set+$test_user_u1
#对测试项添加读和执行权限
$colRights = [System.Security.AccessControl.FileSystemRights]"ExecuteFile,Read"
#文件夹、子文件夹和文件
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

#添加测试写权限
$colRights = [System.Security.AccessControl.FileSystemRights]"Write"
#文件夹、子文件夹和文件
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl


#创建$dir_path子文件夹dir_sub1 
$dir_sub1= $dir_path+"\dir_sub1"
mkdir $dir_sub1

#创建$dir_path子文件file_1.txt 
$file_1= $dir_path+"\file_1.txt"
echo file_1 >$file_1



