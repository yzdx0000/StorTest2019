# -*-coding:utf-8 -*
import os
import utils_path
import log
import common
import get_config
import web_common
import prepare_clean

#######################################################
# 函数功能：界面自动化-----所有存储池的删除
# 脚本作者：duyuli
# 日期：2018-12-27
# testlink case: 3.0-51038,3.0-51043,3.0-51044
#######################################################

FILE_NAME = os.path.splitext(os.path.basename(__file__))[0]                  # 本脚本名字
storage_pool_name1 = "storage_pool_1"
storage_pool_name2 = "storage_pool_2"
volume_name_list = ["volume1", "volume2"]
service_type = "FILE"
disk_part_value_list = ["/dev/sdf", "/dev/sdg"]

def case():
    driver = web_common.init_web_driver()
    obj_web_storage_pool = web_common.Storage_Pool(driver)
    obj_web_file_system = web_common.File_System(driver)

    for volume in volume_name_list:
        common.rm_exe(get_config.get_web_ip(), os.path.join("/mnt", volume, "*"))

    # 删除文件系统
    obj_web_file_system.delete_volumes(volume_name_list)

    # 删除存储池
    obj_web_storage_pool.delete_storage_pool(storage_pool_name=storage_pool_name1)
    obj_web_storage_pool.delete_storage_pool(storage_pool_name=storage_pool_name2)

    # 恢复环境
    obj_web_storage_pool.create_storage_pool(name=storage_pool_name1, service_type=service_type,
                                             disk_all=False, disk_part_value_list=disk_part_value_list)
    obj_web_storage_pool.create_storage_pool(name=storage_pool_name2, service_type=service_type)

    obj_web_file_system.create_volume(volume_name_list[0], storage_pool_name1)
    obj_web_file_system.create_volume(volume_name_list[1], storage_pool_name2)

    web_common.quit_web_driver(driver)


def main():
    prepare_clean.test_prepare(FILE_NAME, env_check=False)
    case()
    prepare_clean.test_clean()
    log.info("%s succeed" % FILE_NAME)


if __name__ == '__main__':
    common.case_main(main)
