# -*-coding:utf-8 -*

#######################################################
# 脚本作者：duyuli
# 脚本说明：混和阈值通用循环脚本,执行前请先调用创建用户组和用户的脚本，可以节省总的循环时间
#######################################################

import os
import time
import random
import commands

import utils_path
import common
import quota_common
import log


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
flag = 0   # 手动操作，1为手动设定（3层目录），0为自动设定（64层目录）
count = 0  # 时间计数，超时
base_volume_path = quota_common.BASE_QUOTA_PATH
auth_id = quota_common.get_auth_provider_id_with_access_zone_name("testzone")
log_path = "/home/StorTest/test_cases/log/case_log"
path_list_all = []
path_root = "/"
path_a = "/a"
path_b = "/b"
path_c = "/c"
path_a_b = "/a/b"
path_a_b_c = "/a/b/c"
path_much = "/01/02/03/04/05/06/07/08/09/10/11/12/13/14/15/16/17/18/19/20/21/22/23/24/25/26/27/28/29/30/31/32\
/33/34/35/36/37/38/39/40/41/42/43/44/45/46/47/48/49/50/51/52/53/54/55/56/57/58/59/60/61/62/63/64"

# path多次调用，写在前面
path_list_all.append("/")
for i in range(3, 195, 3):
    path_list_all.append(path_much[:i])
if flag == 0:
    path_list = random.sample(path_list_all, 5)
else:
    path_list = [path_a, path_a_b, path_a_b_c]

# 创建配额时会改变path_list,后续还需要调用
path_list_choice = path_list
quota_size = [quota_common.FILE_SIZE_1G, quota_common.FILE_SIZE_2G, quota_common.FILE_SIZE_3G]
quota_inode = [500, 1000, 1500]


def curculate_total_size(node_ip, dir_path):
    # 计算文件夹下所有文件的大小，包括子目录下的(不包括文件夹大小)
    total_file_size = 0
    cmd1 = "cd %s; ls -lR|grep '^-'" % dir_path
    rc, stdout = common.run_command(node_ip, cmd1)
    for file_size in stdout.strip().split("\n"):
        size = int(file_size.strip().split()[4])
        total_file_size = size + total_file_size
    return total_file_size


def qmgr_quota_dump():
    # 在出现一直是scanning状态时，收集日志
    time_now = time.strftime("%y-%m-%d-%H-%M-%S")
    ob_node = common.Node()
    node_id_lst = ob_node.get_nodes_id()
    for node_id in node_id_lst:
        cmd = ("cd /home/parastor/tools;./nWatch -t oPara -i %s -c "
               "QMGR#dump_dirquota -a \"outfile=%s/%s_dump_dirquota.log\"" %
               (node_id, log_path, time_now))
        rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
        common.judge_rc(rc, 0, "cmd = %s\nstdout = %s" % (cmd, stdout), exit_flag=False)

        if "qmgr is not here" in stdout:
            continue
        if "dirqrule has dump into file" in stdout:
            cmd1 = "ifconfig ens160 | grep \"inet \" | awk '{ print $2}'"
            rc, stdout1 = common.run_command_shot_time(cmd1)
            ip_local = stdout1.strip()
            cmd2 = "scp %s/%s_dump_dirquota.log %s:%s" % (log_path, time_now, ip_local, log_path)
            common.run_command(quota_common.CLIENT_IP_1, cmd2)
            break
        if node_id == node_id_lst[-1] and "qmgr is not here" in stdout:
            log.info("###   QMGR#dump_dirquota error")
            raise Exception("QMGR#dump_dirquota error")
        return


def check_quota_work():
    # 检查配额为work状态
    log.info("check quota state work")
    global count
    count = count + 1
    if count == 60:  # 2分钟则超时
        log.info("###   check quota state error over 2min!!!")
        qmgr_quota_dump()
        raise Exception("check quota state error over 2min")
    quota_list = get_quotas_list()

    for quota in quota_list:
        if quota["state"] == "QUOTA_WORK":
            continue
        else:
            time.sleep(2)
            check_quota_work()
    return


def set_mix_nest(quota_dic):
    choose_two_for_quota_list = random.sample(quota_dic.keys(), 5)
    quota_dic[choose_two_for_quota_list[0]] = 1
    quota_dic[choose_two_for_quota_list[1]] = 1
    quota_dic[choose_two_for_quota_list[2]] = 1
    quota_dic[choose_two_for_quota_list[3]] = 1
    quota_dic[choose_two_for_quota_list[4]] = 1
    return quota_dic


