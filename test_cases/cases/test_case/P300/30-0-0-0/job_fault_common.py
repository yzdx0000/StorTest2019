# -*-coding:utf-8 -*
import os
import time
import utils_path
import log
import common
import get_config
import get_config_job_fault
import make_fault
import vdbench_common
import random
import quota_common
import nas_common

SYSTEM_IP_0 = get_config.get_parastor_ip(0)
SYSTEM_IP_1 = get_config.get_parastor_ip(1)
SYSTEM_IP_2 = get_config.get_parastor_ip(2)

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
log_file_path = log.get_log_path(FILE_NAME)
log.init(log_file_path, True)

#######################################################
# 函数功能：高可用job故障,库函数接口
# 脚本作者：duyuli
# 日期：2019-01-12
#######################################################

def get_master_opara_node_ip():
    cmd = "/home/parastor/tools/nWatch -t oPara -i 3 -c QMGR#getqmgr"
    rc, stdout = common.pscli_run_command(cmd)
    common.judge_rc(rc, 0, "get opara master")
    master_id = stdout.strip().split('[')[1].split("]")[0]
    node_obj = common.Node()
    node_ip_opara = node_obj.get_node_ip_by_id(master_id)
    return node_ip_opara

def get_master_orole_node_ip():
    cmd = "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_master_dump"
    rc, stdout = common.pscli_run_command(cmd)
    common.judge_rc(rc, 0, "get oRole master")
    master_id = stdout.strip().split(':')[-1]
    node_obj = common.Node()
    node_ip_orole = node_obj.get_node_ip_by_id(master_id)
    return node_ip_orole

def check_progress(node_ip, progress_name):
    for i in range(600):
        if make_fault.check_process(node_ip, progress_name):
            break
        if i == 599:
            raise Exception("check progress failed timeout 10min")
        time.sleep(1)

    return

def pscli_add_force_pending_strategy(job_name, phase, sync="true"):
    """添加job pending"""

    # 此处用pscli，该命令正常包中不可见，专用于高可用故障测试
    cmd = "pscli --command=add_force_pending_strategy --job_name=%s --phase=%s --sync=%s" % (
        job_name, phase, sync)

    rc, stdout = common.pscli_run_command(cmd)
    common.judge_rc(rc, 0, "add_force_pending_strategy")
    return

def pscli_remove_force_pending_strategy(job_name):
    """移除job pending"""

    # 此处用pscli，该命令正常包中不可见，专用于高可用故障测试
    cmd = "pscli --command=remove_force_pending_strategy --job_name=%s" % job_name
    rc, stdout = common.pscli_run_command(cmd)
    common.judge_rc(rc, 0, "remove_force_pending_strategy")
    return

def pscli_wakeup_force_pending_job(job_name):
    """移除job pending"""

    # 此处用pscli，该命令正常包中不可见，专用于高可用故障测试
    cmd = "pscli --command=wakeup_force_pending_job --job_name=%s" % job_name

    rc, stdout = common.pscli_run_command(cmd)
    common.judge_rc(rc, 0, "wakeip_force_pending_job")
    return

def make_fault_disk_pullout(disk_usage, rebuilding=True):
    """
    拔盘操作，触发重建
    :param rebuilding: 是否重建
    :param disk_usage: DATA  or   SHARED
    :return:
    """

    ob_node = common.Node()
    ob_disk = common.Disk()
    nodeid_list = ob_node.get_nodes_id()

    fault_node_id = random.choice(nodeid_list)
    fault_node_ip = ob_node.get_node_ip_by_id(fault_node_id)

    '''获取节点内的所有数据盘的物理id'''
    share_disk_names, monopoly_disk_names = ob_disk.get_share_monopoly_disk_names(fault_node_id)

    """随机获取一个数据盘"""
    fault_disk_name = ""
    if disk_usage == "DATA":
        fault_disk_name = random.choice(monopoly_disk_names)
    """随机获取一个共享盘"""
    if disk_usage == "SHARED":
        fault_disk_name = random.choice(share_disk_names)

    disk_scsi_id = ob_disk.get_physicalid_by_name(fault_node_ip, fault_disk_name)
    fault_disk_uuid = ob_disk.get_disk_uuid_by_name(fault_node_id, fault_disk_name)
    fault_disk_id = ob_disk.get_diskid_by_name(fault_node_id, fault_disk_name)
    storage_pool_id = ob_disk.get_storage_pool_id_by_diskid(fault_node_id, fault_disk_id)

    # 更新磁盘重建的等待时间为1分钟
    if rebuilding:
        common.update_param('MGR', 'disk_isolate2rebuild_timeout', '60000')
    make_fault.pullout_disk(fault_node_ip, disk_scsi_id, disk_usage)

    log.info("pullout disk wait 60s")
    time.sleep(60)

    log.info("node_ip:%s disk_name:%s storage_pool_id:%s" % (fault_node_ip, fault_disk_name, storage_pool_id))
    if rebuilding:
        log.info("wait occur rebuilding 120s")
        time.sleep(120)
    return [fault_node_ip, disk_scsi_id, fault_disk_uuid, fault_disk_id, storage_pool_id]

