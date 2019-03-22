#测试用例：DAC-STUC-SMBD-043
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u2=$xmldoc.path_info.test_user_u2
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-043"
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$dir_path_1=$dir_path+"\dir1"
$dir_path_2=$dir_path_1+"\d1"
$file_path=$dir_path_1+"\file.txt"
$testuser=$test_user_u2

#用户创建的文件只有读的权限
echo "=====$st_case====="

#1.测试允许列出文件夹内容
dir $dir_path_1 > $xmlpath\..\tmp
$result_1 = $?
if ($result_1)
{    
    echo "testcase $st_case allowed List success"
}
else
{
    echo "testcase $st_case allowed List failed"
    echo "failed from $test_user_u2 allowed List failed $dir_path_1."   
}

#2.测试在该子文件夹内创建子文件失败
New-Item $file_path -Force -ItemType file > $xmlpath\..\tmp
$result_2 = $?
if ($result_2)
{  
    echo "testcase $st_case denied create file failed"
    echo "failed from $test_user_u2 denied create file failed $file_path."
}
else
{
    echo "testcase $st_case denied create file success"
}

#3.测试在该子文件夹内创建子文件夹失败
New-Item $dir_path_2 -Force -ItemType directory > $xmlpath\..\tmp
$result_3 = $?
if ($result_3)
{  
    echo "testcase $st_case denied create directory failed"
    echo "failed from $test_user_u2 denied create directory failed $dir_path_2."
}
else
{
    echo "testcase $st_case denied create directory success"
}
 

#4. 如果List成功，而创建文件和文件夹失败，则该测试用例通过
if($result_1  -and !$result_2 -and !$result_3)
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