def get_quotas_list():
    rc, stdout = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, 'get_all_quota_info failed')
    list_quotas = stdout["result"]["quotas"]
    return list_quotas


def print_quota_log_info():
    """
    author:liyi
    date:2018-9-29
    description：打印配额信息
    :return:
    """
    rc, check_result = quota_common.get_all_quota_info()
    common.judge_rc(rc, 0, "get quota failed")
    quotas_info = check_result["result"]["quotas"]
    quota_id_list = quota_common.get_quota_id_list()
    log.info("###混合配额%s组合信息###" % quota_id_list)
    for quota in quotas_info:
        quota_path_info = quota["path"]
        if quota["user_type"] == "USERTYPE_NONE":
            if quota["filenr_hard_threshold"] != 0:
                quota_threshold = quota["filenr_hard_threshold"]
                log.info("###path:%s\t配额规则：普通：inode硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_soft_threshold"] != 0:
                quota_threshold = quota["filenr_soft_threshold"]
                log.info("###path:%s\t配额规则：普通：inode软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_suggest_threshold"] != 0:
                quota_threshold = quota["filenr_suggest_threshold"]
                log.info("###path:%s\t配额规则：普通：inode建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_hard_threshold"] != 0:
                quota_threshold = quota["logical_hard_threshold"]
                log.info("###path:%s\t配额规则：普通：逻辑硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_soft_threshold"] != 0:
                quota_threshold = quota["logical_soft_threshold"]
                log.info("###path:%s\t配额规则：普通：逻辑软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_suggest_threshold"] != 0:
                quota_threshold = quota["logical_suggest_threshold"]
                log.info("###path:%s\t配额规则：普通：逻辑建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))

        if quota["user_type"] == "USERTYPE_USER":
            if quota["filenr_hard_threshold"] != 0:
                quota_threshold = quota["filenr_hard_threshold"]
                log.info("###path:%s\t配额规则：用户：inode硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_soft_threshold"] != 0:
                quota_threshold = quota["filenr_soft_threshold"]
                log.info("###path:%s\t配额规则：用户：inode软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_suggest_threshold"] != 0:
                quota_threshold = quota["filenr_suggest_threshold"]
                log.info("###path:%s\t配额规则：用户：inode建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_hard_threshold"] != 0:
                quota_threshold = quota["logical_hard_threshold"]
                log.info("###path:%s\t配额规则：用户：逻辑硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_soft_threshold"] != 0:
                quota_threshold = quota["logical_soft_threshold"]
                log.info("###path:%s\t配额规则：用户：逻辑软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_suggest_threshold"] != 0:
                quota_threshold = quota["logical_suggest_threshold"]
                log.info("###path:%s\t配额规则：用户：逻辑建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))

        if quota["user_type"] == "USERTYPE_GROUP":
            if quota["filenr_hard_threshold"] != 0:
                quota_threshold = quota["filenr_hard_threshold"]
                log.info("###path:%s\t配额规则：用户组：inode硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_soft_threshold"] != 0:
                quota_threshold = quota["filenr_soft_threshold"]
                log.info("###path:%s\t配额规则：用户组：inode软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["filenr_suggest_threshold"] != 0:
                quota_threshold = quota["filenr_suggest_threshold"]
                log.info("###path:%s\t配额规则：用户组：inode建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_hard_threshold"] != 0:
                quota_threshold = quota["logical_hard_threshold"]
                log.info("###path:%s\t配额规则：用户组：逻辑硬阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_soft_threshold"] != 0:
                quota_threshold = quota["logical_soft_threshold"]
                log.info("###path:%s\t配额规则：用户组：逻辑软阈值\t阈值：%s" % (quota_path_info, quota_threshold))
            if quota["logical_suggest_threshold"] != 0:
                quota_threshold = quota["logical_suggest_threshold"]
                log.info("###path:%s\t配额规则：用户组：逻辑建议阈值\t阈值：%s" % (quota_path_info, quota_threshold))


def check_quota_right():
    # 查询配额前等待获取完全
    log.info("wait 20s before get quota ")
    time.sleep(20)
    print_quota_log_info()
    # 检查配额是否触发阈值
    list_quotas = get_quotas_list()
    for quota in list_quotas:
        quota_path = base_volume_path + quota["path"].split(":")[1]
        filenr_hard_threshold = quota["filenr_hard_threshold"]
        filenr_soft_threshold = quota["filenr_soft_threshold"]
        filenr_soft_threshold_over_time = quota["filenr_soft_threshold_over_time"]
        filenr_used_nr = quota["filenr_used_nr"]

        logical_hard_threshold = quota["logical_hard_threshold"]
        logical_soft_threshold = quota["logical_soft_threshold"]
        logical_soft_threshold_over_time = quota["logical_soft_threshold_over_time"]
        logical_used_capacity = quota["logical_used_capacity"]

        # 检查软阈值
        if (filenr_soft_threshold != 0 and filenr_soft_threshold_over_time != '0') or \
           (logical_soft_threshold != 0 and logical_soft_threshold_over_time != '0'):
            log.info("check soft quota sleep 60s")
            time.sleep(40)
            cmd = ("cd %s; su quota_user -c \"dd if=/dev/zero of=file bs=1M count=1\";") % quota_path
            rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
            if "No space left on device" in stdout:
                log.info("soft quota check right")
            else:
                time.sleep(5)
                get_quotas_list()
                log.info("### quota soft check error path=%s !!!" % quota_path)
                raise Exception("quota soft check error path=%s" % quota_path)

        # 检查硬阈值之前测试truncate扩大文件
        if logical_hard_threshold != 0 and logical_used_capacity == logical_hard_threshold:
            cmd = ("cd %s; su quota_user -c \"truncate -s 100M file_1\";") % quota_path
            rc, stdout = common.run_command(quota_common.CLIENT_IP_1, cmd)
            if "File too large" or "No space left on device" in stdout:
                log.info("file truncate check right")
            else:
                time.sleep(5)
                get_quotas_list()
                log.info("### file truncate error path=%s !!!" % quota_path)
                raise Exception("file truncate error path=%s" % quota_path)

        # 检查硬阈值
        if (filenr_hard_threshold != 0 and filenr_used_nr > filenr_hard_threshold) or \
           (logical_hard_threshold != 0 and logical_used_capacity > logical_hard_threshold):
            get_quotas_list()
            log.info("### hard threshlod check error quota path=%s !!!" % quota_path)
            raise Exception("quota hard check error")
        else:
            log.info("quota hard threshlod check right")
    quota_id_list = quota_common.get_quota_id_list()
    log.info("###混合配额执行成功:规则号为：%s###\n" % quota_id_list)
    return


def executing_case():
    log.info("（2）executing_case")
    '''
    1、测试执行
    2、结果检查
    '''
    # 多客户端写文件到3文件夹
    # for i in {1..2000}; do dd if=/dev/zero of=file_10.2.42.151_b_$i bs=1 count=1; done
    # ll | grep "^-" | wc -l
    # ./nWatch -t oPara -i 1 -c QMGR#chkmult_client -a "ruleid="
    quota_common.chkmult_client_all_dir_on_path(path_much)   # 写入文件前查chkmult

    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_3,
                                                            base_volume_path + path_list_choice[0],
                                                            1, 1100, "quota_user_name", "quota_user")
    cmd = ("cd %s; for i in {1..510}; do su quota_user -c \"touch file_$i\"; done") % \
          (base_volume_path + path_list_choice[0])
    common.run_command(quota_common.CLIENT_IP_3, cmd)

    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_2,
                                                            base_volume_path + path_list_choice[1],
                                                            1, 1100, "a_b_user", "quota_other_user")
    cmd1 = ("cd %s; for i in {1..510}; do su quota_other_user -c \"touch file_$i\"; done") % \
           (base_volume_path + path_list_choice[1])
    common.run_command(quota_common.CLIENT_IP_2, cmd1)

    quota_common.creating_files_by_designated_user_or_group(quota_common.CLIENT_IP_1,
                                                            base_volume_path + path_list_choice[2],
                                                            1, 1100, "quota_user", "quota_user")
    cmd1 = ("cd %s; for i in {1..510}; do su quota_user -c \"touch file_$i\"; done") % \
           (base_volume_path + path_list_choice[2])
    common.run_command(quota_common.CLIENT_IP_1, cmd1)

    check_quota_right()


#######################################################
# 函数功能：
# 函数入参：
# 函数返回值：
#######################################################
def preparing_environment():
    log.info("（1）preparing_environment")
    '''
    1、下发配额相关的配置
    2、创建配额测试相关的目录和文件
    '''
    if flag == 0:
        quota_common.creating_dir(quota_common.CLIENT_IP_1, base_volume_path + path_much)
        cmd = "chmod -R 777 %s" % base_volume_path
        common.run_command(quota_common.CLIENT_IP_1, cmd)
    else:
        quota_common.creating_dir(quota_common.CLIENT_IP_1, base_volume_path + path_a_b_c)

    # 设定组合类型
    quota_dic = {
        "quota_logical_hard":       0,  "quota_logical_soft":       0, "quota_logical_suggest":       0,
        "quota_logical_user_hard":  0,  "quota_logical_user_soft":  0, "quota_logical_user_suggest":  0,
        "quota_logical_group_hard": 0,  "quota_logical_group_soft": 0, "quota_logical_group_suggest": 0,
        "quota_inode_hard":         0,  "quota_inode_soft":         0, "quota_inode_suggest":         0,
        "quota_inode_user_hard":    0,  "quota_inode_user_soft":    0, "quota_inode_user_suggest":    0,
        "quota_inode_group_hard":   0,  "quota_inode_group_soft":   0, "quota_inode_group_suggest":   0}

    if flag == 0:
        quota_dic = set_mix_nest(quota_dic)

# 针对目录配置逻辑空间阈值的配额
    global path_list
    if quota_dic["quota_logical_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=random.choice(quota_size))
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_soft_threshold=random.choice(quota_size),
                                                         logical_grace_time=60)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=536870912)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

