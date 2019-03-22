# -*-coding:utf-8 -*
import os

import utils_path
import common
import s3_common
import log
import prepare_clean

####################################################################################
#
# Author: baorb
# date 2018-01-19
# @summary：
#    基本执行集测试。
# @steps:
#    s3的基础指令集包括：创建账户，创建证书，获取桶列表，创建桶，删除桶，获取对象列表，上传对象，下载对象，md5值检测，
#    复制对象到其他桶，下载复制对象，md5值检测，多段上传，取消多段上传，设置桶配额，验证桶配额是否起作用，get桶配额，取消桶配额，
#    设置同和对象的读acl，获取acl，验证acl是否成功,删除对象删除桶删除证书删除账户；
#
# @changelog：
####################################################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                 # 本脚本名字
ACCOUNT_EMAIL_LST = []
for i in range(2):
    ACCOUNT_EMAIL = FILE_NAME + str(i) + "@sugon.com"
    ACCOUNT_EMAIL_LST.append(ACCOUNT_EMAIL)


def case():
    log.info("1> 创建两个账户")
    i = 0
    account_id_lst = []
    for account_email in ACCOUNT_EMAIL_LST:
        i += 1
        account_name = FILE_NAME + '_account_%d' % i
        rc, account_id = s3_common.add_account(account_name, account_email, 0)
        common.judge_rc(rc, 0, "add account failed!!!")
        account_id_lst.append(account_id)
        """检查账户是否存在"""
        rc, stdout = s3_common.find_account(account_email)
        common.judge_rc(rc, 0, "find account %s failed!!!" % account_email)

    log.info("2> 每个账户添加账户信息")
    certificate_id_lst = []
    for account_id in account_id_lst:
        rc, certificate_id, certificate = s3_common.add_certificate(account_id)
        common.judge_rc(rc, 0, "add certificate failed!!!")
        certificate_id_lst.append(certificate_id)

    log.info("3> 获取桶")
    for certificate_id in certificate_id_lst:
        rc, stdout = s3_common.get_all_bucket(certificate_id)
        common.judge_rc(rc, 0, "get all bucket failed!!!")

    log.info("4> 创建两个桶")
    bucket_name_base = FILE_NAME + '_bucket'
    bucket_name_base = bucket_name_base.replace('_', '-')
    print 'bucket is %s' %bucket_name_base
    certificate_id_base = certificate_id_lst[0]
    rc, stdout = s3_common.add_bucket(bucket_name_base, certificate_id_base)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name_base)

    bucket_name_copy = FILE_NAME + '_bucket_copy'
    bucket_name_copy = bucket_name_copy.replace('_', '-')
    rc, stdout = s3_common.add_bucket(bucket_name_copy, certificate_id_base)
    common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name_copy)

    log.info("5> 再创建10个桶")
    bucket_name_lst_base = []
    for i in range(10):
        bucket_name = FILE_NAME + '_bucket_%d' % i
        bucket_name = bucket_name.replace('_', '-')
        rc, stdout = s3_common.add_bucket(bucket_name, certificate_id_base)
        common.judge_rc(rc, 0, "add bucket %s failed!!!" % bucket_name)
        bucket_name_lst_base.append(bucket_name)

    log.info("6> 检查10个桶是否都在")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id_base)
    common.judge_rc(rc, 0, "get bucket failed!!!")
    for bucket_name in bucket_name_lst_base:
        if bucket_name not in bucket_name_lst:
            common.except_exit("bucket %s create not OK" % bucket_name)
    else:
        log.info("all bucket is create")

    log.info("7> 删除10个桶")
    for bucket_name in bucket_name_lst_base:
        rc, stdout = s3_common.del_bucket(bucket_name, certificate_id_base)
        common.judge_rc(rc, 0, "delete bucket %s failed!!!" % bucket_name)

    log.info("8> 检查10个桶是否还存在")
    rc, bucket_name_lst = s3_common.get_all_bucket_name(certificate_id_base)
    common.judge_rc(rc, 0, "get bucket failed!!!")
    for bucket_name in bucket_name_lst_base:
        if bucket_name in bucket_name_lst:
            common.except_exit("bucket %s delete not OK" % bucket_name)
    else:
        log.info("all bucket is delete")

    log.info("9> 获取桶内所有对象")
    for bucket_name in bucket_name_lst:
        rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name, certificate_id_base)
        common.judge_rc(rc, 0, "get all object failed!!!")

    log.info("10> 上传对象10次")
    """创建10M文件"""
    file_path = '/tmp/s3testfile'
    rc, stdout = s3_common.create_file_m(file_path, 10)
    common.judge_rc(rc, 0, "create file %s failed!!!" % (file_path))
    object_name_lst_base = []
    for i in range(10):
        object_name = FILE_NAME + '_object_%d' % i
        rc, stdout = s3_common.add_object(bucket_name_base, object_name, file_path, certificate_id_base)
        common.judge_rc(rc, 0, "add object %s failed!!!" % object_name)
        object_name_lst_base.append(object_name)

    rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name_base, certificate_id_base)
    common.judge_rc(rc, 0, "get all object in bucket %s failed!!!" % bucket_name_base)
    for object_name in object_name_lst_base:
        if object_name not in object_name_lst:
            common.except_exit("object %s is not put!!!" % object_name)
    else:
        log.info("all object put success")

    log.info("11> 下载10个对象")
    file_down_path_lst = []
    for object_name in object_name_lst_base:
        file_down_path = os.path.join("/tmp", object_name+'down')
        rc, stdout = s3_common.download_object(bucket_name_base, object_name, file_down_path, certificate_id_base)
        common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)
        file_down_path_lst.append(file_down_path)

    log.info("12> 检测MD5值")
    rc, base_file_md5 = s3_common.get_file_md5(file_path)
    common.judge_rc(rc, 0, "get file %s failed!!!" % (file_path))

    for file in file_down_path_lst:
        rc, file_md5 = s3_common.get_file_md5(file)
        common.judge_rc(rc, 0, "get file %s failed!!!" % (file))
        common.judge_rc(base_file_md5, file_md5, "file md5 is not same")

    log.info("13> 复制10个对象到其他桶中")
    object_name_lst_cp = []
    for object_name in object_name_lst_base:
        dest_object_name = object_name + '_copy'
        rc, stdout = s3_common.cp_object(bucket_name_copy, dest_object_name,
                                         certificate_id_base, bucket_name_base, object_name)
        common.judge_rc(rc, 0, "cp src_bucket %s src_obj %s to dest_bucket %s dest_obj %s failed!!!"
                        % (bucket_name_base, object_name, bucket_name_copy, dest_object_name))
        object_name_lst_cp.append(dest_object_name)

    rc, object_name_lst = s3_common.get_all_object_in_bucket(bucket_name_copy, certificate_id_base)
    common.judge_rc(rc, 0, "get all object in becket %s failed!!!" % bucket_name_copy)
    for object_name_cp in object_name_lst_cp:
        if object_name_cp not in object_name_lst:
            common.except_exit("object %s cp failed!!!" % object_name_cp)
    log.info("all object cp success")

    log.info("14> 下载10个复制的对象")
    file_down_path_cp_lst = []
    for object_name in object_name_lst_cp:
        file_down_path = os.path.join("/tmp", object_name+'down')
        rc, stdout = s3_common.download_object(bucket_name_copy, object_name, file_down_path, certificate_id_base)
        common.judge_rc(rc, 0, "download object %s failed!!!" % object_name)
        file_down_path_cp_lst.append(file_down_path)

    log.info("15> 复制的对象下载后MD5校验")
    for file in file_down_path_cp_lst:
        rc, file_md5 = s3_common.get_file_md5(file)
        common.judge_rc(rc, 0, "get file %s failed!!!" % (file))
        common.judge_rc(base_file_md5, file_md5, "node %s file md5 is not same")

    log.info("16> 设置桶的配额200M")
    quota_200m = 209715200
    rc, stdout = s3_common.update_bucket_quota(bucket_name_base, certificate_id_base, quota_200m)
    common.judge_rc(rc, 0, "update bucket %s quota %s failed!!!" % (bucket_name_base, quota_200m))

    log.info("17> 获取桶的配额")
    rc, bucket_quota = s3_common.get_bucket_quota(bucket_name_base, certificate_id_base)
    common.judge_rc(rc, 0, "get bucket %s quota failed!!!" % bucket_name_base)
    common.judge_rc(int(bucket_quota), quota_200m, "bucket %s quota is not right!!!")

    log.info("18> 上传一个大于配额的文件")
    """生成一个210M文件"""
    file_quota_path = "/tmp/s3file_quota"
    rc, stdout = s3_common.create_file_m(file_quota_path, 210)
    common.judge_rc(rc, 0, "create file %s")

    object_name_quota = FILE_NAME + '_object_quota'
    rc, stdout = s3_common.add_object_over_quota(bucket_name_base, object_name_quota,
                                                 file_quota_path, certificate_id_base)
    if 'Insufficient Storage Space' not in stdout:
        common.except_exit("over quota file put success!!!")

    log.info("19> 取消配额")
    rc, stdout = s3_common.update_bucket_quota(bucket_name_base, certificate_id_base, 0)
    common.judge_rc(rc, 0, "update bucket %s quota 0 failed!!!" % bucket_name_base)

    log.info("20> 再次上传文件")
    rc, stdout = s3_common.add_object(bucket_name_base, object_name_quota, file_quota_path, certificate_id_base)
    common.judge_rc(rc, 0, "put file %s failed!!!" % file_quota_path)

    log.info("21> 设置桶的acl")
    rc, stdout = s3_common.set_bucket_acl(bucket_name_base, certificate_id_base, account_id_lst[0],
                                          ACCOUNT_EMAIL_LST[0], account_id_lst[1], ACCOUNT_EMAIL_LST[1], 'FULL_CONTROL')
    common.judge_rc(rc, 0, "set bucket %s acl failed!!!" % bucket_name_base)

    rc, account_acl_id_lst, account_acl_email_lst, permission_lst = \
        s3_common.get_bucket_acl(bucket_name_base, certificate_id_base)
    common.judge_rc(rc, 0, "get bucket %s failed!!!" % bucket_name_base)
    if str(account_id_lst[1]) not in account_acl_id_lst:
        common.except_exit("bucket %s acl account id is error!!!" % bucket_name_base)
    if ACCOUNT_EMAIL_LST[1] not in account_acl_email_lst:
        common.except_exit("bucket %s acl account email is error!!!" % bucket_name_base)
    if 'FULL_CONTROL' not in permission_lst:
        common.except_exit("bucket %s acl permission is error!!!" % bucket_name_base)

    log.info("22> 设置对象的acl")
    rc, stdout = s3_common.set_object_acl(bucket_name_base, object_name_lst_base[0],
                                          certificate_id_base, account_id_lst[0], ACCOUNT_EMAIL_LST[0],
                                          account_id_lst[1], ACCOUNT_EMAIL_LST[1], 'FULL_CONTROL')
    common.judge_rc(rc, 0, "set bucket %s object %s acl failed!!!" % (bucket_name_base, object_name_lst_base[0]))

    rc, account_acl_id_lst, account_acl_email_lst, permission_lst = \
        s3_common.get_object_acl(bucket_name_base, object_name_lst_base[0], certificate_id_base)
    common.judge_rc(rc, 0, "get bucket %s object %s failed!!!" % (bucket_name_base, object_name_lst_base[0]))
    if str(account_id_lst[1]) not in account_acl_id_lst:
        common.except_exit("bucket %s object %s acl account id is error!!!"
                           % (bucket_name_base, object_name_lst_base[0]))
    if ACCOUNT_EMAIL_LST[1] not in account_acl_email_lst:
        common.except_exit("bucket %s object %s acl account email is error!!!"
                           % (bucket_name_base, object_name_lst_base[0]))
    if 'FULL_CONTROL' not in permission_lst:
        common.except_exit("bucket %s object %s acl permission is error!!!"
                           % (bucket_name_base, object_name_lst_base[0]))

    log.info("23> 删除下载的对象")
    for file_down_path_cp in file_down_path_cp_lst:
        cmd = "rm -rf %s" % file_down_path_cp
        common.run_command_shot_time(cmd)
    for file_down_path in file_down_path_lst:
        cmd = "rm -rf %s" % file_down_path
        common.run_command_shot_time(cmd)


def main():
    for i in range(10000):
        log.info('**********************this is num %s begin to run***************' % i) 
        prepare_clean.s3_test_prepare(FILE_NAME, ACCOUNT_EMAIL_LST)
        case()
        prepare_clean.s3_test_clean(ACCOUNT_EMAIL_LST)
        log.info('%s succeed!' % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
