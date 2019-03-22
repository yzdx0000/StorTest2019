# �������  : DAC-STUC-SMBD-019
# ������Ŀ  : DAC-1.0-003-004
# ��������  : ��windowsȨ��λ��֧��009
# �������  : ֧���ļ�"����Ȩ��"Ȩ�����������������ļ�"����Ȩ��"�����ɹ�
# Ԥ������  : �����ļ����ļ�"����Ȩ��"Ȩ��δ����
# ��    ��  : �����ļ�"����Ȩ��"Ȩ������
# ִ�в���  : 1.���û�administrator�������̣������ļ�file1
#             2.�����ļ�file1�û�u1�������ļ�file1�û�u1��"����Ȩ��"Ȩ������
#             3.�����ļ�file1�Ķ�Ȩ������
# Ԥ�ڽ��  : ����3�����ɹ�
# ��������  : �ļ�file1��u1�û���"����Ȩ��"����Ȩ��λ����������
#
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ۡ�һ�<dizhh@sugon.com>
#    �޸�����   : ϵͳ��������

$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$testcase ="DAC-STUC-SMBD-019"
$dir_path = $net_driver_path+$testcase

#step 1 mkdir 
Remove-Item -Path $dir_path -Force -recurse 
mkdir $dir_path
#�������ļ�file1.txt
$file_path =$dir_path+"\file.txt"
echo $testcase > $file_path
 
#step 2 set acl

#ɾ��everyone
$objGroup = "everyone"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl = Get-Acl $file_path
$objAcl.RemoveAccessRule($objAce)

#����administrator
$objGroup = $ad_set+"\administrator"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)

#ɾ��Domain Users
$objGroup = $ad_set+"\Domain Users"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.RemoveAccessRule($objAce)

#����u1 acl
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"ReadAttributes,ReadPermissions, ChangePermissions"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)
Set-Acl -Path $file_path -Aclobject $objAcl
