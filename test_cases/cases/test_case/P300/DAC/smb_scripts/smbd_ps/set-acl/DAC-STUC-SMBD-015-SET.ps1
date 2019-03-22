# �������  : DAC-STUC-SMBD-015
# ������Ŀ  : DAC-1.0-003-004
# ��������  : ��windowsȨ��λ��֧��005
# �������  : ֧���ļ���ɾ��Ȩ���������������ļ���ɾ�������ɹ�
# Ԥ������  : �����ļ��У��ļ���ɾ��Ȩ��δ����
# ��    ��  : �����ļ���ɾ��Ȩ������
# ִ�в���  : 1.���û�administrator�������̣������ļ���dir1�����ļ���dir1_c1����
#               �ļ�file1
#             2.����ļ���dir1�û�u1�������ļ���dir1�û�u1��ɾ����ɾ�����ļ��к�
#               �ļ�Ȩ������
#             3.���û�u1�������̣�ɾ��dir1�����dir1_c1��file1
#             4.ɾ��dir1
# Ԥ�ڽ��  : 3��4�����ɹ�
# ��������  : �ļ���dir1��u1�û���ɾ����ɾ�����ļ��к��ļ�Ȩ��λ����������
# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ۡ�һ�<dizhh@sugon.com>
#    �޸�����   : ϵͳ��������
#ע��ɾ����ҪReadData ReadAttributesȨ��


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

#ɾ��everyone
$objGroup = "everyone"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl = Get-Acl $dir_path
$objAcl.RemoveAccessRule($objAce)

#����administrator
$objGroup = $ad_set+"\administrator"
$colRights = [System.Security.AccessControl.FileSystemRights]"FullControl"
#�ļ��С����ļ��к��ļ�
$InheritanceFlag='ObjectInherit,ContainerInherit'
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

#����U1ɾ��Ȩ��
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"DeleteSubdirectoriesAndFiles, Delete,ReadAttributes,WrietAttributes"
#�ļ��С����ļ��к��ļ�
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none

$objType=[System.Security.AccessControl.AccessControlType]::Allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)
Set-Acl -Path $dir_path -Aclobject $objAcl

#��dir1���洴���ļ�file1�����ļ���dir_sub1
$file_path=$dir_path+"\file.txt"
echo "test" > $file_path
$dir_sub= $dir_path+"\dir_sub1"
mkdir $dir_sub