def make_fault_disk_insert(node_ip, disk_scsi_id, fault_disk_uuid,
                           fault_disk_id, storage_pool_id, disk_usage, rebuilding=True):
    """不断检查重建任务是否存在"""
    start_time = time.time()
    while True:
        if common.check_rebuild_job() is False:
            log.info('rebuild job finish!!!')
            break
        time.sleep(20)
        exist_time = int(time.time() - start_time)
        m, s = divmod(exist_time, 60)
        h, m = divmod(m, 60)
        log.info('rebuild job exist %dh:%dm:%ds' % (h, m, s))

    """插入磁盘"""
    make_fault.insert_disk(node_ip, disk_scsi_id, disk_usage)

    log.info('wait 30s')
    time.sleep(30)
    if rebuilding:
        '''将等待时间的参数修改回来'''
        common.update_param('MGR', 'disk_isolate2rebuild_timeout', '3600000')
    """删除磁盘"""
    common.remove_disks(fault_disk_id)

    log.info('wait 30s')
    time.sleep(30)
    ob_node = common.Node()
    fault_node_id = ob_node.get_node_id_by_ip(node_ip)
    rc, stdout = common.add_disks(fault_node_id, fault_disk_uuid, disk_usage, storage_pool_id=storage_pool_id)
    common.judge_rc(rc, 0, 'add disk to storage pool failed')
    return

def make_fault_vir_down_node(fault_ip_list):
    node_info_tuple_list = vdbench_common.down_node(fault_ip=fault_ip_list)
    for node_ip in fault_ip_list:
        for i in range(600):
            if common.check_ping(node_ip) is False:
                log.info("down vir node: %s success" % node_ip)
                break
            if i == 599:
                log.info("down vir node: %s failed" % node_ip)
                raise Exception("down vir node failed timeout 10min")
            time.sleep(1)
    return node_info_tuple_list

def make_fault_vir_up_node(node_info_tuple_list):
    vdbench_common.up_node(node_info=node_info_tuple_list)

    for node_ip_tuple in node_info_tuple_list:
        for i in range(600):
            node_ip = node_ip_tuple[1]
            if common.check_ping(node_ip):
                log.info("up vir node: %s success" % node_ip)
                break
            if i == 599:
                log.info("up vir node: %s failed" % node_ip)
                raise Exception("down vir node failed timeout 10min")
            time.sleep(1)

    return

def make_fault_remove_node_rebuilding(node_ip):
    node = common.Node()
    node_id = node.get_node_id_by_ip(node_ip)
    common.update_param("MGR", "node_isolate_timeout", "300000")
    rc, stdout = common.remove_node(node_id, remove_mode="AUTO_REBOOT")
    common.judge_rc(rc, 0, "remove node failed")

    for i in range(600):
        if common.check_ping(node_ip) is False:
            log.info("remove node: %s success" % node_ip)
            break
        if i == 599:
            log.info("remove node: %s failed" % node_ip)
            raise Exception("down vir node failed timeout 10min")
        time.sleep(1)
    log.info("wait until occur rebuilding 360s")
    time.sleep(360)
    return

def make_fault_remove_node_no_rebuilding(node_ip):
    node = common.Node()
    node_id = node.get_node_id_by_ip(node_ip)
    rc, stdout = common.remove_node(node_id, remove_mode="AUTO_REBOOT")
    common.judge_rc(rc, 0, "remove node failed")

    for i in range(600):
        if common.check_ping(node_ip) is False:
            log.info("remove node: %s success" % node_ip)
            break
        if i == 599:
            log.info("remove node: %s failed" % node_ip)
            raise Exception("down vir node failed timeout 10min")
        time.sleep(1)
    return

