#测试用例：DAC-STUC-SMBD-040
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-040"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"
$testuser=$test_user_u1

#用户创建的文件只有读的权限
echo "=====$st_case====="

#1.在该目录下创建文件
New-Item $file_path -Force -ItemType file > $xmlpath\..\tmp

#2.测试R权限
type $file_path > $xmlpath\..\tmp
$result_1 = $?
if ($result_1)
{    
    echo "testcase $st_case allow R success"
}
else
{
    echo "testcase $st_case allowed Read failed"
    echo "failed from $testuser Read failed $file_path."   
}

#3.测试W权限
echo "1 " >> $file_path
$result_2 = $?
if ($result_2)
{  
    echo "testcase $st_case denied Write failed"
    echo "failed from $testuser Write failed $file_path."
}
else
{
    echo "testcase $st_case denied Write success"
}

#4. 如果读成功，而写失败，则该测试用例通过
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
