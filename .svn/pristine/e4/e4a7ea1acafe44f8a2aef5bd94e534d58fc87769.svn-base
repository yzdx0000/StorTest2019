#打印出结果，并将xml文件中保存的结果归零
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")

$net_driver_path=$xmldoc.path_info.net_driver_path
$test_sucess=[Int]$xmldoc.path_info.test_sucess
$test_failed=[Int]$xmldoc.path_info.test_failed
$test_total=$test_sucess+$test_failed

# 打印测试信息

echo "=========================================="  >> $xmlpath\..\st_smbd_test_result.txt
echo "TEST PATH:  $net_driver_path"                >> $xmlpath\..\st_smbd_test_result.txt
echo "TESTCASE TOTAL: $test_total."                >> $xmlpath\..\st_smbd_test_result.txt
echo "SUCCEEED: $test_sucess."                     >> $xmlpath\..\st_smbd_test_result.txt
echo "FAILED: $test_failed."                       >> $xmlpath\..\st_smbd_test_result.txt
echo "=========================================="  >> $xmlpath\..\st_smbd_test_result.txt

$xmldoc.path_info.test_sucess=[string]$test_sucess
$xmldoc.path_info.test_failed=[string]$test_failed
$xmldoc.Save("$xmlpath\..\pathinfo.xml")




