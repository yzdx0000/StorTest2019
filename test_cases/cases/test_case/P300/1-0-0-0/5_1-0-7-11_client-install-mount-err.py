#-*-coding:utf-8 -*
#!/usr/bin/python

'''
安装私有客户端
'''
import os

import utils_path
import common
import log
import shell
import get_config


def case():
    log.info("----------case begin----------")
    '''获取系统节点ip'''
    system_ip = get_config.get_parastor_ip(0)

    '''创建节点池'''
    common.create_nodepool('nodepool1', '1,2,3,4,5', 4, 2, 1, 1)
    nodepool_id = common.get_nodepool_id('nodepool1')

    '''创建存储池'''
    common.create_storagepool('stor1', 'FILE', nodepool_id)
    storage_pool_id = common.get_storagepool_id('stor1')

    '''创建卷'''
    cmd = ("pscli --command=create_volume --name=fs1 --type=FILE --storage_pool_id=%s --is_simple_conf=true "
           "--min_throughput=1 --max_throughput=10000 --min_iops=1 --max_iops=10000 --stripe_width=4"
           "--disk_parity_num=2 --node_parity_num=1 --replica_num=1 --total_bytes=10737418240" % storage_pool_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    volume_id = common.get_volume_id('fs1')

    '''创建客户端授权'''
    client_ip = get_config.get_client_ip(0)
    common.create_client_auth(client_ip, volume_id)

    '''安装客户端'''
    common.set_client(client_ip)

    '''挂载输入错误的系统名字'''
    '''检查mount路径是否存在'''
    mount_path = ("/mnt/volume1")
    if True != common.check_path_exist(client_ip, mount_path):
        cmd1 = ("mkdir %s" % mount_path)
        log.info(cmd1)
        rc, stdout, stderr = shell.ssh(client_ip, cmd1)
        if 0 != rc:
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd1, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd1, stdout, stderr))

    cmd2 = ("mount -t parastor nodev %s -o sysname=err -o fsname=fs1" % (mount_path))
    log.info(cmd2)
    rc, stdout, stderr = shell.ssh(client_ip, cmd2)
    if rc == 0:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd2, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd2, stdout, stderr))

    '''客户端挂载'''
    common.mount_client(client_ip, '/mnt/volume1', 'fs1')

    '''取消客户端挂载'''
    common.umount_client(client_ip, '/mnt/volume1')

    '''卸载客户端'''
    common.uninstall_client(client_ip)

    '''检查系统状态'''
    common.ckeck_system()

    return


def main():
    file_name = os.path.basename(__file__)
    file_name = file_name[:-3]
    log_file_path = log.get_log_path(file_name)
    stream = log.init(log_file_path, True)
    case()
    log.info('succeed!')
    return

if __name__ == '__main__':
    main()
