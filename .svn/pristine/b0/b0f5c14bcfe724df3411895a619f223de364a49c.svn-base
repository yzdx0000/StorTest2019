#测试用例：DAC-STUC-SMBD-026
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-026"
$dir_path=$net_driver_path+$st_case
$testuser=$test_user_u1

echo "=====$st_case====="

#获取在dir1下面创建的文件file1、子文件夹dir_sub1
$file_path=$dir_path+"\file.txt"
$dir_sub= $dir_path+"\dir_sub1"

#在dir1下面删除文件file1
remove-item -path $file_path -force
$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser remove-item $file_path"  
}

#在dir1下面删除文件夹dir1_c1
remove-item -path $dir_sub -force
$result_2=$?
if (!$result_2)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser remove-item $dir_sub"  
}

#在dir1下面删除文件夹dir1_c1
remove-item -path $dir_path -force
$result_3=$?
if (!$result_3)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser remove-item $dir_path"  
}

#整个testcase是否成功
if(!$result_1  -and !$result_2 -and !$result_3)
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