def make_fault_add_node(node_ip):
    # 添加节点，以node_ip.xml命名的配置文件

    for i in range(600):
        if common.check_ping(node_ip):
            log.info("ping node: %s success" % node_ip)
            break
        if i == 599:
            log.info("ping node: %s failed" % node_ip)
            raise Exception("down vir node failed timeout 10min")
        time.sleep(1)

    time.sleep(20)
    log.info("add node please waite...")
    common.update_param("MGR", "node_isolate_timeout", "86400000")
    config_file_path = os.path.join(get_config.config_path, "%s.xml" % node_ip)
    rc, stdout = common.add_nodes(config_file_path)
    common.judge_rc(rc, 0, "add node failed")

    # 扩容到到节点池
    node = common.Node()
    rc, stdout = common.get_node_pools()
    common.judge_rc(rc, 0, "get_node_pools failed")

    node_pool = common.json_loads(stdout)["result"]["node_pools"][0]
    node_id = node.get_node_id_by_ip(node_ip)
    node_ids_list = node_pool["node_ids"]
    node_ids_list.append(node_id)
    node_ids = ','.join(map(str, node_ids_list))  # 列表中不全是字符串会报错
    rc, stdout = common.update_node_pool(node_pool["id"], node_pool["name"], node_ids)
    common.judge_rc(rc, 0, "update node pool failed")

    # 扩容到存储池
    rc, stdout = common.get_storage_pools()
    common.judge_rc(rc, 0, "get_storage_pools failed")
    storage_pool = common.json_loads(stdout)["result"]["storage_pools"][1]  # 0为共享池
    rc, stdout = common.expand_storage_pool(storage_pool["id"], node_pool["id"])
    common.judge_rc(rc, 0, "expand storage pool failed")

    # 启动系统
    rc, stdout = common.startup()
    common.judge_rc(rc, 0, "start up sys failed")
    return

def make_fault_master_ojmgs():
    """主oJmgs故障"""
    rc, stdout = common.get_master()
    common.judge_rc(rc, 0, "get master")
    stdout = common.json_loads(stdout)

    node_obj = common.Node()
    master_id = stdout['result']['node_id']
    node_ip = node_obj.get_node_ip_by_id(int(master_id))

    # 做oJmgs主节点进程故障
    process_name = "oJmgs"
    cmd = "mv /home/parastor/bin/oJmgs /home/parastor/bin/oJmgs_bk"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "mv oPara wrong")
    make_fault.kill_process(node_ip, process_name)

    return node_ip

def make_fault_recover_master_ojmgs(node_ip):
    # 恢复环境
    cmd1 = "mv /home/parastor/bin/oJmgs_bk /home/parastor/bin/oJmgs"
    rc, stdout = common.run_command(node_ip, cmd1)
    common.judge_rc(rc, 0, "mv oPara wrong")
    return

def make_fault_zk(node_ip):
    # 做zk进程故障
    process_name = "zk"
    cmd = "mv /home/parastor/conf/zk/bin/zkServer.sh /home/parastor/conf/zk/bin/zkServer_bk.sh"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "mv zkServer.sh wrong")
    make_fault.kill_process(node_ip, process_name)
    return

def make_fault_recover_zk(node_ip):
    cmd = "mv /home/parastor/conf/zk/bin/zkServer_bk.sh /home/parastor/conf/zk/bin/zkServer.sh"
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "mv zkServer.sh bk wrong")
    return

def make_fault_master_opara_or_orole(opara=False, orole=False):
    """主oPara故障 或者 主oRole故障"""
    node_ip_opara = ""
    node_ip_orole = ""

    # 获取主oPara的ip
    if opara:
        cmd = "/home/parastor/tools/nWatch -t oPara -i 3 -c QMGR#getqmgr"
        rc, stdout = common.pscli_run_command(cmd)
        common.judge_rc(rc, 0, "get opara master")
        master_id = stdout.strip().split('[')[1].split("]")[0]
        node_obj = common.Node()
        node_ip_opara = node_obj.get_node_ip_by_id(master_id)

        # 开始做故障
        process_name = "oPara"
        cmd = "mv /home/parastor/bin/oPara /home/parastor/bin/oPara_bk"
        rc, stdout = common.run_command(node_ip_opara, cmd)
        common.judge_rc(rc, 0, "mv oPara wrong")
        make_fault.kill_process(node_ip_opara, process_name)

    # 获取主oRole的ip
    if orole:
        cmd = "/home/parastor/tools/nWatch -t oRole -i 1 -c oRole#rolemgr_master_dump"
        rc, stdout = common.pscli_run_command(cmd)
        common.judge_rc(rc, 0, "get oRole master")
        master_id = stdout.strip().split(':')[-1]
        node_obj = common.Node()
        node_ip_orole = node_obj.get_node_ip_by_id(master_id)

        # 开始做故障
        process_name = "oRole"
        cmd = "mv /home/parastor/bin/oRole /home/parastor/bin/oRole_bk"
        rc, stdout = common.run_command(node_ip_orole, cmd)
        common.judge_rc(rc, 0, "mv oRole wrong")
        make_fault.kill_process(node_ip_orole, process_name)

    if opara and orole:
        return node_ip_opara, node_ip_orole
    if opara:
        return node_ip_opara
    if orole:
        return node_ip_orole

