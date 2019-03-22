# -*- coding=utf-8 -*-
# 根据用例集合文件执行vdbench业务
# 将每条用例的结果都保存，并且统计Pass和fail

import vdb_conf
import iscsi_conf
import os
import shutil
import time
import log


#基础业务执行此脚本
#将vdbench目录存放在该项目路径
log_file_path = log.get_log_path()
log.init(log_file_path, True)

iscsi_conf.iSCSI_login()
disk_list=iscsi_conf.conf_X1000_disk()
log.info(disk_list)
vdb_conf.conf_vdb_para()
cur_dir=os.path.dirname(__file__)
run_case_list = []  # 用例存放列表

def run_casels_vdbench():
    #进入vdbench目录
    vdbench_dir=cur_dir+'\\vdbench'
    case_dir = cur_dir+'\\test_cases'
    vdb_log_dir=cur_dir+'\\vdb_output'
    if not os.path.exists(vdb_log_dir):
        os.mkdir(vdb_log_dir)
    os.chdir(vdb_log_dir)
    jnl_dir=vdb_log_dir+'\journal'
    if not os.path.exists(jnl_dir):
        os.mkdir(jnl_dir)
    with open('case_result.txt' ,'w+') as case_rec:
        title='CASE_LIST'+'\t'+'RESULT\t'+'OPTiME\n'
        case_rec.write(title)

    for count in run_case_list:
        os.chdir(vdbench_dir)
        #执行vdbench脚本
        print('The %s case will be running...' % count)
        cmd='vdbench.bat -f '+case_dir+'\\'+count
        print(cmd)
        start_time=time.time()
        rc = os.system(cmd)
        end_time=time.time()
        rum_time_min=(end_time-start_time)//60
        run_time_sec=(end_time-start_time)%60
        run_time = str(int(rum_time_min))+'m'+str(int(run_time_sec))+'s'

        #判断每次vdbench是否执行成功
        os.chdir(vdb_log_dir)
        if rc != 0:
            result=count+'\t'+'Failed\t'+run_time+'\n'
            with open('case_result.txt','a+') as case_rec:
                case_rec.write(result)
        else:
            result=count+'\t'+'Success\t'+run_time+'\n'
            with open('case_result.txt','a+') as case_rec:
                case_rec.write(result)

        # 将每个用例的vdb日志保存到指定目录
        vdb_dir = vdb_log_dir+'\\vdb_output'
        old_output = vdbench_dir + '\\output'
        new_output = vdb_dir + '_'+count
        if os.path.exists(new_output):
            os.remove(new_output)
        shutil.copytree(old_output, new_output)
        print('The %s case has been finished!!!\n' % count)
        time.sleep(3)

def get_cases():

    #从用例列表中获取需要执行的用例
    list_dir=cur_dir+'\\case_lists'
    os.chdir(list_dir)
    print(os.getcwd())
    with open(vdb_conf.case_list,'r') as case_read:
        cases=case_read.readlines()
    for line in cases:
        if '#' in line or '*' in line or line.strip() == '':
            continue
        else:
            run_case_list.append(line.strip())

def main():
    os.system('chcp 65001')
    get_cases()
    run_casels_vdbench()

if __name__ == '__main__':
    main()