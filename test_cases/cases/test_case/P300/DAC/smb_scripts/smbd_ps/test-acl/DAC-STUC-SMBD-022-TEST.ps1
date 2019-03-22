#����������
$st_case="DAC-STUC-SMBD-022"

$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed


$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"

$testuser=$test_user_u1

echo "=====$st_case====="

$file_path= $dir_path+"\file1.txt"
#test traverse dir
#type $file_path
#get-Content -Path $file_path
cd $dir_path
$result_1=$?
if ($result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser cd $dir_path"  
}

#����testcase�Ƿ�ɹ�
if ($result_1)
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