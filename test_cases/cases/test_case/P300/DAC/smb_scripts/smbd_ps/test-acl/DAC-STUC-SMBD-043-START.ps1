﻿$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")
$ad_set=$xmldoc.path_info.ad_set
$test_user_u1=$xmldoc.path_info.test_user_u1
$pwd_u1=$xmldoc.path_info.pwd_u1
$test_user_u2=$xmldoc.path_info.test_user_u2
$pwd_u2=$xmldoc.path_info.pwd_u2

#以指定用户u1启动powershell,创建文件夹dir1
$username=$ad_set+$test_user_u1
$userpasswd=ConvertTo-SecureString $pwd_u1 -AsPlainText -force
$cred=New-Object System.Management.Automation.PSCredential($username,$userpasswd)
Start-Process powershell.exe -Credential $cred -NoNewWindow -Argumentlist "$xmlpath\DAC-STUC-SMBD-043-START-U1.bat" -Wait

#以指定用户u2启动powershell,并进行权限测试
$username=$ad_set+$test_user_u2
$userpasswd=ConvertTo-SecureString $pwd_u2 -AsPlainText -force
$cred=New-Object System.Management.Automation.PSCredential($username,$userpasswd)
Start-Process powershell.exe -Credential $cred -NoNewWindow -Argumentlist "$xmlpath\DAC-STUC-SMBD-043-START-U2.bat" -Wait