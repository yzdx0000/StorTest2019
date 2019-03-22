#测试用例：DAC-STUC-SMBD-029
#设置扩展属性 未实现
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-029"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"
$file_path_xattr_r = $dir_path+"\testxattr_r.bmp"
$file_path_xattr_w = $dir_path+"\testxattr_w.bmp"

$testuser=$test_user_u1

echo "=====$st_case====="

#test
#设置扩展属性
[reflection.Assembly]::LoadWithPartialName("system.windows.forms") > $xmlpath\..\tmp
$image=New-Object System.Drawing.Bitmap($file_path_xattr_r)
$image.Save($file_path_xattr_w)
$result_xattr=$?
if (!$result_xattr)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser set xattr $file_path_xattr_w"  
}

echo $st_case >> $file_path
$result_1=$?
if (!$result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser write $file_path"  
}

#属性暂不支持拒绝
#attrib +h $file_path 
#$result_2=$?
#if (!$result_2)
#{    
#    echo "$st_case test success"
#}
#else
#{
#    echo "$st_case test failed"
#    echo "failed from $testuser attrib +h $file_path"  
#}

#整个testcase是否成功
#if(!$result_1  -and !$result_2 -and !$result_xattr)
if(!$result_1 -and !$result_xattr)
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
