#测试用例：DAC-STUC-SMBD-041
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-041"
$dir_path=$net_driver_path+$st_case
$dir_path_1=$dir_path+"\1"
$file_path=$dir_path_1+"\file.txt"

#用户创建的文件只有读的权限
echo "=====$st_case====="

#1.在该目录下创建夹
mkdir $dir_path_1 > $xmlpath\..\tmp

#2.测试L权限
dir $dir_path_1 
$result_1 = $?
if ($result_1)
{    
    echo "testcase $st_case allow list success"
}
else
{
    echo "testcase $st_case allowed list failed"
    echo "failed from test_user_u1 list failed $dir_path_1."   
}

#3.测试在该子文件夹下是否可创建文件
New-Item $file_path -Force -ItemType file
$result_2 = $?
if ($result_2)
{  
    echo "testcase $st_case denied create file failed"
    echo "failed from test_user_u1 denied create file failed $file_path."
}
else
{
    echo "testcase $st_case denied create file success"
}

#4.测试在该子文件夹下是否可创建文件夹
cd $dir_path_1
mkdir 2
$result_3 = $?
if (!$result_3)
{  
    echo "testcase $st_case denied create directory failed"
    echo "failed from test_user_u1 denied create directory failed $dir_path_1."
}
else
{
    echo "testcase $st_case denied create directory success"
}

#5. 如果遍历成功，而创建子文件和文件夹失败，则该测试用例通过
if($result_1  -and !$result_2 -and $result_3)
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
