#测试用例：DAC-STUC-SMBD-043
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")


$net_driver_path=$xmldoc.path_info.net_driver_path
$st_case="DAC-STUC-SMBD-043"
$ad_set=$xmldoc.path_info.ad_set
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$dir_path_1=$dir_path+"\dir1"

#使用u1用户在该目录下创建文件目录dir1
New-Item $dir_path_1 -Force -ItemType directory > $xmlpath\..\tmp


