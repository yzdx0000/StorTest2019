# �������  : DAC-STUC-SMBD-017
# ������Ŀ  : DAC-1.0-003-004
# ��������  : ��windowsȨ��λ��֧��007
# �������  : ֧���ļ���Ȩ���������������ļ��������ɹ�
# Ԥ������  : �����ļ����ļ���Ȩ��δ����
# ��    ��  : �����ļ���Ȩ������
# ִ�в���  : 1.���û�administrator�������̣������ļ�file1
#             2.����ļ�file1�û�u1�������ļ�file1�û�u1�Ķ�Ȩ������
#             3.���û�u1�������̣�
#             4.attrib file1�鿴�ļ�file1����
#             5.type file1��ȡ�ļ�
#             6.��ȡ�ļ�file1����չ����:�û�u1��
#             7.��ȡ�ļ�file1��Ȩ��
# Ԥ�ڽ��  : 4��5��6��7�����ɹ�
# ��������  : �ļ�file1��u1�û��Ķ�Ȩ��λ����������

$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_user_u1=$xmldoc.path_info.test_user_u1

$testcase ="DAC-STUC-SMBD-017"
$dir_path = $net_driver_path+$testcase

#step 1 mkdir 
Remove-Item -Path $dir_path -Force -recurse 
mkdir $dir_path
#�������ļ�file1.txt
$file_path =$dir_path+"\file.txt"
echo $testcase > $file_path 
#copyͼƬ�ļ�
copy-item $xmlpath\..\testxattr_r.bmp -destination $dir_path
$file_path_xattr_r = $dir_path+"\testxattr_r.bmp"

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


#����u1 acl
$objGroup =  $ad_set+$test_user_u1
$colRights = [System.Security.AccessControl.FileSystemRights]"Read"
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow

$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl.AddAccessRule($objAce)

Set-Acl -Path $file_path -Aclobject $objAcl
Set-Acl -Path $file_path_xattr_r -Aclobject $objAcl
