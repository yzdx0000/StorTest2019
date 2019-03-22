# -*-coding:utf-8 -*
import os
import datetime

import utils_path
import config_common as this
import process_sys_conf as conf
import common
import quota_common
import upgrade_common
import log
import get_config
import prepare_clean

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]
sys_ip_list = get_config.get_allparastor_ips()


def case():
    base = this.Base(node_name="NodePool_1",
                     stor_name="storage_pool_1",
                     stripe_width=1,
                     disk_parity_num=0,
                     node_parity_num=1,
                     replica_num=2)

    http = conf.ProcessConf()
    bflag = base.check_if_installed()
    if bflag:
        base.uninstall_parastor()
    base.install_parastor()

    base.install_webui()
    http.http_connect_cluster()
    # 2、节点池配置
    base.create_node_pool()
    # 3、存储池配置
    base.create_stor_pool()
    # 启动系统
    base.start_system()
    # 4、文件系统配置
    volume_name_lst = ['test']
    base.create_volume(volume_name_lst)
    # 5、 资源管理器配置
    file_path = os.path.join("/mnt/test", "test1")
    quota_common.creating_dir(sys_ip_list[0], file_path)
    # 6、目录配额配置
    quota_common.create_one_quota(path='%s:/' % volume_name_lst[0],
                                  logical_quota_cal_type='QUOTA_LIMIT',
                                  logical_hard_threshold=20)

    # 7、访问管理->认证服务器->AD 配置
    base.create_ad(ad_name='AD')
    # 8、访问管理->认证服务器->LDAP 配置
    base.create_ldp(ldap_name='LADP')
    # 9、访问管理->认证服务器-->NIS配置
    base.create_nis(nis_name='NIS')
    # 10、访问区配置
    zone_name = 'PTEST'
    access_zone_id = base.create_zone(access_zone_name=zone_name)
    base.enable_nas(access_zone_id=access_zone_id, protocol_types='FTP,SMB')
    # 11、业务子网配置
    auth_provider_id = base.get_auth_provider_id_by_zone_name(zone_name)
    subnet_id = base.create_subnet(access_zone_id, subnet_name='PSTEST')
    base.create_vip_pool(subnet_id)
    # 12、用户/用户组配置
    group_id = base.create_auth_group(auth_provider_id, group_name='test ')
    base.create_auth_user(auth_provider_id, group_id, user_name='test')
    # 13、ACL策略配置
    base.update_acl(name='dac_nfs3_set_posix_acl', volue=2)
    base.update_acl(name='dac_treat_rwx', volue=1)
    # 14、协议管理->SMB配置
    smb_export_id = base.create_smb_export(access_zone_id, export_name='test', volume_name='test')
    base.add_smb_auth(smb_export_id, user_or_group_name='administrator', type='USER')
    # 15、协议管理-FTP配置
    base.create_ftp_export(access_zone_id, ftp_user_name='administrator', ftp_path='test')
    # 16、数据保护->文件->快照管理->快照配置
    base.open_snapshot()
    snap_name = "test"
    base.create_snapshot(snap_name=snap_name, path='test')
    # 17、数据保护->文件->快照管理->快照策略配置
    base.create_snapshot_strategy(strategy_name='test', volume='test')
    # 18、管理运维->任务配置->任务配置
    base.update_jobengine(type='CONCHK', enable_type='NONE')
    # 19、管理运维->任务配置->影响度配置
    base.create_jobengine_impact(job_name='test')
    # 20、管理运维->参数配置
    base.update_node_timeout(current_volue='172800000')
    # webUI断开连接，卸载parastor
    http.http_clean_connect()
    base.uninstall_parastor()
    # 收集配置信息
    current_time = datetime.datetime.now()
    currenttime_before = current_time.strftime('%y-%m-%d-%H-%M-%S')
    begin = conf.ProcessConf(file_name='config',
                             timestamp=currenttime_before)
    begin.process_diff()
    # 执行在线升级
    upgrade_common.online_upgrade()
    # 收集配置信息
    current_time = datetime.datetime.now()
    currenttime_after = current_time.strftime('%y-%m-%d-%H-%M-%S')
    begin = conf.ProcessConf(file_name='config',
                             timestamp=currenttime_after)
    begin.process_diff()
    # 比对升级前后配置信息
    begin = conf.ProcessConf(lef_timestamp=currenttime_before,
                             right_timestamp=currenttime_after)

    begin.process_diff()
    # 快照回滚
    snap_id = base.get_snapshot_id_by_name(snap_name)
    base.revert_snapshot(snap_id)


def main():
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.defect_test_prepare(FILE_NAME, env_check=False)
    log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
