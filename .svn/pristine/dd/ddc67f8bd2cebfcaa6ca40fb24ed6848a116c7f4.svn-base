# -*- coding:utf-8 -*-
#根据用例自动适配vdbench配置文件
#分单类型IO与混合类型IO两种情况配置

import iscsi_conf
import os
import log

#本次执行vdbench参数配置
case_list = 'test'
case_run_time = '1200'
iorate = '150'
threads = '16'
range_size = '(0,100M)'
maxdata = '2G'
iscsi_conf.iSCSI_login()
disk_idlist = iscsi_conf.conf_X1000_disk()

# 自动适配Lun个数，修改配置文件

def conf_vdb_para():
    curr_dir=os.path.dirname(__file__)
    caselist_dir=curr_dir+'\\case_lists'
    new_conf = 'rd=run1,wd=wd*,iorate=' + iorate + ',elapsed=' + case_run_time \
               + ',maxdata='+maxdata+',threads=' + threads + ',interval=1'
    print(os.path.exists(caselist_dir))
    os.chdir(caselist_dir)
    with open(case_list,'r') as listr:
        all_cases=listr.readlines()

    #打印所有本次需要执行的用例
    case_dir=curr_dir+'\\test_cases'
    os.chdir(case_dir)
    print('The test will run these cases...')
    for line in all_cases:
        if '#' in line or '*' in line or line.strip() == '':
            continue
        else:
            print(line.strip())
    # 自动配置vdbench脚本
    for case in all_cases:
        case=case.strip()
        # 过滤注释标记的用例
        if '#' in case or '*' in case or case == '':
            continue
        else:
            case_jd = case.split('-')
            if int(case_jd[1]) <= 8:
                # 执行单类型基础业务1-01到1-08
                # 删除原有的sd参数配置与wd参数配置
                with open(case, 'r') as case_update:
                    lines = case_update.readlines()
                with open(case, 'w') as case_update:
                    for line in lines:
                        if 'lun=' in line or ('wd=wd' in line and 'sd=sd' in line):
                            continue
                        case_update.write(line)

                # 根据磁盘ID自动配置到vdbench脚本
                with open(case, 'r') as case_update:
                    newlines = case_update.readlines()
                with open(case, 'w') as case_update:
                    for line in newlines:
                        case_update.write(line)
                        if 'sd=default' in line:
                            for count in disk_idlist:
                                sd_line = 'sd=sd' + count + ',lun=\\\.\PhysicalDrive' + count + ',range='+range_size+'\n'
                                case_update.write(sd_line)
                        elif 'wd=default' in line:
                            for count in disk_idlist:
                                wd_line = 'wd=wd' + count + ',sd=sd' + count + '\n'
                                case_update.write(wd_line)

                # 将顶端新的配置写到vdbench配置文件中
                with open(case, 'r') as case_read:
                    data = case_read.readlines()
                with open(case, 'w') as case_write:
                    for line in data:
                        if 'iorate' in line or 'elapsed' in line or 'threads' in line:
                            line = line.replace(line, new_conf)
                        case_write.write(line)
            else:
                # 执行混合类型的业务1-09以后，盘符数量必须至少两个
                # 判断盘符数量是否至少两个
                if len(disk_idlist) < 2:
                    print('错误！至少需要两个Lun才能执行这类用例！！！')
                    os._exit(1)

                # 获取配置文件中的关键配置参数存入列表
                with open(case, 'r') as case_read:
                    case_data = case_read.readlines()
                xfersize_count = 0
                xfersize_list = []
                for sd_conf in case_data:
                    if 'wd=wd' in sd_conf and 'sd=sd' in sd_conf:
                        sd_list = sd_conf.split('xfersize')
                        xfersize_info = 'xfersize' + sd_list[1]
                        xfersize_list.append(xfersize_info)
                        xfersize_count += 1
                        if xfersize_count == 2:
                            break
                # 将原有的配置清除，配置文件初始化
                with open(case, 'w') as case_clear:
                    for case_line in case_data:
                        if 'sd=sd' in case_line or 'range' in case_line:
                            continue
                        case_clear.write(case_line)

                # 根据Lun的个数自动修改配置文件
                with open(case, 'r') as case_read:
                    new_case_date = case_read.readlines()
                with open(case, 'w') as case_update:
                    for case_line in new_case_date:
                        case_update.write(case_line)
                        if 'sd=default' in case_line:
                            jud = 0
                            for count in disk_idlist:
                                sd_line = 'sd=sd' + count + ',lun=\\\.\PhysicalDrive' + count + ',range=' + range_size +'\n'
                                case_update.write(sd_line)
                            for count in disk_idlist:
                                wd_line = 'wd=wd' + count + ',sd=sd' + count + ',' + xfersize_list[jud % 2]
                                case_update.write(wd_line)
                                jud += 1

                # 将最后一行的参数配置写入配置文件
                with open(case, 'r') as case_read:
                    data = case_read.readlines()
                with open(case, 'w') as case_write:
                    for line in data:
                        if 'iorate' in line and 'elapsed' and line or 'threads' in line:
                            line = line.replace(line, new_conf)
                        case_write.write(line)


