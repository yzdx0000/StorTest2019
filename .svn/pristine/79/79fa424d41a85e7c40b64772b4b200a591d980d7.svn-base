# -*-coding:utf-8 -*
import os
import sys
import time
import threading
import logging
import traceback

import utils_path
import get_config
import common
import tool_use
import s3_common
import prepare_clean
import json
import commands

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    vdbench创建文件后，检查文件正确性
# @steps:
#    1、创建账户；
#    2、创建证书；
#    3、创建桶；
#    4、vdbench创建文件；
#    5、上传文件；
#    6、下载文件；
#    7、校验文件md5值；
#
# @changelogging：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]  # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"
email_lst = []
email_lst.append(ACCOUNT_EMAIL)
src_md5_path = '/tmp/src_md5_file'
src_md5_dic = {}
check_md5_dic = {}
s3data_log = None


def log_init_s3data(case_log_path):
    """
    日志解析
    """
    global s3data_log
    file_name = os.path.basename(__file__)
    file_name = file_name.split('.')[0]
    now_time = time.strftime('%Y-%m-%d-%H-%M-%S', time.localtime(time.time()))
    file_name = now_time + '_' + file_name + '.log'
    file_name = os.path.join(case_log_path, file_name)
    print file_name

    s3data_log = logging.getLogger(name='s3data_log')
    s3data_log.setLevel(level=logging.INFO)

    handler = logging.FileHandler(file_name, mode='a')
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    handler.setFormatter(formatter)

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG)
    formatter = logging.Formatter('[%(levelname)s][%(asctime)s]   %(message)s', '%y-%m-%d %H:%M:%S')
    console.setFormatter(formatter)

    s3data_log.addHandler(console)
    s3data_log.addHandler(handler)
    return


def run_func(func):
    """
    打印错误日志
    """

    def _get_fault(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception:
            s3data_log.error("", exc_info=1)
            traceback.print_exc()
            sys.exit(1)

    return _get_fault


@run_func
def cleaning_environment(account_email_lst):
    """
    :author:                  baourobing
    :date:                    2018.08.29
    :description:             清理s3用例环境
    :param account_email_lst: (list)账户邮箱
    :return:
    """
    """打开强删桶的开关"""
    rc, stdout = s3_common.set_force_delete_bucket(1)
    # common.judge_rc(rc, 0, "set_force_delete_bucket=1 fail!!!")
    if rc != 0:
        s3data_log.error("set_force_delete_bucket=1 fail!!!")
        raise Exception
    s3data_log.info("wait for force delete bucket working...")
    time.sleep(60)
    s3data_log.info("begin delete account...")
    """获取账户id"""
    for account_email in account_email_lst:
        """判断账户是否存在"""
        rc, stdout = s3_common.find_account(account_email)
        if rc != 0:
            s3data_log.error("account is not exist!")
            break
        """获取账户id"""
        rc, account_id = s3_common.get_account_id_by_email(account_email)
        if rc != 0:
            s3data_log.error("get_account_id_by_email failed")
        """获取证书id列表"""
        rc, certificate_id_lst, certificate_lst = s3_common.get_certificate_by_accountid(account_id)
        if rc != 0:
            s3data_log.error("get certificate by account id failed!")
        # 处理账户证书为空的情况
        if len(certificate_id_lst) == 0:
            s3_common.add_certificate(account_id)
        rc, certificate_id_lst, certificate_lst = s3_common.get_certificate_by_accountid(account_id)
        for certificate_id in certificate_id_lst:
            """获取所有桶的列表"""
            rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
            if rc != 0:
                s3data_log.error("get_all_bucket_name failed!!!")
            while (bucket_name_lst != []) and (bucket_name_lst is not None):
                for bucket_name in bucket_name_lst:
                    """删除桶"""
                    rc, stdout = s3_common.del_bucket(bucket_name, certificate_id)
                    if rc != 0:
                        s3data_log.error("delete bucket failed!")
                rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id)
            """删除证书"""
            s3_common.del_certificate(certificate_id)
        """删除账户"""
        rc,stdout = s3_common.del_account(account_id)
        if rc != 0:
            s3data_log.error("delete account failed!")
            raise Exception
    return


