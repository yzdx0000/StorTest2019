# -*- coding:utf-8 -*-
#查看每次执行完后的结果统计

import os
import time
import vdb_conf
list_name=vdb_conf.case_list
def get_totals():
	cmd='chcp 65001'
	os.system(cmd)

	curr_dir=os.getcwd()
	log_dir=curr_dir+'\\vdbench'+'\\vdb_summary'
	list_dir=curr_dir+'\\vdbench'+'\\case_lists'
	vdb_dir=curr_dir+'\\vdbench'

	os.chdir(list_dir)
	with open(list_name,'r') as filer:
		case_ls=filer.readlines()

	nowtime=time.strftime('%Y-%m-%d')

	title='\t\t   '+nowtime+'\t'+'total_time\t  '+'IO_rate\t'+'MB/sec'+'  bytes  '+\
		  'r_pct  '+'res_time  '+'r_resp '+'  w_resp\t'+'resp_max  '+'resp_std\t'+\
		  'depth '+' cpu%  '+'cpu%\t'
	print(title)

	os.chdir(log_dir)
	for case_log in case_ls:
		case_log_name=case_log.strip()+'.log'
		if not os.path.exists(case_log_name):
			continue
		with open(case_log_name,'r') as logr:
			log_data=logr.readlines()
		for data in log_data:
			if 'avg' in data:
				line=case_log.strip()+' '+data.strip()
				print(line)
	print('')
	os.chdir(vdb_dir)
	with open('case_result.txt'
			,'r') as resultr:
		result_ls=resultr.readlines()
		for line in result_ls:
			print(line.strip())

if __name__=='__main__':
	get_totals()

