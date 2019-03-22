#测试用例：DAC-STUC-SMBD-051
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$net_driver_path=$xmldoc.path_info.net_driver_path
$ad_set=$xmldoc.path_info.ad_set
$testuser=$xmldoc.path_info.test_user_u1
$st_case="DAC-STUC-SMBD-051"
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

$test_temp=[Int]$xmldoc.path_info.test_temp

#用户对文件只有读的权限
echo "=====$st_case====="

#1. 使用u1用户对目录下的子文件读操作
type $file_path > $xmlpath\..\tmp
$result_1=$?
if ($?)
{    
    echo "testcase $st_case allowed $testuser Read success"
}
else
{
    echo "testcase $st_case allowed $testuser Read failed"
    echo "failed from $testuser allowed Read failed $file_path."   
}

#3. 如果读成功，而写失败，则该测试用例通过
if($result_1)
{
    $test_temp=1
}

$xmldoc.path_info.test_temp=[string]$test_temp
$xmldoc.Save("$xmlpath\..\pathinfo.xml")




