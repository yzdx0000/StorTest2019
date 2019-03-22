# -*-coding:utf-8 -*
import os
import time
import threading

import utils_path
import log
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
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL = FILE_NAME + "@sugon.com"

VDB_THREADS = 20
ANCHOR_PATH = '/tmp'
src_path = os.path.join(ANCHOR_PATH, 'src_vdb')
dst_path = os.path.join(ANCHOR_PATH, 'dst_vdb')

src_md5_dic = {}
check_md5_dic = {}


def get_dir_files(path):
    if os.path.exists(path):
        for src_dirpath, src_dirnames, src_filenames in os.walk(path):
            break
    else:
        common.except_exit("The path:%s doesn't exist." % path)
    return src_dirpath, src_dirnames, src_filenames

def read_get_file(file_path):
    """
    :author:          baourobing
    :date:            2018.08.29
    :description:     判断文件内容
    :param nodeip:
    :param file_path:
    :return:
    """
    cmd = 'ls -l %s' % file_path
    print cmd
    rc, stdout = commands.getstatusoutput(cmd)
    objsize = stdout.split()[4]
    if int(objsize) <= 100:
        return -1
    else:
        return 0


def put_obj(bucket_name, certificate_id, parent_path, num):
    src_child_dirpath, src_child_dirnames, src_child_filenames = get_dir_files(parent_path)
    for src_child_file in src_child_filenames:
        file_path = os.path.join(parent_path, src_child_file)
        md5 = list(s3_common.get_file_md5(file_path))
        object_name = "%s_%s" % (num, src_child_file)
        src_md5_dic[object_name] = md5
        rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id, print_flag=False,retry=True)
        while rc != 0:
            time.sleep(5)
            rc, stdout = s3_common.add_object(bucket_name, object_name, file_path, certificate_id, print_flag=False,retry=True)
    return


def get_obj(bucket_name, certificate_id, parent_path, num):
    src_child_dirpath, src_child_dirnames, src_child_filenames = get_dir_files(parent_path)
    for src_child_file in src_child_filenames:
        object_name = "%s_%s" % (num, src_child_file)
        filepath = os.path.join(dst_path, object_name)
        rc, stdout = s3_common.download_object(bucket_name, object_name, filepath, certificate_id, print_flag=False, retry=True)
        rc1 = read_get_file(filepath) 
        while rc != 0 or rc1 != 0:
            time.sleep(5)
            rc, stdout = s3_common.download_object(bucket_name, object_name, filepath, certificate_id, print_flag=False,retry=True)
            rc1 = read_get_file(filepath)
        md5 = list(s3_common.get_file_md5(filepath))
        check_md5_dic[object_name] = md5
    return

 

def case():
    log.info("1> 创建账户")
    account_name = FILE_NAME + "_account1"
    rc, account_id = s3_common.add_account(account_name, ACCOUNT_EMAIL, 0)
    common.judge_rc(rc, 0, "create account failed!!!")

    log.info("2> 创建证书")
    rc, certificate_id, certificate = s3_common.add_certificate(account_id)
    common.judge_rc(rc, 0, "create certificate failed!!!")

    log.info("3> 创建桶")
    bucket_name = FILE_NAME + '_bucket'
    rc, stdout = s3_common.add_bucket(bucket_name, certificate_id)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)

    log.info("4> vdbench创建文件")
    obj_vdb = tool_use.Vdbenchrun(depth=1, width=VDB_THREADS, files=100,
                                  size='(4k,10,64k,20,120k,10,1M,10,2M,10,500k,20,10M,10,8M,10)',
                                  xfersize='4K',
                                  threads=VDB_THREADS)
    rc = obj_vdb.run_create(anchor_path=src_path, journal_path='/tmp')
    common.judge_rc(rc, 0, "vdbench create file failed!!!")

    is_exists = os.path.exists(dst_path)
    if not is_exists:
        os.makedirs(dst_path)

    log.info("5> 上传对象")
    src_dirpath, src_dirnames, src_filenames = get_dir_files(src_path)
    log.info('src_dirname_list is %s' % repr(src_dirnames)) 
    put_threads = []
    for src_dirname in src_dirnames:
        src_dir = os.path.join(src_dirpath, src_dirname)
        put_tmp = threading.Thread(target=put_obj, args=(bucket_name, certificate_id, src_dir, src_dirname))
        put_threads.append(put_tmp)
        put_tmp.daemon = True
        put_tmp.start()
    for put_thread in put_threads:
        put_thread.join()

    log.info("6> 下载对象")
    get_threads = []
    for src_dirname in src_dirnames:
        src_dir = os.path.join(src_dirpath, src_dirname)
        get_tmp = threading.Thread(target=get_obj, args=(bucket_name, certificate_id, src_dir, src_dirname))
        get_threads.append(get_tmp)
        get_tmp.daemon = True
        get_tmp.start()
    for get_thread in get_threads:
        get_thread.join()

    log.info("7> 校验md5值")
    src_md5_path = '/tmp/src_md5_file'
    if os.path.exists(src_md5_path):
            os.system("rm -rf %s" % src_md5_path)
    os.system('touch %s' % src_md5_path)
    with open(src_md5_path, 'w') as f:
        json.dump(src_md5_dic, f)
   
    if len(src_md5_dic) != len(check_md5_dic):
        log.info(len(src_md5_dic))
        log.info(len(check_md5_dic))
        common.except_exit("len is not same!!!")
    for key in src_md5_dic:
        if src_md5_dic[key] != check_md5_dic[key]:
            log.info('src_md5_dic: file:%s, md5sum:%s\n'
                  'check_md5_dic: file:%s, md5sum:%s\n'
                   % (key, src_md5_dic[key], key, check_md5_dic[key]))
            common.except_exit("md5 is not same!!!")
    else:
        log.info("md5 is OK")


    # cmd1 = "rm -rf %s" % src_path
    cmd2 = "rm -rf %s" % dst_path
    # common.command(cmd1)
    common.command(cmd2)
    return


def main():
    prepare_clean.s3_test_prepare(FILE_NAME, [ACCOUNT_EMAIL])
    case()
#    prepare_clean.s3_test_clean([ACCOUNT_EMAIL])
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
