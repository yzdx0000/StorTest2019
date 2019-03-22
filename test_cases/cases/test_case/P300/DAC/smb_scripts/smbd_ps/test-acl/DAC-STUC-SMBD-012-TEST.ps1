#测试用例：DAC-STUC-SMBD-012
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$test_user_u1=$xmldoc.path_info.test_user_u1
$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed

$st_case="DAC-STUC-SMBD-012"
$dir_path=$net_driver_path+$st_case

$testuser=$test_user_u1
echo "=====$st_case====="

#test DAC-STUC-SMBD-012 
#attrib $dir_path > $xmlpath\..\tmp
get-item $dir_path > $xmlpath\..\tmp
$result_1=$?
if ($result_1)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser attrib $dir_path"  
}
#dir $dir_path > $xmlpath\..\tmp
Get-ChildItem $dir_path > $xmlpath\..\tmp
$result_2=$?
if ($result_2)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser dir $dir_path"  
}

get-acl $dir_path > $xmlpath\..\tmp
$result_3=$?
if ($result_3)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser get-acl $dir_path"  
}

#读取扩展属性
#ads 不是扩展属性
<#
get-Content -Path $dir_path -Stream ads > $xmlpath\..\tmp
$result_4=$?
if ($result_4)
{    
    echo "$st_case test success"
}
else
{
    echo "$st_case test failed"
    echo "failed from $testuser get-Content -Path $dir_path -Stream ads"  
}
#>

#整个testcase是否成功
#if($result_1  -and $result_2 -and $result_3 -and $result_4)
if($result_1  -and $result_2 -and $result_3)
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