def make_fault_recover_master_opara_or_orole(node_ip_opara=None, node_ip_orole=None):
    """恢复环境"""
    if node_ip_opara:
        cmd = "mv /home/parastor/bin/oPara_bk /home/parastor/bin/oPara"
        rc, stdout = common.run_command(node_ip_opara, cmd)
        common.judge_rc(rc, 0, "mv oPara_bk wrong")

    if node_ip_orole:
        cmd = "mv /home/parastor/bin/oRole_bk /home/parastor/bin/oRole"
        rc, stdout = common.run_command(node_ip_orole, cmd)
        common.judge_rc(rc, 0, "mv oRole_bk wrong")
    return

def make_fault_other_process_random(no_opara=False, no_orole=False):
    process_list = ['oStor', 'oPara', 'oRole', 'oMgcd', 'oJob']
    parastor_ip_list = get_config.get_allparastor_ips()

    if no_opara:
        opara_ip = get_master_opara_node_ip()
        parastor_ip_list.remove(opara_ip)
    if no_orole:
        orole_ip = get_master_orole_node_ip()
        parastor_ip_list.remove(orole_ip)

    exe_ip = random.choice(parastor_ip_list)
    process_name = random.choice(process_list)

    # 开始做故障
    cmd = "mv /home/parastor/bin/%s /home/parastor/bin/%s_bk" % (process_name, process_name)
    rc, stdout = common.run_command(exe_ip, cmd)
    common.judge_rc(rc, 0, "mv %s wrong" % process_name)
    make_fault.kill_process(exe_ip, process_name)
    return exe_ip, process_name

def make_fault_recover_other_process(node_ip, process_name):
    cmd = "mv /home/parastor/bin/%s_bk /home/parastor/bin/%s" % (process_name, process_name)
    rc, stdout = common.run_command(node_ip, cmd)
    common.judge_rc(rc, 0, "mv %s wrong" % process_name)
    return

def get_access_zone_id_by_name(name):
    rc, stdout = common.get_access_zones()
    common.judge_rc(rc, 0, "get access")
    stdout = common.json_loads(stdout)
    for info in stdout["result"]["access_zones"]:
        if info["name"] == name:
            access_id = info["id"]
            return access_id
    return None

def delete_ftp_nfs_smb_export():
    ids_ftp = nas_common.get_ftp_exports_id_list()
    ids_nfs = nas_common.get_nfs_exports_id_list()
    ids_smb = nas_common.get_smb_exports_id_list()
    if ids_ftp:
        common.delete_ftp_exports(ids_ftp)
    if ids_nfs:
        common.delete_nfs_exports(ids_nfs)
    if ids_smb:
        common.delete_smb_exports(ids_smb)
    return

def create_access_zone():
    obj_node = common.Node()
    id_list = obj_node.get_nodes_id()
    node_ids = ",".join(str(i) for i in id_list)
    rc, stdout = common.create_access_zone(node_ids=node_ids, name="testzone")
    common.judge_rc(rc, 0, "create_access_zone")
    return

def create_subnet():
    access_zone_id = get_access_zone_id_by_name("testzone")
    rc, stdout = common.create_subnet(access_zone_id=access_zone_id,
                                      name="subnet",
                                      ip_family="IPv4",
                                      svip="50.2.42.41",
                                      subnet_mask=22,
                                      subnet_gateway="50.2.43.254",
                                      network_interfaces="ens224")
    common.judge_rc(rc, 0, "create_subnet")
    return

