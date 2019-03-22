#测试用例：DAC-STUC-SMBD-027
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-027"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\du.exe"

$testuser=$test_user_u1

echo "=====$st_case====="

#test execute du.exe
#$file_path > $xmlpath\..\tmp
$ad_set=$xmldoc.path_info.ad_set
$pwd_u1=$xmldoc.path_info.pwd_u1

#以指定用户u1启动powershell,并进行测试
$username=$ad_set+$test_user_u1
$userpasswd=ConvertTo-SecureString $pwd_u1 -AsPlainText -force
$cred=New-Object System.Management.Automation.PSCredential($username,$userpasswd)
Start-Process -FilePath $file_path -Credential $cred -NoNewWindow -Wait  > $xmlpath\..\tmp

$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser execute $file_path"  
}

#整个testcase是否成功
if (!$result_1)
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