class S3DataConsistencyTest(object):
    def __init__(self, case_log_path):
        log_init_s3data(case_log_path)
        s3data_log.info("********** 初始化 s3data-log ************")

        self.start_flag = True
        self._running_flag = False
        self._return_value = True
        self._intervals = 60
        self.thread_lst = []
        self.start_time = 0
        self.running_time = 0

        # 获取一致性参数
        data_consistency_param = get_config.get_data_consistency_param()
        self.src_parent_dir = data_consistency_param['parent_dir']
        self.dst_parent_dir = data_consistency_param['parent_dir']
        self.vdb_thread_num = int(data_consistency_param['vdb_thread_num'])
        self.output_path = data_consistency_param['parent_dir']
        self.vdb_width = int(data_consistency_param['vdb_width'])
        self.round_timeout = int(data_consistency_param['round_timeout'])
        # 获取oOss_ip
        s3_access_ips_list = get_config.get_vip_addresses()[-1].encode('utf-8').split(',')
        self.oOss_ip = s3_access_ips_list[0]

    @run_func
    def start(self, ):

        self.thread_lst = []
        th = threading.Thread(target=self.check_in_loop)
        th_timeout = threading.Thread(target=self.judge_timeout)
        self.thread_lst.append(th)
        self.thread_lst.append(th_timeout)
        self._running_flag = True
        for th in self.thread_lst:
            th.daemon = True
            th.start()

    def judge_timeout(self):
        while True:
            if self._running_flag is False:
                break
            if self.start_time == 0:
                continue
            self.running_time = time.time() - self.start_time
            s3data_log.info("current round running time: %s" % self.running_time)
            if self.running_time > self.round_timeout:
                s3data_log.error("this round has running timeout!")
                self._running_flag = False
                break
            time.sleep(300)
        s3data_log.info("judge timeout thread is stopped!")

    @run_func
    def stop(self):
        s3data_log.info("stop s3_data_consistency, please wait for this round finish....")
        self.start_flag = False

    @run_func
    def is_running(self):
        """返回故障是否在执行"""
        return self._running_flag

    @run_func
    def return_value(self):
        """返回值"""
        return self._return_value

    @run_func
    def check_in_loop(self):
        s3data_log.info("===============清理账户========================")
        if email_lst:
            cleaning_environment(email_lst)
        # s3_common.cleaning_environment([ACCOUNT_EMAIL])

        s3data_log.info("1> 创建账户")
        account_name = FILE_NAME + "_account1"
        rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
        # common.judge_rc(rc, 0, "create account failed!!!")
        if rc != 0:
            s3data_log.error("create account failed!!!")
            self._running_flag = False
            raise Exception

        s3data_log.info("2> 创建证书")
        rc, certificate_id, certificate = s3_common.add_certificate(account_id)
        # common.judge_rc(rc, 0, "create certificate failed!!!")
        if rc != 0:
            s3data_log.error("create certificate failed!!!")
            self._running_flag = False
            raise Exception

        while True:
            if self.start_flag is False:
                self._running_flag = False
                break
            self.start_time = time.time()
            self.data_consistency_run(certificate_id)
            if self._return_value is False:
                self._running_flag = False
                break
            time.sleep(self._intervals)
        s3data_log.info("s3data thread is stopped!")

    @run_func
    def get_dir_files(self, path):
        src_dirpath = None
        src_dirnames = None
        src_filenames = None
        if os.path.exists(path):
            for src_dirpath, src_dirnames, src_filenames in os.walk(path):
                break
        else:
            s3data_log.error("The path:%s doesn't exist." % path)
            self._running_flag = False
            raise Exception
            # common.except_exit("The path:%s doesn't exist." % path)
        return src_dirpath, src_dirnames, src_filenames

    @run_func
    def read_get_file(self, file_path):
        """
        :author:          baourobing
        :date:            2018.08.29
        :description:     判断文件内容
        :param nodeip:
        :param file_path:
        :return:
        """
        cmd = 'ls -l %s' % file_path
        # print cmd
        rc, stdout = commands.getstatusoutput(cmd)
        objsize = stdout.split()[4]
        if int(objsize) <= 100:
            return -1
        else:
            return 0

    @run_func
    def add_object(self,
                   bucket_name,
                   object_name,
                   filepath,
                   certificate_id,
                   oOss_ip,
                   exe_node_ip=None,
                   print_flag=True,
                   retry=False):
        """
        :author:               baourobing
        :date:                 2018.08.29
        :description:          添加对象
        :param exe_node_ip:    (str)执行命令的节点
        :param bucket_name:    (str)桶名字
        :param object_name:    (str)对象名字
        :param filepath:       (str)文件的绝对路径
        :param certificate_id: (str)证书id
        :return:
        """
        cmd = 'curl -i http://%s:%s/%s/%s -X PUT -T %s -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
              % (oOss_ip, 20480, bucket_name, object_name, filepath, certificate_id)
        if exe_node_ip is None:
            rc, stdout = common.run_command_shot_time(cmd)
            common.pscli_run_command(cmd)
        else:
            rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
        if rc != 0:
            s3data_log.info(cmd)
            s3data_log.info(stdout)
            return rc, stdout
        else:
            if s3_common.check_curl(stdout):
                return 0, stdout
            else:
                return -1, stdout

    @run_func
    def download_object(self, bucket_name, object_name, filepath, certificate_id, sig=None, exe_node_ip=None, print_flag=True,
                        retry=False, ooss_ip=None):
        """
        :author:               baourobing
        :date:                 2018.08.29
        :description:          下载对象
        :param exe_node_ip:    (str)执行命令的节点ip
        :param bucket_name:    (str)桶名字
        :param object_name:    (str)对象名字
        :param filepath:       (str)存文件的路径
        :param certificate_id: (str)证书id
        :return:
        """
        if sig is None:
            cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS4-HMAC-SHA256 Credential=%s"' \
                  % (ooss_ip, 20480, bucket_name, object_name, filepath, certificate_id)
        else:
            cmd = 'curl -s http://%s:%s/%s/%s -o %s -H "Authorization: AWS %s:%s"' \
                  % (ooss_ip, 20480, bucket_name, object_name, filepath, certificate_id, sig)
        # s3data_log.info(cmd)
        if exe_node_ip is None:
            rc, stdout = common.run_command_shot_time(cmd)
        else:
            rc, stdout = common.run_command(exe_node_ip, cmd, print_flag=print_flag)
        if rc != 0:
            s3data_log.info(cmd)
            s3data_log.info(stdout)
        return rc, stdout

    @run_func
    def put_obj(self, bucket_name, certificate_id, parent_path, num, oOss_ip):
        src_child_dirpath, src_child_dirnames, src_child_filenames = self.get_dir_files(parent_path)
        for src_child_file in src_child_filenames:
            file_path = os.path.join(parent_path, src_child_file)
            md5 = list(s3_common.get_file_md5(file_path))
            object_name = "%s_%s" % (num, src_child_file)
            src_md5_dic[object_name] = md5
            while True:
                rc, stdout = self.add_object(bucket_name,
                                             object_name,
                                             file_path,
                                             certificate_id,
                                             oOss_ip,
                                             print_flag=False,
                                             retry=True)
                if 0 != rc:
                    s3data_log.info("========retry add object===========")
                    s3data_log.info(object_name)
                    s3data_log.error(stdout)
                    s3data_log.error("file upload error!!!")
                    time.sleep(5)
                    continue
                # 防止进入死循环
                if self._running_flag is False:
                    break
                break
        return

    @run_func
    def get_obj(self, bucket_name, certificate_id, dst_parent_dir, parent_path, num, oOss_ip):
        dst_path = os.path.join(dst_parent_dir, 'dst_vdb')
        src_child_dirpath, src_child_dirnames, src_child_filenames = self.get_dir_files(parent_path)
        for src_child_file in src_child_filenames:
            object_name = "%s_%s" % (num, src_child_file)
            filepath = os.path.join(dst_path, object_name)
            while True:
                rc, stdout = self.download_object(bucket_name,
                                                  object_name,
                                                  filepath,
                                                  certificate_id,
                                                  print_flag=False,
                                                  retry=True,
                                                  ooss_ip=oOss_ip)
                if 0 != rc:
                    s3data_log.info("========retry download object===========")
                    s3data_log.info(object_name)
                    s3data_log.error("cmd: download_object, stdout: %s" % stdout)
                    s3data_log.error("file download error!!!")
                    time.sleep(5)
                    continue
                rc1 = self.read_get_file(filepath)
                if 0 != rc1:
                    s3data_log.info("========retry download object===========")
                    s3data_log.info(object_name)
                    s3data_log.error("cmd: download_object, stdout: %s" % stdout)
                    s3data_log.error("download file error!!!")
                    time.sleep(5)
                    continue
                # 防止进入死循环
                if self._running_flag is False:
                    break
                break
            md5 = list(s3_common.get_file_md5(filepath))
            check_md5_dic[object_name] = md5
        return

    @run_func
    def data_consistency_run(self, certificate_id):
        s3data_log.info("********** 获取s3data参数 ************")

        s3data_log.info("3> 创建桶")
        bucket_name = FILE_NAME + '_bucket'
        bucket_name = bucket_name.replace('_', '-')
        rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
        while rc != 0:
            s3_common.add_bucket(bucket_name, certificate_id)
            rc, stdout = s3_common.check_bucket(bucket_name, certificate_id)
            s3data_log.error(stdout)
        #   common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

        src_path = os.path.join(self.src_parent_dir, 'src_vdb')
        dst_path = os.path.join(self.dst_parent_dir, 'dst_vdb')
        src_md5_path = '/tmp/src_md5_file'

        s3data_log.info("4> vdbench创建文件")
        obj_vdb = tool_use.Vdbenchrun(depth=1,
                                      width=self.vdb_width,
                                      files=self.vdb_thread_num,
                                      size='(4k,10,64k,20,120k,10,1M,10,2M,10,500k,20,10M,10,8M,10)',
                                      xfersize='4K',
                                      threads=self.vdb_thread_num,
                                      output_path=self.output_path)
        rc = obj_vdb.run_create(anchor_path=src_path, journal_path='/tmp')
        if rc != 0:
            s3data_log.error("vdbench create files failed!!!!")
            self._return_value = False
        # common.judge_rc(rc, 0, "vdbench create file failed!!!")

        is_exists = os.path.exists(dst_path)
        if not is_exists:
            os.makedirs(dst_path)

        s3data_log.info("5> 上传对象")
        src_dirpath, src_dirnames, src_filenames = self.get_dir_files(src_path)
        s3data_log.info('src_dirname_list is %s' % repr(src_dirnames))
        put_threads = []
        for src_dirname in src_dirnames:
            src_dir = os.path.join(src_dirpath, src_dirname)
            put_tmp = threading.Thread(target=self.put_obj,
                                       args=(bucket_name,
                                             certificate_id,
                                             src_dir,
                                             src_dirname,
                                             self.oOss_ip))
            put_threads.append(put_tmp)
            put_tmp.daemon = True
            put_tmp.start()
        for put_thread in put_threads:
            put_thread.join()

        s3data_log.info("6> 下载对象")
        get_threads = []
        for src_dirname in src_dirnames:
            src_dir = os.path.join(src_dirpath, src_dirname)
            get_tmp = threading.Thread(target=self.get_obj,
                                       args=(bucket_name,
                                             certificate_id,
                                             self.dst_parent_dir,
                                             src_dir,
                                             src_dirname,
                                             self.oOss_ip))
            get_threads.append(get_tmp)
            get_tmp.daemon = True
            get_tmp.start()
        for get_thread in get_threads:
            get_thread.join()

        s3data_log.info("7> 校验md5值")
        if os.path.exists(src_md5_path):
            os.system("rm -rf %s" % src_md5_path)
        os.system('touch %s' % src_md5_path)
        with open(src_md5_path, 'w') as f:
            json.dump(src_md5_dic, f)

        if len(src_md5_dic) != len(check_md5_dic):
            s3data_log.info('the num of src_files is %s\n' % len(src_md5_dic))
            s3data_log.info('the num of dst_files is %s\n' % len(check_md5_dic))
            self._return_value = False
        for key in src_md5_dic:
            if src_md5_dic[key] != check_md5_dic[key]:
                s3data_log.error('src_md5_dic: file:%s, md5sum:%s\n'
                                 'check_md5_dic: file:%s, md5sum:%s\n'
                                 % (key, src_md5_dic[key], key, check_md5_dic[key]))
                s3data_log.error("%s failed" % FILE_NAME)
                self._return_value = False
                break
        else:
            s3data_log.info("md5 is OK")
            cmd1 = "rm -rf %s" % src_path
            cmd2 = "rm -rf %s" % dst_path
            common.command(cmd1)
            common.command(cmd2)
            s3data_log.info("%s succeed" % FILE_NAME)

            s3data_log.info("8> 清理桶和对象")
            rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id, retry=True)
            if rc != 0:
                s3data_log.error("get_all_bucket_name failed!!!")
                self._return_value = False
            while (bucket_name_lst != []) and (bucket_name_lst is not None):
                for bucket_name in bucket_name_lst:
                    s3_common.del_bucket(bucket_name, certificate_id, exe_node_ip=None, retry=True)
                rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id, retry=True)
            s3data_log.info("delete all bucket success!")
        return

if __name__ == '__main__':
    case_log_path = '/home/StorTest/test_cases/log/case_log/test'

    aaa = S3DataConsistencyTest(case_log_path)
    aaa.start()
    for i in range(10):
        s3data_log.info("running flag: %s" % aaa.is_running())
        time.sleep(10)

    aaa.stop()
    while True:
        s3data_log.info("running flag: %s" % aaa.is_running())
        time.sleep(30)