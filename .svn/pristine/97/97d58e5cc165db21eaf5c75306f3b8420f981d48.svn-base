#!/usr/bin/python
# -*- conding:utf-8 -*-

import utils_path
import remote

windows_host_ip = '10.2.41.229'
port = '8000'
win_host = ('%s:%s' % (windows_host_ip, port))
def test():
	vdb_test = remote.Remote(uri=win_host)
	case_name = '3-20-01-01'
	vdb_test.run_keyword('init_log',kwargs={'case_sn':case_name})
	vdb_conf = vdb_test.run_keyword('gen_vdb_conf', kwargs={'range_size':'(0,100M)','maxdata':'1G','xfersize':'(4k,80,16k,20)','iorate':'200'})
	rc1 = vdb_test.run_keyword('run_vdb', kwargs={'case_sn':case_name,'vdb_conf':vdb_conf,'jn_jro':'jn','time':100})
	rc2 = vdb_test.run_keyword('run_vdb', kwargs={'case_sn':case_name,'vdb_conf':vdb_conf,'jn_jro':'jro','time':90})
test()
