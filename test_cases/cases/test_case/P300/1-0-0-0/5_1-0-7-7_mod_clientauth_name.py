#-*-coding:utf-8 -*
#!/usr/bin/python

'''
修改客户端授权
'''
import json
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

    '''创建两个卷'''
    cmd = ("pscli --command=create_volume --name=fs1 --type=FILE --storage_pool_id=%s --is_simple_conf=true "
           "--min_throughput=1 --max_throughput=10000 --min_iops=1 --max_iops=10000 --stripe_width=4"
           "--disk_parity_num=2 --node_parity_num=1 --replica_num=1 --total_bytes=10737418240" % storage_pool_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    cmd = ("pscli --command=create_volume --name=fs2 --type=FILE --storage_pool_id=%s --is_simple_conf=true "
           "--min_throughput=1 --max_throughput=10000 --min_iops=1 --max_iops=10000 --stripe_width=4"
           "--disk_parity_num=2 --node_parity_num=1 --replica_num=1 --total_bytes=10737418240" % storage_pool_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 != rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    volume1_id = common.get_volume_id('fs1')
    volume2_id = common.get_volume_id('fs2')

    '''创建授权'''
    common.create_client_auth('1.1.0.13', volume1_id)
    volume_ids = [volume1_id]
    client_auth_id = common.get_client_auth_id('1.1.0.13', volume_ids)

    '''修改授权为卷fs2'''
    common.update_client_auth(client_auth_id, '1.1.0.13', volume2_id)

    '''修改授权为卷fs1和fs2'''
    volume1_2_id = (volume1_id + ',' + volume2_id)
    common.update_client_auth(client_auth_id, '1.1.0.13', volume1_2_id)

    '''修改授权的卷为空'''
    cmd = ("pscli --command=update_client_auth --auth_info=\'{\"id\":%s,\"ip\":\"1.1.0.13\",\"volume_ids\":[]}\'" %client_auth_id)
    log.info(cmd)
    rc, stdout, stderr = shell.ssh(system_ip, cmd)
    if 0 == rc:
        log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
        raise Exception(
            "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
    else:
        msg = common.json_loads(stdout)
        if msg['err_no'] != 7004 or msg['err_msg'] != 'CLIENT_AUTH_VOLUME_IDS_EMPTY':
            log.error("Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))
            raise Exception(
                "Execute command: \"%s\" failed. \nstdout: %s \nstderr: %s" % (cmd, stdout, stderr))

    '''修改授权为卷fs1'''
    common.update_client_auth(client_auth_id, '1.1.0.13', volume1_id)

    '''检查系统状态'''
    common.ckeck_system()

    '''清除资源'''
    common.clear_test_env()

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