def create_storage_pool():
    rc, stdout = common.create_storage_pool(name="storage_pool_1",
                                            type="FILE",
                                            node_pool_ids=1)
    common.judge_rc(rc, 0, "create_storage_pool")
    return

def create_volume():
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id("storage_pool_1")
    rc, stdout = common.create_volume(name="volume1",
                                      storage_pool_id=storage_pool_id,
                                      stripe_width="4",
                                      disk_parity_num="2",
                                      node_parity_num="1",
                                      replica_num="1",
                                      total_bytes=quota_common.FILE_SIZE_1G)
    common.judge_rc(rc, 0, "create_volume")
    return

def create_group_user():
    auth_provider_id = nas_common.get_auth_providers_id_list()
    if auth_provider_id == '':
        create_access_zone()
        auth_provider_id = nas_common.get_auth_providers_id_list()

    rc, stdout = common.create_auth_group(auth_provider_id, name="group")
    common.judge_rc(rc, 0, "create_auth_group")

    auth_provider_id = nas_common.get_auth_providers_id_list()
    msg = nas_common.get_auth_groups(auth_provider_id)
    primary_group_id = msg["result"]["auth_groups"][0]["id"]
    rc, stdout = common.create_auth_user(auth_provider_id, "user", "111111", primary_group_id)
    common.judge_rc(rc, 0, "create_auth_user")
    return

def makedir_no_check(path):
    cmd = 'mkdir -p %s' % path
    common.pscli_run_command(cmd, print_flag=False)
    return

def delete_volume():
    obj_volume = common.Volume()
    volume_id = obj_volume.get_volume_id("volume1")
    common.rm_exe(SYSTEM_IP_0, "/mnt/volume1/*")
    if volume_id is not None:
        rc, stdout = common.delete_volumes(ids=volume_id)
        common.judge_rc(rc, 0, "delete_volumes")
    return

def create_storage_volume():
    obj_storage = common.Storagepool()
    rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="storage_pool_1")
    if storage_pool_id is None:
        create_storage_pool()

    obj_volume = common.Volume()
    volume_id = obj_volume.get_volume_id("volume1")
    if volume_id is None:
        create_volume()
    return

def get_job_pending_name(job_name):
    name_pending_dict = {
        # "create_node_pools_proportion",  # 4
        # "create_node_pools_replica",     # 5
        "create_storage_pool": "CreateStoragePoolJob",
        # "update_node_pools",            # 6
        # "expand_storage_pool",          # 8
        "create_volumes": "CreateVolumesJob",
        # "create_client_auth",  # 13
        # "update_client_auth",  # 16
        # "delete_client_auth",  # 17
        # "create_access_zone",  # 21
        "enable_nas": "EnableNasJob",  # 34
        "create_subnet": "CreateSubnetJob",  # 24
        "add_vip_address_pool": "CreateIpAddressPoolJob",  # 27
        "create_auth_group": "CreateAuthGroupJob",  # 30
        "create_auth_user": "CreateAuthUserJob",  # 30
        # "create_ftp_export",  # 31
        # "create_nfs_export",  # 32
        # "create_smb_export",  # 33
        "update_vip_address_pool": "UpdateIpAddressPoolJob",  # 28
        "update_subnet": "UpdateSubnetJob",  # 25
        "delete_vip_address_pool": "DeleteIpAddressPoolJob",  # 29
        "delete_subnet": "DeleteSubnetJob",  # 26
        "update_access_zone": "UpdateAccessZoneJob",  # 22
        "disable_nas": "DisableNasJob",  # 34
        "delete_access_zone": "DeleteAccessZoneJob",  # 23
        "update_volume": "UpdateVolumeJob",  # 11
        "delete_volumes": "DeleteVolumesJob",  # 12
        # "delete_storage_pool",  # 9
    }
    return name_pending_dict[job_name]

def check_job_pending_phase(job_name, stage):
    cmd = "/home/parastor/conf/zk/bin/zkCli.sh ls /jobs/current_jobs"
    time_start = time.time()
    while True:
        rc, stdout = common.pscli_run_command(cmd)
        job_pending_name = stdout.strip().split("\n")[-1][1:-1]
        if get_job_pending_name(job_name) in job_pending_name:
            cmd1 = "/home/parastor/conf/zk/bin/zkCli.sh get /jobs/current_jobs/%s/0" % job_pending_name
            rc, stdout = common.pscli_run_command(cmd1)

            # job阶段转换的时候避免json格式化失败
            try:
                phase = common.json_loads(stdout.split("\n")[5])["phase"]
            except ValueError:
                log.info("json load error and retry")
                time.sleep(1)
                continue

            if phase == stage:
                break
        time_end = time.time()
        if (time_end - time_start) > 3600:
            raise Exception("check job pending timeout 1h")
        log.info("check phase %s s" % (time_end - time_start))
        time.sleep(5)
    return

