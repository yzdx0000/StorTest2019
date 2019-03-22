#测试用例：DAC-STUC-SMBD-042
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u2=$xmldoc.path_info.test_user_u2
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-042"
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"
$testuser=$test_user_u2

#用户u1创建的文件u2只有读的权限(u1与u2用户均为Domain Users)
echo "=====$st_case====="

#1.测试R权限允许
type $file_path > $xmlpath\..\tmp
$result_1 = $?
if ($result_1)
{    
    echo "testcase $st_case allowed Read success"
}
else
{
    echo "testcase $st_case allowed Read failed"
    echo "failed from $test_user_u2 allowed Read failed $file_path."   
}

#2.测试W权限被拒绝
echo "123" > $file_path
$result_2 = $?
if ($result_2)
{  
    echo "testcase $st_case denied write file failed"
    echo "failed from $test_user_u2 denied write file failed $file_path."
}
else
{
    echo "testcase $st_case denied write file success"
}

#3. 如果读成功，而写失败，则该测试用例通过
if($result_1  -and !$result_2)
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