# 针对目录配置inode阈值的配额
    if quota_dic["quota_inode_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=random.choice(quota_inode))
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_soft_threshold=random.choice(quota_inode),
                                                         filenr_grace_time=60)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=500)
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

# 针对目录配置用户inode阈值的配额
    if quota_dic["quota_inode_user_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=random.choice(quota_inode),
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_user_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))

        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_soft_threshold=random.choice(quota_inode),
                                                         filenr_grace_time=60,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_user_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=500,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

# 针对目录配置用户组inode阈值的配额
    if quota_dic["quota_inode_group_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_hard_threshold=random.choice(quota_inode),
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_group_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_soft_threshold=random.choice(quota_inode),
                                                         filenr_grace_time=60,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_inode_group_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         filenr_quota_cal_type='QUOTA_LIMIT',
                                                         filenr_suggest_threshold=500,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

# 针对目录配置用户空间阈值的配额
    if quota_dic["quota_logical_user_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=random.choice(quota_size),
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_user_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_soft_threshold=random.choice(quota_size),
                                                         logical_grace_time=60,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_user_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=536870912,
                                                         user_type='USERTYPE_USER',
                                                         user_or_group_name='quota_user')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

# 针对目录配置用户组空间阈值的配额
    if quota_dic["quota_logical_group_hard"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_hard_threshold=random.choice(quota_size),
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_group_soft"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_soft_threshold=random.choice(quota_size),
                                                         logical_grace_time=60,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    if quota_dic["quota_logical_group_suggest"] == 1:
        path_choice = random.sample(path_list, 1)
        path_list = list(set(path_list).difference(set(path_choice)))
        rc, check_result = quota_common.create_one_quota(path=('%s:/%s' % (quota_common.VOLUME_NAME, path_choice[0])),
                                                         auth_provider_id=auth_id,
                                                         logical_quota_cal_type='QUOTA_LIMIT',
                                                         logical_suggest_threshold=536870912,
                                                         user_type='USERTYPE_GROUP',
                                                         user_or_group_name='quota_group')
        common.judge_rc(rc, 0, "create  quota failed", exit_flag=False)

    check_quota_work()
    return


def cleaning_environment():
    log.info("（*）cleaning_environment（*）")
    '''
    1、删除所有配额相关的配置信息
    2、删除所有配额测试相关的文件和目录
    '''
    quota_common.delete_all_quota_config()
    # 清空目录
    log.info("\t[ delete_all_files_and_dir ]")
    rc, stdout = common.rm_exe(quota_common.CLIENT_IP_1, os.path.join(base_volume_path, '*'))
    if stdout != "":
        log.info("### rm -rf error !!!")
        raise Exception("rm -rf error")
    return


#######################################################
# 函数功能：本用例入口函数
# 函数入参：无
# 函数返回值：无
#######################################################
def quota_main():
    file_name = os.path.basename(__file__)
    file_name = os.path.splitext(file_name)[0]
    log_file_path = log.get_log_path(file_name)
    log.init(log_file_path, True)
    cleaning_environment()
    preparing_environment()
    executing_case()

    # 单独调用
    # check_quota_right()
    # curculate_total_size(quota_common.CLIENT_IP_1, base_volume_path + path_a_b)
    return


if __name__ == '__main__':
    common.case_main(quota_main)