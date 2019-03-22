#测试用例：DAC-STUC-SMBD-031
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-031"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"

$testuser=$test_user_u1
echo "=====$st_case====="

#test
#改变所有者

#去掉“/”
$user_u1=$test_user_u1.Substring(1,$test_user_u1.length-1)
$objAcl = Get-Acl $file_path
$owner_new= New-Object System.Security.Principal.NTAccount($ad_set,$user_u1)
$objAcl.SetOwner($owner_new)
Set-Acl -Path $file_path -Aclobject $objAcl
$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser Set-Acl $file_path"  
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
