#测试用例：DAC-STUC-SMBD-025
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-025"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"

$testuser=$test_user_u1

echo "=====$st_case====="

#测试设置文件夹dir1的权限
$objGroup =  $ad_set+$test_user_u1

$colRights = [System.Security.AccessControl.FileSystemRights]"Read"
#只有该文件夹
$InheritanceFlag=[System.Security.AccessControl.InheritanceFlags]::none
$PropagationFlag=[System.Security.AccessControl.PropagationFlags]::none

$objType=[System.Security.AccessControl.AccessControlType]::Allow
$objAce=New-Object System.Security.AccessControl.FileSystemAccessRule($objGroup,$colRights,$InheritanceFlag,$PropagationFlag,$objType)
$objAcl = Get-Acl $dir_path
$objAcl.ResetAccessRule($objAce)

Set-Acl -Path $dir_path -Aclobject $objAcl
$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser Set-Acl $dir_path"  
}

#整个testcase是否成功
if(!$result_1)
{    
    echo "testcase $st_case all success"
    $test_sucess=$test_sucess+1 
}
else
{
    echo "testcase $st_case failed"
    $test_failed=$test_failed+1
}
$xmldoc.path_info.test_sucess=[string]$test_sucess
$xmldoc.path_info.test_failed=[string]$test_failed
$xmldoc.Save("$xmlpath\..\pathinfo.xml")
