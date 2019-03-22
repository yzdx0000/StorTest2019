import os
import subprocess

dir = 'C:\\Users\\Administrator\\Desktop\\pythoncode\\test_cases'
os.chdir(dir)
cmd = 'ls'
rc,stdout = subprocess.getstatusoutput(cmd)

with open('test', 'a+') as fw:
    fw.write(stdout)