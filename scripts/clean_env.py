#!/usr/bin/python

import os
import sys
import commands

client_ip = ['10.2.42.11','10.2.42.10']

cmd = 'ps aux | grep .*py$'
stdout=commands.getoutput(cmd)
py_name=os.path.abspath(__file__)
py_name = py_name.split('/').pop()
cmd =('ps aux | grep %s | grep -v grep | awk \'{print $2}\'' % py_name)
py_pid=commands.getoutput(cmd)
if stdout != '':
	std_ls = stdout.split()
	case_pid =  std_ls[1]
	if case_pid != py_pid:
		cmd = ('kill -9 %s' % case_pid)
		rc = os.system(cmd)
		if rc != 0:
			print ('kill case process failed!!!')
		else:
			print ('kill case process successful!!!')
	else:
		print ('the case is already dead!!!')	

for client in client_ip:
	cmd = ('ssh %s "systemctl restart iscsid"' % client)
	rc = os.system(cmd)
	if rc == 0:
		print ('The iscsid restart successful!')
	else:
		print ('The iscsied restart failed!')
	cmd = ('ssh %s "ps -aux | grep vdbench | grep -v grep" | awk \'{print $2}\'' % client)
	stdout = commands.getoutput(cmd)
	if stdout == '':
		print ('The client %s vdbench Process is not exsits already!' % client)
	else:
		vdb_pid = stdout.split('\n')
		for pid in vdb_pid:
			cmd = ('ssh %s "kill -9 %s"' % (client,pid))
			print cmd
			rc = os.system(cmd)
			if rc != 0:
				print ('vdbench Process killed failed!!!')
				os._exit(1)
		cmd = ('ssh %s "ps -aux | grep vdbench | grep -v grep"' % client)
		stdout = commands.getoutput(cmd)
		if stdout == '':
			print ('vdbench Process killed successful!!!')
		else:
			print ('vdbench killed ERROR!!!Please Check!!!')
	print ('logout all the client!!!')
	cmd1 = ('ssh %s "iscsiadm -m node -u"' % client)
	rc1 = os.system(cmd1)
	cmd2 = ('ssh %s "iscsiadm -m node -o delete"' % client)
	rc2 = os.system(cmd2)
	if rc1 != 0 or rc2 !=0:
		print ('logout failed or there is no login!!!')
	else:
		print ('logout client successful!!!')
