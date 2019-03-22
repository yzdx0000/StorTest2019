# -*-coding:utf-8 -*
import os
import sys
import threading
import time
import logging
import traceback

import utils_path
import get_config
import common
import tool_use

vdbench_nas_log = None

def run_func(func):
    """
    打印错误日志
    """
    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            vdbench_nas_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)
    return _get_fault

def log_init_vdbench(case_log_path):
    """
    日志解析
    """
    global vdbench_nas_log

    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    log_file_name = now_time + '_' + file_name + '.log'
    log_file_path = os.path.join(case_log_path, log_file_name)
    print log_file_path

    vdbench_nas_log = logging.getLogger(name='vdbench_nas_log')
    vdbench_nas_log.setLevel(level = logging.INFO)

    handler = logging.FileHandler(log_file_path, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    vdbench_nas_log.addHandler(console)
    vdbench_nas_log.addHandler(handler)

    return


class VdbenchNasTest(object):
    def __init__(self, case_log_path, casename):
        log_init_vdbench(case_log_path)
        vdbench_nas_log.info("********** 初始化 vdbench_nas_log ************")

        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 30
        self.thread_lst = []
        self.casename = casename

    @run_func
    def start(self, ):

        self.thread_lst = []
        th = threading.Thread(target=self.start_nas,
                              args=(self.casename,))
        self.thread_lst.append(th)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    @run_func
    def stop(self):
        vdbench_nas_log.info("===============stop vdbench==============")
        self.stop_nas()

    @run_func
    def is_running(self):
        """返回线程是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    '''
    @run_func
    def check_in_loop(self, casename, vdb_flag):
        
        while True:
            if self.start_flag is False:
                self._running_flag = False
                break
            rc = self.start_nas(casename, vdb_flag)
            if rc != 0:
                self._running_flag = False
                break
            time.sleep(30)
        
        rc = self.start_nas(casename, vdb_flag)
        if rc != 0:
            vdbench_nas_log.error("vdbench stop in abnormal!")
        vdbench_nas_log.info("vdbench process is stopped")
        self._running_flag = False
    '''

    @run_func
    def stop_nas(self):
        cmd = 'ps -ef |grep "vdbench" | grep -v "python" | grep -v "grep" | awk \'{print $2}\' | xargs kill -9'
        common.run_command_shot_time(cmd)
        vdbench_nas_log.info("kill all vdbench process")
        self._running_flag = False

    @run_func
    def run_vdbench(self,
                    casename,
                    vdbflagname,
                    anchor_path,
                    journal_path,
                    ip,
                    jn_check_internal_step,
                    jn_map_storage_time,
                    elapsed = None,
                    output_path = None,
                    operations = None,
                    format = None,
                    threads = None,
                    depth = None,
                    width = None,
                    files = None,
                    size = None,
                    xfersize = None):
        obj_vdb = tool_use.Vdbenchrun(elapsed = elapsed,
                                      output_path = output_path,
                                      operations = operations,
                                      format = format,
                                      threads = threads,
                                      depth = depth,
                                      width = width,
                                      files = files,
                                      size = size,
                                      xfersize = xfersize)
        obj_vdb.run_create_and_operations_jn(casename, anchor_path, journal_path,
                                             vdbflagname, jn_check_internal_step,
                                             jn_map_storage_time, ip)


    @run_func
    def start_nas(self, casename):
        """
        :author:  lyzhb
        :date: 2018.01.15
        :description: 把_set_create_and_check_file生成的文件进行vdbench运行
        :param filename: 脚本名称，这个是vdbenchdayinlog用的
        :param vdbflagname:vdbench形成的配置文件的名称
        :param  vdb_flag:  vdbench运行的配置文件的文件大小标志
                            可以有三个值：'big'，'small'.'bigAndSmall','middle','other'
                            当该值为前四个时，threads,depth,width,files,size有默认值
        """

        vdbench_nas_log.info("********** 获取参数 ************")
        # 获取 nas_vdbench 参数
        nas_vdbench_param = get_config.get_nas_vdbench_param()
        nas_vdbflagname = nas_vdbench_param['vdbflagname']
        nas_vdb_flag = nas_vdbench_param['vdb_flag']
        nas_anchor_path = nas_vdbench_param['anchor_path']
        nas_journal_path = nas_vdbench_param['journal_path']
        nas_ip = nas_vdbench_param['ip']
        nas_elapsed = int(nas_vdbench_param['elapsed'])
        # nas_output_path = nas_vdbench_param['output_path']
        nas_operations = nas_vdbench_param['operations']
        nas_format = nas_vdbench_param['format']
        nas_threads = int(nas_vdbench_param['threads'])
        nas_depth = int(nas_vdbench_param['depth'])
        nas_width = int(nas_vdbench_param['width'])
        nas_files = int(nas_vdbench_param['files'])
        nas_size = nas_vdbench_param['size']
        nas_xfersize = nas_vdbench_param['xfersize']
        nas_jn_check_internal_step = nas_vdbench_param['jn_check_internal_step']
        nas_jn_map_storage_time = nas_vdbench_param['jn_map_storage_time']
        print nas_anchor_path


        # 获取vdbench输出目录
        outputname = casename + '_' + nas_vdbflagname + 'output'
        vdbench_log_path = utils_path.vdbench_log_path
        vdbench_output_path = os.path.join(vdbench_log_path, outputname)
        vdbench_nas_log.info('vdbench_output_path: ' + vdbench_output_path)
        nas_output_path = vdbench_output_path

        if nas_vdb_flag == 'small':
            self.run_vdbench(casename,
                             nas_vdbflagname,
                             nas_anchor_path,
                             nas_journal_path,
                             nas_ip,
                             nas_jn_check_internal_step,
                             nas_jn_map_storage_time,
                             elapsed=3600000,
                             output_path=nas_output_path,
                             operations='(read,write)',
                             format='yes',
                             threads=30,
                             depth=5,
                             width=10,
                             files=5,
                             size='(1k,10,3k,10,500k,10,4k,10,111k,10,8k,10,2k,10,800k,5,16k,10,64k,10,128k,5)',
                             xfersize='1k')

        elif nas_vdb_flag == 'big':
            self.run_vdbench(casename,
                             nas_vdbflagname,
                             nas_anchor_path,
                             nas_journal_path,
                             nas_ip,
                             nas_jn_check_internal_step,
                             nas_jn_map_storage_time,
                             elapsed=3600000,
                             output_path=nas_output_path,
                             operations='(read,write)',
                             format='yes',
                             threads=20,
                             depth=4,
                             width=10,
                             files=10,
                             size='(1m,40,4m,30,10m,20,100m,10)',
                             xfersize='4k')

        elif nas_vdb_flag == 'middle':
            self.run_vdbench(casename,
                             nas_vdbflagname,
                             nas_anchor_path,
                             nas_journal_path,
                             nas_ip,
                             nas_jn_check_internal_step,
                             nas_jn_map_storage_time,
                             elapsed=1000,
                             output_path=nas_output_path,
                             operations='(read,write)',
                             format='yes',
                             threads=20,
                             depth=2,
                             width=5,
                             files=200,
                             size='(1000k,10,800k,10,500k,20,1500k,10,2m,20,10m,10,5m,10,8m,10)',
                             xfersize='4k')
        else:
            self.run_vdbench(casename,
                             nas_vdbflagname,
                             nas_anchor_path,
                             nas_journal_path,
                             nas_ip,
                             nas_jn_check_internal_step,
                             nas_jn_map_storage_time,
                             elapsed=nas_elapsed,
                             output_path=nas_output_path,
                             operations=nas_operations,
                             format=nas_format,
                             threads=nas_threads,
                             depth=nas_depth,
                             width=nas_width,
                             files=nas_files,
                             size=nas_size,
                             xfersize=nas_xfersize)
        '''
        启动vdbench后要不断探测vdbench有没有结束，
        检测方法是到vdbench的输出中查status文件中是否有“Shutting down slaves”这句话
        '''
        # vdbench_output_path = '/home/vdb_config/output0217'
        vdbenchstatus = os.path.join(vdbench_output_path, 'status.html')
        vdbenchresult = os.path.join(vdbench_output_path, 'logfile.html')
        vdbench_error = os.path.join(vdbench_output_path, 'errorlog.html')

        # 根据vdbench输出判断结果
        vdbench_nas_log.info('vdbench  %s is stop' % vdbenchstatus)
        cmd1 = 'tail -10 %s ' % vdbenchresult
        vdbench_nas_log.info('cmd is %s' % cmd1)
        rc1, output1 = common.run_command_shot_time(cmd1)
        cmd2 = 'tail -5 %s ' % vdbench_error
        vdbench_nas_log.info('cmd is %s' % cmd2)
        rc2, output2 = common.run_command_shot_time(cmd2)

        if output1.find("completed successfully") < 0:
            vdbench_nas_log.error('vdbench %s completed error')
            vdbench_nas_log.info("=============logfile.html===============")
            vdbench_nas_log.error(output1)
            vdbench_nas_log.info("=============errorlog.html===============")
            vdbench_nas_log.error(output2)
            self._return_value = False
        else:
            vdbench_nas_log.info('vdbench %s completed successfully')

        # 不管vdbench 是正常结束还是异常结束，把_running_flag 置为 False
        self._running_flag = False
        return


@run_func
def main():
    case_log_path = '/home/StorTest/test_cases/log/case_log/test'
    # log_init_vdbench(case_log_path)
    casename = '30-0-0-1'
    vdb_test = VdbenchNasTest(case_log_path, casename)

    vdb_test.start()
    for i in range(10):
        vdbench_nas_log.info("======check times: %s========" % i)
        vdbench_nas_log.info("running flag: %s" % vdb_test.is_running())
        time.sleep(30)

    vdb_test.stop()
    while True:
        vdbench_nas_log.info("running flag: %s" % vdb_test.is_running())
        time.sleep(30)

if __name__=="__main__":
    common.case_main(main)

