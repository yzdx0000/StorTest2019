#测试用例：DAC-STUC-SMBD-052
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-052"
$ad_set=$xmldoc.path_info.ad_set
$testuser=$xmldoc.path_info.test_user_u4
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

#用户对文件只有读的权限
echo "=====$st_case====="

#1. 使用u1用户对文件写操作
echo "123" >> $file_path 
$result_1 = $?
if (!$result_1)
{    
    echo "testcase $st_case denied Write success"
}
else
{
    echo "testcase $st_case denied Write failed"
    echo "failed from $testuser denied Write failed $file_path."   
}

#3. 如果对u1的读拒绝成功，则该测试用例通过
if(!$result_1)
{
    $test_sucess=$test_sucess+1
    echo "$st_case all test success"
}
else
{
    $test_failed=$test_failed+1
    echo "$st_case failed"
}

$xmldoc.path_info.test_sucess=[string]$test_sucess
$xmldoc.path_info.test_failed=[string]$test_failed
$xmldoc.Save("$xmlpath\..\pathinfo.xml")




