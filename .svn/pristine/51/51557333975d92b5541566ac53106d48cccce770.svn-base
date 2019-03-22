#设置xml文件u1完全控制
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$test_user_u1=$xmldoc.path_info.test_user_u1
$file_path = "$xmlpath\..\pathinfo.xml"

#set acl
$objAcl = Get-Acl $file_path

#set U1 权限
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
#只有该文件夹
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $file_path -Aclobject $objAcl


