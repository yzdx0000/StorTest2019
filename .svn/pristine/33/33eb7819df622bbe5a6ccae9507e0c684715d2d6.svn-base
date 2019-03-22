#测试用例：DAC-STUC-SMBD-042
$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")


$net_driver_path=$xmldoc.path_info.net_driver_path
$st_case="DAC-STUC-SMBD-042"
$ad_set=$xmldoc.path_info.ad_set
$dir_path=$net_driver_path+$st_case
#$dir_path="D:\"+$st_case
$file_path=$dir_path+"\file.txt"

#使用u1用户在该目录下创建文件file.txt
New-Item $file_path -Force -ItemType file > $xmlpath\..\tmp


