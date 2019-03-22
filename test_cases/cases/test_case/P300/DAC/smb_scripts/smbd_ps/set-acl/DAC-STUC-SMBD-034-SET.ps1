# �������  : DAC-STUC-SMBD-034
# ������Ŀ  : DAC-1.0-003-006
# ��������  : ��windowsĿ¼Ȩ��Ӧ�÷�ʽ��֧��002
# �������  : ֧���ļ���"���ļ��С����ļ��к��ļ�"Ȩ��Ӧ�÷�ʽ�����ã����ļ�����
#             ��Ȩ�ޣ����ļ������ļ��м̳�
#             ���ļ��еĸ�Ȩ��
# Ԥ������  : �����ļ��С����ļ������ļ���
# ��    ��  : �����ļ���дȨ�ޣ�Ȩ��Ӧ�÷�ʽΪ"���ļ��С����ļ��к��ļ�"
# ִ�в���  : 1.���û�administrator�������̣������ļ���dir1
#             2.����ļ���dir1�û�u1�������ļ���dir1�û�u1��дȨ�ޣ�Ȩ��Ӧ�÷�ʽ
#               Ϊ"���ļ��С����ļ��к��ļ�
#             3.����dir1�����ļ���dir2�����ļ�file1
#             4.���û�u1�������̣�����dir1���ļ�file2������dir2���ļ�file3��дdir
#               ���ļ�file1
# Ԥ�ڽ��  : ����4����file2��file3��дfile1�����ɹ�
# ��������  :
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

$testcase ="DAC-STUC-SMBD-034"
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


#set U1 �ļ���Ȩ������
$objGroup =  $ad_set+$test_user_u1
#�Բ�������Ӷ���ִ��Ȩ��
$colRights = [System.Security.AccessControl.FileSystemRights]"ExecuteFile,Read"
#�ļ��С����ļ��к��ļ�
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

#��Ӳ���дȨ��
$colRights = [System.Security.AccessControl.FileSystemRights]"Write"
#�ļ��С����ļ��к��ļ�
$InheritanceFlag='ObjectInherit,ContainerInherit'
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none
$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)

$objAcl.AddAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl


#����$dir_path���ļ���dir_sub1 
$dir_sub1= $dir_path+"\dir_sub1"
mkdir $dir_sub1

#����$dir_path���ļ�file_1.txt 
$file_1= $dir_path+"\file_1.txt"
echo file_1 >$file_1