def job_pscli(job_name):
    if job_name == "create_node_pools_proportion":
        rc, stdout = common.create_node_pools(name="NodePool_1",
                                              node_ids="1,2,3",
                                              stripe_width="4",
                                              disk_parity_num="2",
                                              node_parity_num="1",
                                              replica_num="1")
        common.judge_rc(rc, 0, "create")

    if job_name == "create_node_pools_replica":
        rc, stdout = common.create_node_pools(name="NodePool_1",
                                              node_ids="1,2,3",
                                              stripe_width="1",
                                              disk_parity_num="0",
                                              node_parity_num="1",
                                              replica_num="2")
        common.judge_rc(rc, 0, "create_node_pools_replica")

    if job_name in ["update_node_pools", "expand_storage_pool"]:
        make_fault_remove_node_no_rebuilding(get_config_job_fault.get_node_ip_remove_list()[0])
        make_fault_add_node(get_config_job_fault.get_node_ip_remove_list()[0])

    if job_name in ["create_storage_pool", "delete_storage_pool"]:
        obj_storage = common.Storagepool()
        rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="storage_pool_1")
        if storage_pool_id is None:
            create_storage_pool()
            rc, storage_pool_id = obj_storage.get_storagepool_id(storage_pool_name="storage_pool_1")

        delete_volume()
        rc, stdout = common.delete_storage_pool(id=storage_pool_id)
        common.judge_rc(rc, 0, "delete_storage_pool")

    if job_name in ["create_volumes", "update_volume", "delete_volumes"]:
        create_storage_volume()

        obj_volume = common.Volume()
        volume_id = obj_volume.get_volume_id("volume1")
        rc, stdout = common.update_volume(id=volume_id,
                                          total_bytes=quota_common.FILE_SIZE_2G)
        common.judge_rc(rc, 0, "update_volume")

        common.rm_exe(SYSTEM_IP_0, "/mnt/volume1/*")
        rc, stdout = common.delete_volumes(ids=volume_id)
        common.judge_rc(rc, 0, "delete_volumes")

    if job_name in ["create_client_auth", "update_client_auth", "delete_client_auth"]:
        ip = get_config.get_client_ip()
        obj_volume = common.Volume()
        volume_ids = obj_volume.get_volume_id("volume1")
        if volume_ids is None:
            create_volume()
            volume_ids = obj_volume.get_volume_id("volume1")

        rc, stdout = common.create_client_auth(ip=ip, volume_ids=volume_ids)
        common.judge_rc(rc, 0, "create_client_auth")

        obj_client = common.Clientauth()
        ip_update = get_config.get_client_ip(1)
        client_auth_id = obj_client.get_client_auth_id(ip, [volume_ids])
        rc, stdout = common.update_client_auth(client_auth_id, ip_update, volume_ids)
        common.judge_rc(rc, 0, "update_client_auth")

        client_auth_id = obj_client.get_client_auth_id(ip_update, [volume_ids])
        rc, stdout = common.delete_client_auth(ids=client_auth_id)
        common.judge_rc(rc, 0, "delete_client_auth")

    if job_name in ["create_access_zone", "update_access_zone", "delete_access_zone"]:
        create_storage_volume()
        access_id = get_access_zone_id_by_name("testzone")
        if access_id is None:
            create_access_zone()

        obj_node = common.Node()
        id_list = obj_node.get_nodes_id()
        node_ids_update = ",".join(str(i) for i in id_list[:-1])
        access_id = get_access_zone_id_by_name("testzone")
        rc, stdout = common.update_access_zone(id=access_id, node_ids=node_ids_update)
        common.judge_rc(rc, 0, "update_access_zone")

        delete_ftp_nfs_smb_export()
        rc, stdout = common.delete_access_zone(id=access_id)
        common.judge_rc(rc, 0, "delete_access_zone")

    if job_name in ["create_subnet", "update_subnet", "delete_subnet"]:
        create_storage_volume()
        access_zone_id = get_access_zone_id_by_name("testzone")
        if access_zone_id is None:
            create_access_zone()

        subnet_id = nas_common.get_subnets_ids_list()
        if subnet_id == '':
            create_subnet()
            subnet_id = nas_common.get_subnets_ids_list()

        rc, stdout = common.update_subnet(subnet_id, svip="50.2.42.45")
        common.judge_rc(rc, 0, "update_subnet")

        rc, stdout = common.delete_subnet(subnet_id)
        common.judge_rc(rc, 0, "delete_subnet")

    if job_name in ["add_vip_address_pool", "update_vip_address_pool", "delete_vip_address_pool"]:
        create_storage_volume()
        access_zone_id = get_access_zone_id_by_name("testzone")
        if access_zone_id is None:
            create_access_zone()

        id_list = nas_common.get_subnets_ids_list()
        if not id_list:
            create_subnet()
            id_list = nas_common.get_subnets_ids_list()

        vip_id = nas_common.get_vip_address_pool_ids_list()
        if vip_id == '':
            rc, stdout = common.add_vip_address_pool(subnet_id=id_list,
                                                     domain_name="www.vip.com",
                                                     vip_addresses="50.2.42.42-44",
                                                     supported_protocol="NAS",
                                                     allocation_method="DYNAMIC")
            common.judge_rc(rc, 0, "add_vip_address_pool")
            vip_id = nas_common.get_vip_address_pool_ids_list()

        rc, stdout = common.update_vip_address_pool(vip_id, load_balance_policy="LB_CONNECTION_COUNT")
        common.judge_rc(rc, 0, "update_vip_address_pool")

        rc, stdout = common.delete_vip_address_pool(vip_id)
        common.judge_rc(rc, 0, "delete_vip_address_pool")

        subnet_id = nas_common.get_subnets_ids_list()
        rc, stdout = common.delete_subnet(subnet_id)
        common.judge_rc(rc, 0, "delete_subnet")

    if job_name in ["create_ftp_export", "create_nfs_export", "create_smb_export",
                    "create_auth_group", "create_auth_user"]:
        create_storage_volume()

        access_id = get_access_zone_id_by_name("testzone")
        if access_id is None:
            create_access_zone()
            access_id = nas_common.get_access_zones_ids_list()

        rc, stdout = common.enable_nas(access_id)
        common.judge_rc(rc, 0, "enable_nas")

        auth_provider_id = nas_common.get_auth_providers_id_list()
        rc, stdout = common.create_auth_group(auth_provider_id, name="group")
        common.judge_rc(rc, 0, "create_auth_group")

        msg = nas_common.get_auth_groups(auth_provider_id)
        primary_group_id = msg["result"]["auth_groups"][0]["id"]
        rc, stdout = common.create_auth_user(auth_provider_id, "user", "111111", primary_group_id)
        common.judge_rc(rc, 0, "create_auth_user")

        access_zone_id = nas_common.get_access_zones_ids_list()
        export_path_ftp = "volume1:/ftp"
        makedir_no_check("/mnt/volume1/ftp")
        rc, stdout = common.create_ftp_export(access_zone_id, "user", export_path_ftp)
        common.judge_rc(rc, 0, "create_ftp_export")

        export_path_nfs = "volume1:/nfs"
        makedir_no_check("/mnt/volume1/nfs")
        rc, stdout = common.create_nfs_export(access_zone_id, "NFS", export_path_nfs)
        common.judge_rc(rc, 0, "create_nfs_export")

        export_path_smb = "volume1:/smb"
        makedir_no_check("/mnt/volume1/smb")
        rc, stdout = common.create_smb_export(access_zone_id, "SMB", export_path_smb)
        common.judge_rc(rc, 0, "create_smb_export")

        rc, stdout = common.disable_nas(access_id)
        common.judge_rc(rc, 0, "disable_nas")

        delete_ftp_nfs_smb_export()
        rc, stdout = common.delete_access_zone(id=access_id)
        common.judge_rc(rc, 0, "delete_access_zone")

    if job_name in ["enable_nas", "disable_nas"]:
        create_storage_volume()
        access_id = get_access_zone_id_by_name("testzone")
        if access_id is None:
            create_access_zone()
            access_id = get_access_zone_id_by_name("testzone")

        rc, stdout = common.enable_nas(access_id)
        common.judge_rc(rc, 0, "enable_nas")

        rc, stdout = common.disable_nas(access_id)
        common.judge_rc(rc, 0, "disable_nas")

    return
