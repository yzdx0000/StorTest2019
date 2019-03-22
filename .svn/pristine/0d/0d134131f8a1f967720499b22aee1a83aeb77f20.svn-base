#测试用例：DAC-STUC-SMBD-024
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$ad_set=$xmldoc.path_info.ad_set
$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-024"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"

$testuser=$test_user_u1

echo "=====$st_case====="

#设置文件夹dir1扩展属性 暂未实现

#设置属性暂时未实现
#设置文件夹dir1为属性为隐藏
#attrib +h $dir_path
#$result_1=$?
#if (!$result_1)
#{    
#    echo "$st_case test success"
#}
#else
#{
#    echo "$st_case test failed"
#    echo "failed from $testuser attrib $dir_path"  
#}

#在dir1下面创建文件file1
$file_path= $dir_path+"\file1.txt"
echo "test" > $file_path
$result_2=$?
if (!$result_2)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser write $file_path"  
}

#在dir1下面创建文件夹dir1_c1
$dir_sub= $dir_path+"\dir1_c1"
mkdir $dir_sub > $xmlpath\..\tmp
$result_3=$?
if ($result_3)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser mkdir $dir_sub"  
}

#整个testcase是否成功
if(!$result_2 -and $result_3)
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
