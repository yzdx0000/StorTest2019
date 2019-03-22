# -*-coding:utf-8 -*
import os
import time

import utils_path
import common
import snap_common
import log
import get_config
import prepare_clean
import nas_common
import shell
import random
import json
"""
Author:liangxy
date 2018-08-15
@summary：
     缺陷自动化——导出nfs目录命令的export_name参数未对长度进行检查（脚本中增加特殊字符）
@steps:
    1、生成错误参数列表
    2、创建访问区FILE_NAME
    3、创建导出目录
    4、使用pscli命令导出nfs协议目录，检查报错信息
    5、清理环境，返回结果
@changelog：
    最后修改时间：
    修改内容：
"""

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]


def case():
    log.info("case begin")
    """节点列表"""
    ob_node = common.Node()
    case_node_id_lst = ob_node.get_nodes_id()

    """handle->节点id、客户端ip；添加后要删除的访问区"""
    case_id = random.choice(case_node_id_lst)
    case_ip = ob_node.get_node_ip_by_id(case_id)
    imp_info_lst = []
    log.info(">1 指定错误参数")
    wrong_sp = "0~@#$%^*-=+?"     # `&()><切割shell命令造成中断的符号都不行
    wrong_nfs_name_sn = ""
    str_lenth = 81
    wrong_nfs_name_nu = "a" * str_lenth
    err_msg_unit = []
    detial_cmp_lst = []
    log.info(">2 创建访问分区")
    msg_add_az = nas_common.create_access_zone(node_ids=case_id, name=FILE_NAME + "az")
    common.judge_rc(msg_add_az["err_no"], 0, "create az" + msg_add_az["detail_err_msg"])

    id_az = msg_add_az["result"]
    imp_info_lst.append(id_az)
    log.info("az id created： %d" % id_az)
    """创建目录"""
    log.info(">3 创建目录")

    get_volume_lst = get_config.get_volume_names()
    case_volume = random.choice(get_volume_lst)
    path_create = case_volume + ":/" + FILE_NAME
    msg_get_file = nas_common.get_file_list(case_volume + ":/")
    common.judge_rc(msg_get_file["err_no"], 0, "get file list" + msg_get_file["detail_err_msg"])
    for files in msg_get_file["result"]["files"]:
        if FILE_NAME == files["name"]:
            file_dele_p = nas_common.delete_file(path_create)
            common.judge_rc(file_dele_p["err_no"], 0, "first dele:" + FILE_NAME + file_dele_p["detail_err_msg"])
    msg_add_file = nas_common.create_file(path_create)
    common.judge_rc(msg_add_file["err_no"], 0, "create file" + msg_add_file["detail_err_msg"])
    """创建nfs导出"""
    log.info(">4 创建nfs导出")

    msg_crt_export_nfs_nu = nas_common.create_nfs_export(access_zone_id=id_az,
                                                         export_name=wrong_nfs_name_nu, export_path=path_create)
    dict_err = {(wrong_nfs_name_nu,): msg_crt_export_nfs_nu["err_no"]}
    err_msg_unit.append(dict_err)
    cmp_detail = "Export name '%s' length:81 exceed the max length:80" % wrong_nfs_name_nu.replace('\"', '')
    detial_cmp = cmp(cmp_detail, str(msg_crt_export_nfs_nu["detail_err_msg"]))
    detial_cmp_dict = {(wrong_nfs_name_sn,): [detial_cmp, msg_crt_export_nfs_nu["detail_err_msg"], cmp_detail]}
    detial_cmp_lst.append(detial_cmp_dict)
    for str_e in wrong_sp:
        wrong_nfs_name_sn = "\"" + str_e + FILE_NAME + "\""
        msg_crt_export_nfs = nas_common.create_nfs_export(access_zone_id=id_az, export_name=wrong_nfs_name_sn,
                                                          export_path=path_create)
        cmp_detail = "Export name '%s' can only consist of letters, numbers and underlines, begin with a letter." \
                     % wrong_nfs_name_sn.replace('\"', '')
        if "$" in str_e:
            cmp_detail = "Export name can not be empty."
        detial_cmp = cmp(cmp_detail, str(msg_crt_export_nfs["detail_err_msg"]))
        detial_cmp_dict = {(wrong_nfs_name_sn,): [detial_cmp, msg_crt_export_nfs["detail_err_msg"], cmp_detail]}
        detial_cmp_lst.append(detial_cmp_dict)
        id_nfs = msg_crt_export_nfs["result"]
        imp_info_lst.append(id_nfs)
        dict_err = {(wrong_nfs_name_sn,): msg_crt_export_nfs["err_no"]}
        err_msg_unit.append(dict_err)
    """删除本脚本创建的资源"""
    log.info(">5 删除访问区 %d，清理环境" % id_az)
    prepare_clean.nas_test_clean()
    file_dele = nas_common.delete_file(path_create)
    """检查修改结果"""
    log.info(">6 验证结果，含特殊字符的export name应无法导出nfs")
    for err in err_msg_unit:
        log.info("test rst:%s" % err)
    for detail_dict in detial_cmp_lst:
        log.info("detail:{}\n".format(detail_dict))
    # Export name '0P300_1035' can only consist of letters, numbers and underlines, begin with a letter.
    # $符号：Export name can not be empty.
    # 字符长度报错：Export name 'aaaaaaaaaaaaaaaaaaaaa
    # aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa' length:81 exceed the max length:80
    for err in err_msg_unit:
        common.judge_rc_unequal(err.values()[0], 0, "wrong name" + err.keys()[0].__str__())
    for detail_dict in detial_cmp_lst:
        info_rc = "\nwrong info: " + detail_dict.values()[0][1].__str__() + "\nexpect info: " + detail_dict.values()[0][2].__str__()
        common.judge_rc(detail_dict.values()[0][0], 0, info_rc)
    common.judge_rc(file_dele["err_no"], 0, "delete file" + file_dele["detail_err_msg"])
    log.info("case succeed!\n%s and %s are illegal" % (str(str_lenth), wrong_sp))
    return


def main():
    # prepare_clean.defect_test_prepare(FILE_NAME)

    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    log.info("%s succeed!" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
