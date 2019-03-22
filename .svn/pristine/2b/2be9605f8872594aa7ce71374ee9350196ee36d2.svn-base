@echo off
set current_path=%~dp0
powershell -command "&{Set-ExecutionPolicy -Scope  Process  -ExecutionPolicy "unrestricted" -Force; %current_path%\DAC-STUC-SMBD-025-TEST.ps1 >> %current_path%/../st_smbd_test_result.txt}" 
