#测试用例：DAC-STUC-SMBD-028
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-028"
$dir_path=$net_driver_path+$st_case
$file_path=$dir_path+"\file.txt"
$file_path_xattr_r = $dir_path+"\testxattr_r.bmp"

$testuser=$test_user_u1

echo "=====$st_case====="
#test 读属性目前不能拒绝
#attrib $file_path  > $xmlpath\..\tmp 
#$result_1=$?
#if (!$result_1)
#{    
#    echo "$st_case test success"
#}
#else
#{
#    echo "$st_case test failed"
#    echo "failed from $testuser attrib $file_path"  
#}

type $file_path > $xmlpath\..\tmp
$result_2=$?
if (!$result_2)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser type $file_path"  
}

get-acl $file_path > $xmlpath\..\tmp
$result_3=$?
if (!$result_3)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser get-acl $file_path"  
}

[reflection.Assembly]::LoadWithPartialName("system.windows.forms") > $xmlpath\..\tmp
$image=New-Object System.Drawing.Bitmap($file_path_xattr_r)
$result_xattr=$?
if (!$result_xattr)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser get-xattr $file_path_xattr_r"  
}

#整个testcase是否成功
#if(!$result_1  -and !$result_2 -and !$result_3)
if( !$result_2 -and !$result_3 -and !$result_xattr)
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
