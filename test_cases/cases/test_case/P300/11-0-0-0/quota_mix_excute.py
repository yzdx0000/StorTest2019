#-*-coding:utf-8 -*
import utils_path
import os
import log
import common
import time
import quota_common
import prepare_clean
import get_config
N = 3               # 循环次数

quota_create_group_path = "/home/StorTest/test_cases/cases/test_case/P300/11-0-0-0/create_quota_group_user.py"
quota_mix_nest_two_3_path = "/home/StorTest/test_cases/cases/test_case/P300/11-0-0-0/quota_mix_nest_two_3.py"
FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]          # 本脚本名字
CLIENT_IP_1 = get_config.get_client_ip(0)


def case():
    """
    author:liyi
    date:2018-10-05
    description : 收集脚本执行日志，并对日志进行处理，处理后结果保存到quota.log中
    :return:
    """
    log.info("case begin...........")
    flag = True
    for exec_num in range(N):
        if(flag):
            cmd = "python %s" % quota_create_group_path
            common.run_command_shot_time(cmd)
        flag = False
        log.info("###第 %s次循环" % (exec_num + 1))
        cmd = "python %s| tee -a /home/StorTest/test_cases/log/case_log/stdout.log" %  quota_mix_nest_two_3_path
        common.run_command_shot_time(cmd)
        time.sleep(2)

    filename = '/home/StorTest/test_cases/log/case_log/stdout.log'
    """对日志文件处理,提取以###开头的行"""
    f = open('/home/StorTest/test_cases/log/case_log/quota.log', 'w')
    with open(filename) as files:
        cnt = 0
        for line in files:
            cnt = cnt + 1
            if '###' in line:
                print(cnt, ":", line)
                f.write(line)
            else:
                pass
    f.close()


def main():
    prepare_clean.quota_test_prepare(FILE_NAME)
    case()
    log.info('%s succeed!' % FILE_NAME)
    prepare_clean.quota_test_prepare(FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
