#����������DAC-STUC-SMBD-033
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-033"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"

$testuser=$test_user_u1

echo "=====$st_case====="

#test
#���ļ�дȨ��
#׷��д���ļ�file_1.txt 
$file_1= $dir_path+"\file_1.txt"
echo "append file_1" >> $file_1
$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser append $file_1"  
}
#�ļ���дȨ�� 
#����$dir_path���ļ�file_2.txt 
$file_2= $dir_path+"\file_2.txt"
echo file_2 > $file_2
$result_2=$?
if ($result_2)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser create $file_2"  
}
#���ļ���дȨ��
#����$dir_path���ļ�file_3.txt 
$dir_sub1= $dir_path+"\dir_sub1"
$file_3= $dir_sub1+"\file_3.txt"
echo file_3 > $file_3
$result_3=$?
if (!$result_3)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser create $file_3"  
}

#����testcase�Ƿ�ɹ�
if(!$result_1  -and $result_2 -and !$result_3)
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
