#-*-coding:utf-8 -*
#!/usr/bin/python

'''
LTP_syscalls测试集
'''

import os, commands
import utils_path
import common
import log
import shell
import get_config


def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建客户端授权'''
    client_ip = get_config.get_client_ip(0)

    '''客户端运行ltp_syscalls测试集'''
    cmd = ("/opt/ltp/runltp -p -q -l /tmp/ltp_fs.result -o /tmp/ltp_fs.out -C /tmp/ltp_fs.fail "
           "-d /mnt/parastor/ltp -f /opt/ltp/runtest/fs")
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(client_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''检查fail文件'''
    syscalls = ["inotify02"]  #讨论允许失败项

    cmd = "ssh %s awk '{print$1}' /tmp/ltp_fs.fail" % system_ip
    rc, stdout = commands.getstatusoutput(cmd)
    if 0 != rc:
        log.error("awk failed!!!")
        raise Exception("awk failed!!!")
    else:
        stdout_lst = stdout.splitlines()
        for mem in stdout_lst:
            if mem not in syscalls:
                log.error("Execute command: LTP_fs failed,Please check /tmp/ltp_fs.fail!")
                raise Exception(
                    "Execute command: LTP_fs failed,Please check /tmp/ltp_fs.fail!")

    '''检查系统状态'''
    common.ckeck_system()

    return


def main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    case()
    log.info('succeed!')
    return

if __name__ == '__main__':
    main()
