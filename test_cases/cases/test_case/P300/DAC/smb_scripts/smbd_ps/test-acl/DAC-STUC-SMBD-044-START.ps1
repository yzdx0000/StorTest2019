$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")
$ad_set=$xmldoc.path_info.ad_set
$test_user_u3=$xmldoc.path_info.test_user_u3
$pwd_u3=$xmldoc.path_info.pwd_u3

#以指定用户u3启动powershell,并进行权限测试
$username=$ad_set+$test_user_u3
$userpasswd=ConvertTo-SecureString $pwd_u3 -AsPlainText -force
$cred=New-Object System.Management.Automation.PSCredential($username,$userpasswd)
Start-Process powershell.exe -Credential $cred -NoNewWindow -Argumentlist "$xmlpath\DAC-STUC-SMBD-044-START.bat" -Wait
