@echo off
rem 设置powershell脚本可执行脚本
powershell -command "&{Set-ExecutionPolicy -Scope  LocalMachine -ExecutionPolicy "unrestricted" -Force}"

del  /Q /S /F .\st_smbd_test_result.txt

:l_begin
powershell -file .\test-acl\DAC-STUC-SMBD-INIT.ps1
powershell -file .\set-acl\DAC-STUC-SMBD-SET_XML.ps1
echo    设置文件夹acl
echo "set acl begining..."
set testcase_begin=11
set testcase_end=46

FOR /L %%a IN (%testcase_begin%, 1, %testcase_end%) DO (
    powershell -file .\set-acl\DAC-STUC-SMBD-0%%a-SET.ps1
)

#powershell -file .\set-acl\DAC-STUC-SMBD-040-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-041-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-042-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-043-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-044-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-045-SET.ps1
#powershell -file .\set-acl\DAC-STUC-SMBD-046-SET.ps1
powershell -file .\set-acl\DAC-STUC-SMBD-051-SET.ps1
powershell -file .\set-acl\DAC-STUC-SMBD-052-SET.ps1
powershell -file .\set-acl\DAC-STUC-SMBD-053-SET.ps1

echo "Congratulations! set acl finshed!"

echo    测试文件夹acl

FOR /L %%a IN (%testcase_begin%, 1, %testcase_end%) DO (
    powershell -file .\test-acl\DAC-STUC-SMBD-0%%a-START.ps1
)

#powershell -file .\test-acl\DAC-STUC-SMBD-040-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-041-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-042-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-043-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-044-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-045-START.ps1
#powershell -file .\test-acl\DAC-STUC-SMBD-046-START.ps1
powershell -file .\test-acl\DAC-STUC-SMBD-051-START.ps1
powershell -file .\test-acl\DAC-STUC-SMBD-052-START.ps1
powershell -file .\test-acl\DAC-STUC-SMBD-053-START.ps1
powershell -file .\test-acl\DAC-STUC-SMBD-RESULT.ps1


rem 是否需要循环测试
rem goto l_begin 
