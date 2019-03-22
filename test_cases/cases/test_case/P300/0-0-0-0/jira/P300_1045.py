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
date 2018-08-13
@summary：
     缺陷自动化——导出smb目录命令的export_name参数未对特殊字符进行检查
@steps:
    1、添加ad认证、设置ntp
    2、创建访问区FILE_NAME
    3、创建导出目录
    4、使用pscli命令导出smb协议目录，检查报错信息
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
    '''
    在选定节点添加上访问分区
    '''
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
    """创建smb导出"""
    log.info(">4 创建smb导出")
    wrong_sp = "0~@#$%^*-=+?"     # `&()><切割shell命令造成中断的符号都不行
    wrong_smb_name_sn = ""
    detail_msg_err_lst = []
    rst_msg_err_lst = []
    # for str_e in wrong_sp:
    # Export name 'P300_1045+' can only consist of letters, numbers and underlines, begin with a letter.
    for str_e in wrong_sp:
        wrong_smb_name_sn = str_e + FILE_NAME
        msg_crt_export_smb = nas_common.create_smb_export(access_zone_id=id_az, export_name=wrong_smb_name_sn, export_path=path_create)
        id_smb = msg_crt_export_smb["result"]
        imp_info_lst.append(id_smb)
        dict_crt_rest = {(wrong_smb_name_sn,): msg_crt_export_smb["err_no"]}
        rst_msg_err_lst.append(dict_crt_rest)
        expcet_detail = "Export name '%s' can only consist of letters, numbers and underlines, begin with a letter." \
                        % wrong_smb_name_sn
        if str_e == "$":
            expcet_detail = "Export name can not be empty."
        cmp_detail = cmp(expcet_detail, str(msg_crt_export_smb["detail_err_msg"]))
        dict_crt_rest = {(wrong_smb_name_sn,): [cmp_detail, msg_crt_export_smb["detail_err_msg"], expcet_detail]}
        detail_msg_err_lst.append(dict_crt_rest)
    """删除本脚本创建的资源"""
    log.info(">5 删除访问区 %d，清理环境" % id_az)
    file_dele = nas_common.delete_file(path_create)
    """检查修改结果"""
    log.info(">6 验证结果，特殊字符应无法创建访问区")
    for info in detail_msg_err_lst:
        log.info(info)
    for rst in rst_msg_err_lst:
        log.info(rst)
    for rst in rst_msg_err_lst:
        common.judge_rc_unequal(rst.values()[0], 0, "wrong name: " + rst.keys().__str__())
    for info in detail_msg_err_lst:
        info_rc = "expect:\n" + info.values()[0][2] + "actrually:\n" + info.values()[0][1]
        common.judge_rc(info.values()[0][0], 0, info_rc)
    common.judge_rc(file_dele["err_no"], 0, "delete file" + file_dele["detail_err_msg"])
    log.info("case succeed! %s are illegal" % wrong_sp)
    return


def main():
    # prepare_clean.defect_test_prepare(FILE_NAME)

    prepare_clean.nas_test_prepare(FILE_NAME)
    case()
    prepare_clean.nas_test_clean()
    log.info("%s succeed!" % FILE_NAME)

    # oCnas服务比较特殊，不用检查


if __name__ == '__main__':
    common.case_main(main)
