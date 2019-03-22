#-*- coding:utf8 -*-
import os
import sys
import json
import commands

list = os.listdir("/home/StorTest/test_cases/cases/test_case/X1000/basic_io") #列出文件夹下所有的目录与文件
thick_case=[]
for i in list:
    if "1-"  in i:
    #    continue

    #cmd=("cat {} |grep -i THIN".format(i))
    #res,final=commands.getstatusoutput(cmd)
    #if final:
        thick_case.append(i)
        with open("/home/StorTest/test_cases/cases/test_case/X1000/basic_io/thick_case_list","ab+") as f:
            f.write("/X1000/lun_manager/{}\n".format(i))

print thick_case
print len(thick_case)
        


