from robotremoteserver import RobotRemoteServer as Rs
import os
import subprocess
import datetime
import time
import utils_path
import iscsi_conf
import log

os.system('chcp 65001')

class run_vdbench():
    # 测试连接
    def test_connect(self):
        log.info("the linux host is connected with windows host!")
        return 0

    # 初始化日志
    def init_log(self, case_sn = None):
        log_file_path = log.get_log_path() + '_' + case_sn + '.log'
        log.init(log_file_path, True)

    # 生成vdbench配置文件，返回vdbench配置文件路径
    def gen_vdb_conf(self,range_size='(0,100M)', maxdata='2G', xfersize='(4k,100)',
                     seekpct='0', rdpct='0', iorate='100', threads='16', run_time='900', offset=None, align=None):
        # login,获取卷信息
        iscsi_conf.iSCSI_login()
        disk_id_list = iscsi_conf.conf_X1000_disk()
        log.info('test disk id list is:%s' % disk_id_list)
        # 进入vdbench目录，准备生成vdb配置文件
        win_lib_dir = os.getcwd()
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        vdbench_dir = current_dir + '\\vdbench'
        vdb_conf_dir = current_dir + '\\vdb_conf_dir'
        journal_dir = current_dir + '\\journal'
        if not os.path.exists(vdbench_dir):
            log.error('Error!the vdbench is not exists!!!')
            os._exit(1)
        if not os.path.exists(journal_dir):
            os.mkdir(journal_dir)
        if not os.path.exists(vdb_conf_dir):
            os.mkdir(vdb_conf_dir)
        os.chdir(vdb_conf_dir)
        vdb_top_line = ('sd=default,journal=%s' % journal_dir)
        # 判断是否有offset或者align参数
        if '' != offset and '' == align:
            vdb_top_line = vdb_top_line + ',offset=' + offset
        elif '' == offset and '' != align:
            vdb_top_line = vdb_top_line + ',align=' + align
        elif '' != offset and '' != align:
            vdb_top_line = vdb_top_line + ',offset=' + offset + ',align=' + align
        vdb_mid_line = ('wd=default,xfersize=%s,rdpct=%s,seekpct=%s' % (xfersize, rdpct, seekpct))
        vdb_end_line = ('rd=run1,wd=wd*,iorate=%s,elapsed=%s,maxdata=%s,threads=%s,interval=1'
                        % (iorate, run_time, maxdata, threads))
        # 生成vdbench配置文件
        while True:
            curtime = time.time()
            curtime = str(round(curtime%10000, 3))
            curtime_list = curtime.split('.')
            curtime = curtime_list[0] + curtime_list[1]
            vdb_conf_name = 'vdb_conf' + curtime
            if not os.path.exists(vdb_conf_name):
                break
        with open(vdb_conf_name, 'w') as vdb_conf:
            # 写入sd配置参数
            vdb_conf.write(vdb_top_line+'\n')
            for disk_id in disk_id_list:
                sd_line = ('sd=sd%s,lun=\\\.\PhysicalDrive%s,range=%s' % (disk_id, disk_id, range_size))
                vdb_conf.write(sd_line + '\n')
            # 写入wd配置参数
            vdb_conf.write(vdb_mid_line+'\n')
            for disk_id in disk_id_list:
                wd_line = ('wd=wd%s,sd=sd%s' % (disk_id, disk_id))
                vdb_conf.write(wd_line + '\n')
            # 写入最后一行参数配置
            vdb_conf.write(vdb_end_line)
        vdb_conf_path = vdb_conf_dir + '\\' + vdb_conf_name
        os.chdir(win_lib_dir)
        return vdb_conf_path

    def run_vdb(self, case_sn=None, vdb_conf=None, jn_jro=None, time=None):
        if vdb_conf == None:
            log.error('Error!vdbench conf path is not exsits!')
            os._exit(1)
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        vdbench_dir = current_dir + '\\vdbench'
        output_dir = current_dir + '\\output'
        if not os.path.exists(vdbench_dir):
            log.error('Error!the vdbench is not exists!!!')
            os._exit(1)
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        run_cmd = ('%s\\vdbench.bat -f %s' % (vdbench_dir, vdb_conf))
        if time != None:
            run_cmd = run_cmd + ' -e ' + str(time)
        if jn_jro != None and jn_jro != 'no':
            with open(vdb_conf, 'r') as vdb_read:
                lines = vdb_read.readlines()
                for line in lines:
                    if 'offset' in line or 'align' in line:
                        log.error('jn or jro conflicts with offset and align!!!')
                        return -1
            run_cmd = run_cmd + ' -' + jn_jro
        run_cmd = run_cmd + ' -o ' + current_dir + '\\vdb_output'
        log.info(run_cmd)
        rc = os.system(run_cmd)
        if rc != 0:
            log.error('Error!run vdbench failed!!!')
            return 1
        else:
            log.error('vdbench execute successful!!!')
            return 0

    def kill_win_vdb(self):
        cmd_task = 'tasklist'
        (rc, stdout) = subprocess.getstatusoutput(cmd_task)
        if 0 == rc:
            log.info('get windows process info successful.')
            result = stdout.split('\n')
            for line in result:
                if 'java.exe' in line:
                    cmd = 'taskkill /im java.exe /f'
                    log.info('Kill vdbench process in windows.')
                    rc = os.system(cmd)
                    if 0 == rc:
                        log.info('Kill vdbench process in windows successful!')
                        return 0
                    else:
                        log.error('Kill vdbench process failed.try again!')
                        os.system(cmd)
            log.info('vdbench process in windows host is not found!')
        else:
            log.error('get windows process info failed!!!')
        iscsi_conf.ISCSI_logout()

    def upload_vdb_output(self, log_host_ip='10.2.43.227', vdb_dir=None):
        win_lib_dir = os.getcwd()
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        output_dir = current_dir + '\\vdb_output'
        winscp_path = 'C:\\Program Files (x86)\\WinSCP'
        os.chdir(winscp_path)
        with open('winscp_script', 'w+') as wt_script:
            cmd_task = 'option echo off\noption batch on\noption confirm off\n'
            wt_script.write(cmd_task)
            login_txt = ('open sftp://root:111111@%s:22\n' % log_host_ip)
            wt_script.write(login_txt)
            put_txt = ('cd %s\nput %s vdb_win_output\n' % (vdb_dir, output_dir))
            wt_script.write(put_txt)
            other_txt = 'option transfer binary\noption synchdelete off\nremote\nclose\nexit'
            wt_script.write(other_txt)

        #cmd = ("'%s' /console /script=winscp_script" % winscp_path)
        cmd = ".\\WinSCP.exe /console /script=winscp_script"
        rc = os.system(cmd)
        if 0 == rc:
            log.info("vdbench log in windows upload successful!!!")

        # 恢复原来目录
        os.chdir(win_lib_dir)

if __name__ == '__main__':
    instance = run_vdbench()
    Rs(instance, host='10.2.41.229', port=8010)
