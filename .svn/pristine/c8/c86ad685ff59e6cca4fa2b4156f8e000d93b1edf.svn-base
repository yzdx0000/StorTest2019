# -*-coding:utf-8 -*
import os

import utils_path
import log
import common
import get_config
import prepare_clean

##########################################
#
# Author: baorb
# date 2018-11-13
# @summary：
#    测试聚合持续CREATE/MKDIR/UNLINK/RMDIR/STAT性能。
# @steps:
#    1，多客户端跑mdtest测试性能
#
# @changelog：
##########################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
PROPERTY_TRUE_PATH = os.path.join(prepare_clean.PROPERTY_PATH, FILE_NAME)   # /mnt/volume1/mini_case/3_0014_data_test
FILE_DIR = os.path.dirname(__file__)
One_Node_NP = 20


def case():
    log.info("获取聚合持续CREATE/MKDIR/UNLINK/RMDIR/STAT性能")
    client_node_lst = get_config.get_allclient_ip()
    conf_content_lst = []
    for client_node in client_node_lst:
        str_content = "%s slots=%s" % (client_node, One_Node_NP)
        conf_content_lst.append(str_content)
    conf_content_str = '\n'.join(conf_content_lst)
    mdtest_conf = os.path.join(FILE_DIR, 'mdtest_machines')
    with open(mdtest_conf, 'w') as fd:
        fd.write(conf_content_str)
    np_num = One_Node_NP * len(conf_content_lst)
    cmd = ("mpirun --allow-run-as-root -np %s --machinefile %s mdtest -b 2 -z 5 -I 1000 -u -d %s"
           % (np_num, mdtest_conf, PROPERTY_TRUE_PATH))
    rc, stdout = common.run_command_shot_time(cmd)
    common.judge_rc(rc, 0, "mdtest failed!\nstdout: %s" % stdout)
    stdout_line_lst = stdout.splitlines()
    dir_creat = 0
    dir_stat = 0
    dir_remove = 0
    file_create = 0
    file_stat = 0
    file_unlink = 0
    for line in stdout_line_lst:
        if 'Directory creation' in line:
            dir_creat = line.split(':')[-1].split()[-2]
        if 'Directory stat' in line:
            dir_stat = line.split(':')[-1].split()[-2]
        if 'Directory removal' in line:
            dir_remove = line.split(':')[-1].split()[-2]
        if 'File creation' in line:
            file_create = line.split(':')[-1].split()[-2]
        if 'File stat' in line:
            file_stat = line.split(':')[-1].split()[-2]
        if 'File removal' in line:
            file_unlink = line.split(':')[-1].split()[-2]

    log.info("***********************************************")
    log.info("一共%s个客户端，每个客户端%s个线程" % (len(conf_content_lst), One_Node_NP))
    log.info("目录mkdir: %s/s" % dir_creat)
    log.info("目录stat: %s/s" % dir_stat)
    log.info("目录rmdir: %s/s" % dir_remove)
    log.info("文件create: %s/s" % file_create)
    log.info("文件stat: %s/s" % file_stat)
    log.info("文件unlink: %s/s" % file_unlink)
    log.info("***********************************************")
    log.info("case succeed!")
    return


def main():
    prepare_clean.preperty_test_prepare(FILE_NAME)
    case()
    prepare_clean.preperty_test_clean(FILE_NAME)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)