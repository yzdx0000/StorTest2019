# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 邸忠辉<dizhh@sugon.com>
#    修改内容   : 系统测试用例

# 用例编号  : DAC-STUC-SMBD-023
# 测试项目  : DAC-1.0-003-005
# 用例标题  : 对windows权限类型支持002
# 用例简介  : 支持文件夹读权限设置拒绝；测试文件夹读操作失败
# 预置条件  : 创建文件夹，文件夹读权限未设置
# 输    入  : 设置文件夹读权限拒绝
# 执行步骤  : 1.以用户administrator挂载网盘，创建文件夹dir1
#             2.添加文件夹dir1用户u1，设置文件夹dir1用户u1的读权限拒绝
#             3.以用户u1挂载网盘
#             4.attrib dir1查看文件夹dir1属性
#             5.dir dir1列出文件夹
#             6.读取文件夹dir1的扩展属性:用户u1等
#             7.读取文件夹dir1的权限
# 预期结果  : 4、5、6、7操作失败
# 后置条件  : 文件夹dir1的u1用户的读权限位被设置拒绝
#
# 修改历史  :
#  1.日    期   : 2016年3月22日
#    作    者   : 邸忠辉<dizhh@sugon.com>
#    修改内容   : 系统测试用例
#:注隐藏\归档\只读属性暂不支持
#注 读取属性拒绝不起作用，本地文件系统也是如此。
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1


$testcase ="DAC-STUC-SMBD-023"
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

#set U1 读权限允许
$objGroup =  $ad_set+$test_user_u1

$colRights = [System.Security.AccessControl.FileSystemRights]"Read"
#仅该文件夹
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none

$objType=[System.Security.AccessControl.AccessControlType]::deny
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl




