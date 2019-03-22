#测试用例：DAC-STUC-SMBD-051
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$net_driver_path=$xmldoc.path_info.net_driver_path
$test_temp=[Int]$xmldoc.path_info.test_temp
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-051"
$ad_set=$xmldoc.path_info.ad_set
$testuser=$xmldoc.path_info.test_user_u2
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

#用户对文件只有读的权限
#echo "=====$st_case====="

#1. 使用u2用户对目录下的子文件读操作
type $file_path > $xmlpath\..\tmp
$result_1 = $?
if ($result_1)
{    
    echo "testcase $st_case denied $testuser Read failed"
    echo "failed from $testuser denied Read failed $file_path."  
}
else
{
    echo "testcase $st_case denied $testuser Read success" 
}

#2. 如果u1读被允许，u2读被拒绝，则该测试用例通过
if($test_temp -and !$result_1)
{
    $test_sucess=$test_sucess+1
    echo "$st_case all test success"
}
else
{
    $test_failed=$test_failed+1
    echo "$st_case failed"
}

#3.回复标记，并保存
$test_temp=0
$xmldoc.path_info.test_temp=[string]$test_temp
$xmldoc.path_info.test_sucess=[string]$test_sucess
$xmldoc.path_info.test_failed=[string]$test_failed
$xmldoc.Save("$xmlpath\..\pathinfo.xml")




