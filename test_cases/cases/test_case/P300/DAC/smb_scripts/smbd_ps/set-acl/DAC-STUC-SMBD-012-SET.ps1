# �������  : DAC-STUC-SMBD-012
# ������Ŀ  : DAC-1.0-003-004
# ��������  : ��windowsȨ��λ��֧��002
# �������  : ֧���ļ��ж�Ȩ���������������ļ��ж������ɹ�
# Ԥ������  : �����ļ��У��ļ��ж�Ȩ��δ����
# ��    ��  : �����ļ��ж�Ȩ������
# ִ�в���  : 1.���û�administrator�������̣������ļ���dir1
#             2.����ļ���dir1�û�u1�������ļ���dir1�û�u1�Ķ�Ȩ������
#             3.���û�u1�������̣�
#             4.attrib dir1�鿴�ļ���dir1����:ע����\�鵵\ֻ�������ݲ�֧��
#             5.dir dir1�г��ļ���
#             6.��ȡ�ļ���dir1����չ����:�û�u1��
#             7.��ȡ�ļ���dir1��Ȩ��
# Ԥ�ڽ��  : 4��5��6��7�����ɹ�
# ��������  : �ļ���dir1��u1�û��Ķ�Ȩ��λ����������

# �޸���ʷ  :
#  1.��    ��   : 2016��3��22��
#    ��    ��   : ۡ�һ�<dizhh@sugon.com>
#    �޸�����   : ϵͳ��������
#access_mask = 0x100081 dir
#access_mask = 0x80  attrib
#access_mask = 0x20080 getacl
#access_mask = 0x100081 getcontent
#define ADVACE_READ_DATA            0x00000001 /* SEC_FILE_READ_DATA */
#define ADVACE_READ_ATTRIBUTES      0x00000080 /* SEC_FILE_READ_ATTRIBUTE/SEC_DIR_READ_ATTRIBUTE */
#define ADVACE_READ_ACL             0x00020000 /* SEC_STD_READ_CONTROL */

$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1


$testcase ="DAC-STUC-SMBD-012"
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

#set U1 ��Ȩ������
$objGroup =  $ad_set+$test_user_u1

$colRights = [System.Security.AccessControl.FileSystemRights]"Read"
#�����ļ���
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none

$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl

#set U1 ��չ����
Set-Content -Path $dir_path -Value testads -Stream ads
