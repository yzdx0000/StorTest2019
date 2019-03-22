$xmlpath=Split-Path -Parent $MyInvocation.MyCommand.Definition
$xmldoc=New-Object XML
$xmldoc.Load("$xmlpath\..\pathinfo.xml")
$ad_set=$xmldoc.path_info.ad_set
#u4用户的主要组为sugon
$test_user_u4=$xmldoc.path_info.test_user_u4
$pwd_u4=$xmldoc.path_info.pwd_u4

#以指定用户u4启动powershell,并进行权限测试
$username=$ad_set+$test_user_u4
$userpasswd=ConvertTo-SecureString $pwd_u4 -AsPlainText -force
$cred=New-Object System.Management.Automation.PSCredential($username,$userpasswd)
Start-Process powershell.exe -Credential $cred -NoNewWindow -Argumentlist "$xmlpath\DAC-STUC-SMBD-046-START.bat" -Wait
