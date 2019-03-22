#!usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
:author: Liu he
:Description:
@file: xstor_web_com.py 
@time: 2019/03/18 
"""

import os
import time
from multiprocessing import Process
import threading
from selenium import webdriver
from selenium.webdriver import ActionChains  # double_click
from selenium.webdriver.support.select import Select  # 下来菜单选择
from selenium.webdriver.support.wait import WebDriverWait  # 智能等待
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException  # 导入指定异常

import log
import get_config
import common
import web_common

web_base = web_common.Web_Base
first_level_label = web_common.First_Level_Label  # 导入父类


class AccessManage(first_level_label):
    """访问管理"""
    def locate_access_zone(self):
        """访问管理--->访问分区"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_accesszone']/a", check_by_click=True).click()
        return

    def locate_subnet(self):
        """访问管理--->业务子网"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_subnet']/a", check_by_click=True).click()
        return

    def create_access_zone(self, name, auth_provider_name=None, nodes_all=False, node_hostname_list=None,
                           enable_nas=False, nfs=False, smb=False, ftp=False, s3=False, san=False):
        """
        author:liuhe
        :param s3:
        :param ftp:
        :param smb:
        :param nfs:
        :param enable_nas:
        :param name: 访问分区名称
        :param auth_provider_name: 认证服务器
        :param nodes_all: 是否全选
        :param node_hostname_list: 指定选择的节点  eg ["vm151", "vm152", "vm153"]
        :return:
        tips: 若要使能nas，请指明nfs=True，smb=True等等
        """
        log.info("begin to create access zone")

        # 定位到访问分区
        self.locate_access_zone()

        # 单击创建
        self.find_element_by_xpath("//*[@id='access_zone_bn_create']/i", check=True).click()

        # 输入name
        self.find_element_by_xpath("//*[@id='ofs_access_zone_create_name_id']", js_send_keys=name)

        # 选择认证服务器
        if auth_provider_name:
            self.select_by_text("//*[@id='ofs_access_zone_create_auth_provider_id']", auth_provider_name)

        # 点开节点列表
        self.find_element_by_xpath("//*[@id='ofs_access_zone_create_node_list']/div/i").click()

        # 选择节点
        if nodes_all:
            for i in range(10):  # 避免全选点击后子项未加载完成的情况
                if len(self.driver.find_elements_by_xpath("//*[@type='checkbox']")) > 2:
                    self.find_element_by_xpath("//*[@title='节点名称']/../..//s").click()
                    break
                time.sleep(0.5)

        if node_hostname_list:
            for hostname in node_hostname_list:
                self.find_element_by_xpath("//*[@title='%s']/../..//s" % hostname).click()

        # 确定节点
        self.find_element_by_xpath("//*[@id='accessZoneCreateNodeListWindow-btn-0']").click()

        # 回到上层窗口下一步
        self.find_element_by_xpath("//*[@id='access_zone_create_window_step1-btn-0']").click()

        smb_xpath = "//*[@id='protocolSetting-nas-smb-box']"
        nfs_xpath = "//*[@id='protocolSetting-nas-nfs-box']"
        ftp_xpath = "//*[@id='protocolSetting-nas-ftp-box']"
        # s3_xpath = "//*[@id='protocolSetting-object-s3-box']"
        san_xpath = "//*[@id='protocolSetting-block-iSCSI-box']"

        smb_obj = self.find_element_by_xpath(smb_xpath)
        nfs_obj = self.find_element_by_xpath(nfs_xpath)
        ftp_obj = self.find_element_by_xpath(ftp_xpath)
        # s3_obj = self.find_element_by_xpath(s3_xpath)
        san_obj = self.find_element_by_xpath(san_xpath)

        if nfs or smb or ftp or s3:
            enable_nas = True

        # 无nas
        if enable_nas is False:
            if smb_obj.is_selected():
                self.execute_script_click(dom=smb_obj)  # box 类型反选

            if nfs_obj.is_selected():
                self.execute_script_click(dom=nfs_obj)

            if ftp_obj.is_selected():
                self.execute_script_click(dom=ftp_obj)
            #
            # if s3_obj.is_selected():
            #     self.execute_script_click(dom=s3_obj)

        # 有部分或全部nas
        if smb:
            if smb_obj.is_selected() is False:
                self.execute_script_click(xpath=smb_xpath)
        else:
            if smb_obj.is_selected():
                self.execute_script_click(xpath=smb_xpath)

        if nfs:
            if nfs_obj.is_selected() is False:
                self.execute_script_click(xpath=nfs_xpath)
        else:
            if nfs_obj.is_selected():
                self.execute_script_click(xpath=nfs_xpath)

        if ftp:
            if ftp_obj.is_selected() is False:
                self.execute_script_click(xpath=ftp_xpath)
        else:
            if ftp_obj.is_selected():
                self.execute_script_click(xpath=ftp_xpath)
        if san:  # 如果判断 san 是否为true
            if san_obj.is_selected() is False:  # 获取默认san 勾选状态，是否勾选，
                self.execute_script_click(xpath=san_xpath)  # 如果默认san 没勾选，则勾选
        else:
            if san_obj.is_selected():
                self.execute_script_click(xpath=san_xpath)
        # if s3:
        #     if s3_obj.is_selected() is False:
        #         self.execute_script_click(xpath=s3_xpath)
        # else:
        #     if s3_obj.is_selected():
        #         self.execute_script_click(xpath=s3_xpath)

        # 单击完成
        self.find_element_by_xpath("//*[@id='access_zone_create_window_step2-btn-1']").click()

        # 单击确定创建  starts-with  contains
        self.find_element_by_xpath("//div[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 等待创建完成
        log.info("wait enable nas")
        self.check_element_done(time_out=600, check_by_click=True)
        return name

    def delete_access_zone(self, name):
        """
         auther:liuhe
        :param name:
        :return:
        """
        log.info("begin to delete access zone")

        # 定位到访问分区
        self.locate_access_zone()

        is_enable_nas_start_stat = False

        is_enable_san_start_stat = False  # 定义初始san状态

        # 勾选待删除的访问分区
        self.find_element_by_xpath("//div[starts-with(text(),'%s')]/../../div/label/s" % name, check=True).click()

        # 点击服务设置
        self.find_element_by_xpath("//*[@id='access_zone_bn_protocol_setting']").click()

        # smb nfs ftp s3 等服务置为空
        smb_xpath = "//*[@id='protocolSetting-nas-smb-box']"
        nfs_xpath = "//*[@id='protocolSetting-nas-nfs-box']"
        ftp_xpath = "//*[@id='protocolSetting-nas-ftp-box']"
        # s3_xpath = "//*[@id='protocolSetting-object-s3-box']"
        san_xpath = "//*[@id='protocolSetting-block-iSCSI-box']"

        smb_obj = self.find_element_by_xpath(smb_xpath)
        nfs_obj = self.find_element_by_xpath(nfs_xpath)
        ftp_obj = self.find_element_by_xpath(ftp_xpath)
        # s3_obj = self.find_element_by_xpath(s3_xpath)
        san_obj = self.find_element_by_xpath(san_xpath)

        if smb_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(smb_xpath)  # box 类型反选
        if nfs_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(nfs_xpath)
        if ftp_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(ftp_xpath)
        # if s3_obj.is_selected():
        #     is_enable_nas_start_stat = True
        #     self.execute_script_click(s3_xpath)
        if san_obj.is_selected():
            is_enable_san_start_stat = True
            self.execute_script_click(san_xpath)

        # 单击确定
        self.find_element_by_xpath("//*[@id='protocolSettingWindow-btn-0']").click()

        if is_enable_nas_start_stat is True:
            # 勾选警告
            self.execute_script_click("//*[@id='riskCheckbox']")

            # 点击确定
            self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()

            # disable_nas 等待时间
            log.info("wait disable nas")
            self.check_element_done(time_out=self.timeout_max_default)

        # 重新勾选待删除的访问分区
        obj = self.find_element_by_xpath("//div[starts-with(text(),'%s')]/../../div/label/input" % name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 单击删除
        self.find_element_by_xpath("//*[@id='access_zone_bn_delete']").click()

        # 确认删除
        self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()

        # 等待访问分区删除成功
        self.check_element_done(check_by_click=True)
        return

    def update_access_zone(self, access_zone_name, access_zone_name_update=None, auth_provider_name=None,
                           node_name_list=None):
        """
        auther:liuhe
        :param access_zone_name:
        :param access_zone_name_update:
        :param auth_provider_name:
        :param node_name_list:
        :return:
        """
        log.info("update access zone")
        # 定位到访问分区
        self.locate_access_zone()
        # 勾选指定的访问分区
        self.find_element_by_xpath(
            "//*[starts-with(text(), '%s')]/../..//s" % access_zone_name, check_by_click=True).click()
        # 点击修改
        self.find_element_by_xpath("//*[@id='access_zone_bn_modify']").click()
        # 修改名称
        if access_zone_name_update:
            self.find_element_by_xpath(
                "//*[@id='ofs_access_zone_create_name_id']", js_send_keys=access_zone_name_update)
        if auth_provider_name:
            self.select_by_text("//*[@id='ofs_access_zone_create_auth_provider_id']", auth_provider_name)
        # 修改节点，点击节点搜索
        self.find_element_by_xpath("//*[@id='ofs_access_zone_create_node_list']//i").click()
        # 勾选指定节点
        if node_name_list:
            obj_check_box_list = self.driver.find_elements_by_xpath("//*[@id='nodeGrid']//input")
            for check_box in obj_check_box_list:
                if check_box.is_selected():
                    self.execute_script_click(dom=check_box)

            for node_name in node_name_list:
                self.find_element_by_xpath("//*[@title='%s']/../..//s" % node_name).click()
        # 点击确定
        self.find_element_by_xpath("//*[@id='accessZoneCreateNodeListWindow-btn-0']").click()
        # 点击确认修改
        self.find_element_by_xpath("//*[@id='accessZoneUpdateWindow-btn-0']").click()
        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")
        # 点击确定
        self.execute_script_click(xpath="//div[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]")
        # 检查修改完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)
        return access_zone_name_update

    def disable_or_enable_nas(self, access_zone_name, smb=False, nfs=False, ftp=False, s3=False, san=False):
        """
        auther:liuhe
        :param access_zone_name:
        :param smb:
        :param nfs:
        :param ftp:
        :param s3:
        :param san:
        :return:
        """
        # 停用nas协议，默认关闭nas
        log.info("disable or enable nas or disable san")

        # 定位到访问分区
        self.locate_access_zone()

        # 勾选指定的访问分区
        self.find_element_by_xpath(
            "//*[starts-with(text(), '%s')]/../..//s" % access_zone_name, check_by_click=True).click()

        # 点击服务设置
        self.find_element_by_xpath("//*[@id='access_zone_bn_protocol_setting']").click()

        # 勾选相应的服务
        if smb:
            obj_smb = self.find_element_by_xpath("//*[@id='protocolSetting-nas-smb-box']")
            if obj_smb.is_selected() is False:
                self.execute_script_click(dom=obj_smb)
        else:
            obj_smb = self.find_element_by_xpath("//*[@id='protocolSetting-nas-smb-box']")
            if obj_smb.is_selected():
                self.execute_script_click(dom=obj_smb)

        if nfs:
            obj_nfs = self.find_element_by_xpath("//*[@id='protocolSetting-nas-nfs-box']")
            if obj_nfs.is_selected() is False:
                self.execute_script_click(dom=obj_nfs)

        else:
            obj_nfs = self.find_element_by_xpath("//*[@id='protocolSetting-nas-nfs-box']")
            if obj_nfs.is_selected():
                self.execute_script_click(dom=obj_nfs)

        if ftp:
            obj_ftp = self.find_element_by_xpath("//*[@id='protocolSetting-nas-ftp-box']")
            if obj_ftp.is_selected() is False:
                self.execute_script_click(dom=obj_ftp)
        else:
            obj_ftp = self.find_element_by_xpath("//*[@id='protocolSetting-nas-ftp-box']")
            if obj_ftp.is_selected():
                self.execute_script_click(dom=obj_ftp)

        # if s3:
        #     obj_s3 = self.find_element_by_xpath("//*[@id='protocolSetting-object-s3-box']")
        #     if obj_s3.is_selected() is False:
        #         self.execute_script_click(dom=obj_s3)
        #
        # else:
        #     obj_s3 = self.find_element_by_xpath("//*[@id='protocolSetting-object-s3-box']")
        #     if obj_s3.is_selected():
        #         self.execute_script_click(dom=obj_s3)
        if san:
            obj_san = self.find_element_by_xpath("//*[@id='protocolSetting-block-iSCSI-box']")
            if obj_san.is_selected() is False:
                self.execute_script_click(dom=obj_san)

        else:
            obj_san = self.find_element_by_xpath("//*[@id='protocolSetting-block-iSCSI-box']")
            if obj_san.is_selected():
                self.execute_script_click(dom=obj_san)

        # 点击确定
        self.find_element_by_xpath("//*[@id='protocolSettingWindow-btn-0']").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定
        self.find_element_by_xpath("//div[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]").click()

        # 检查修改完成
        self.check_element_done(time_out=self.timeout_max_default)

        return

    def create_subnet(self, access_zone_name, subnet_name, svip, mask,
                      eth_name_list, domain_name, ip_address_pool_list, protocol):
        """
        创建业务子网，并添加vip池
        :param access_zone_name:      testzone
        :param subnet_name:           subnet
        :param svip:                  10.2.41.1
        :param mask:                  255.255.252.0
        :param eth_name_list:         ens192
        :param domain_name:           www.domaindomain.com
        :param ip_address_pool_list:  ["10.2.41.1", "10.2.41.10-21"]  支持单个IP地址和ip地址段
        :return:
        """
        log.info("create subnet and add ip address pool")

        # 定位到业务子网
        self.locate_subnet()

        # 选择访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 点击创建
        self.execute_script_click(xpath="//*[@id='subnet_bn_create']", check=True)

        # 填写子网名称
        self.find_element_by_xpath("//*[@id='ofs_subnet_create_name_id']", js_send_keys=subnet_name)

        # 填写SVIP
        self.find_element_by_xpath("//*[@id='ofs_subnet_create_service_vip_id']", js_send_keys=svip)

        # 填写子网掩码
        self.find_element_by_xpath("//*[@id='ofs_subnet_create_subnet_mask_id']", js_send_keys=mask)

        # 点击搜索网卡
        self.find_element_by_xpath("//*[@id='ofs_subnet_create_nic_selected']//i").click()

        # 勾选指定网卡名称
        for eth_name in eth_name_list:
            self.execute_script_click(xpath="//*[@title='%s']/../..//input" % eth_name)

        # 点击确定网卡
        self.find_element_by_xpath("//*[@id='subnet_create_nic_list_window-btn-0']").click()

        # 点击确定业务子网
        self.find_element_by_xpath("//*[@id='subnetCreateWindow-btn-0']").click()

        # 等待创建子网完成
        self.check_element_done()

        # 选中指定名称的subnet
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击创建ip地址池
        self.find_element_by_xpath("//*[@id='vip_addr_pool_bn_create']", check=True).click()

        # 填写ip地址池域名
        self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_domain_name_id']", js_send_keys=domain_name)

        # 填写ip地址，入参为list表
        text = "\\n".join(ip_address_pool_list)
        self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_ip_address_id']", js_send_keys=text)

        self.select_by_val("//*[@id='ofs_vip_addr_pool_create_support_protocol_id']", protocol)  # 选择制定认证类型

        # 点击确定增加ip地址池
        self.find_element_by_xpath("//*[@id='VIPAddrPoolCreateWindow-btn-0']").click()

        # 检查添加完成
        self.check_element_done(time_out=1200, check_by_click=True)
        return subnet_name

    def modify_subnet(self, access_zone_name, subnet_name, subnet_name_modify=None, svip=None, mask=None,
                      eth_name_list=None):
        """
        修改业务子网
        :param subnet_name_modify:    待修改的业务子网名称
        :param access_zone_name:      testzone
        :param subnet_name:           subnet
        :param svip:                  10.2.41.1
        :param mask:                  255.255.252.0
        :param eth_name_list:              ens192
        :return:
        """
        log.info("modefy subnet")

        # 定位到业务子网
        self.locate_subnet()

        # 选择访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 选择指定修改的subnet
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击修改
        self.find_element_by_xpath("//*[@id='subnet_bn_update']", check=True).click()

        # 填写子网名称
        if subnet_name_modify is not None:
            self.find_element_by_xpath("//*[@id='ofs_subnet_create_name_id']", js_send_keys=subnet_name_modify)

        # 填写SVIP
        if svip is not None:
            self.find_element_by_xpath("//*[@id='ofs_subnet_create_service_vip_id']", js_send_keys=svip)

        # 填写子网掩码
        if mask is not None:
            self.find_element_by_xpath("//*[@id='ofs_subnet_create_subnet_mask_id']", js_send_keys=mask)

        # 点击搜索网卡
        if eth_name_list:
            self.find_element_by_xpath("//*[@id='ofs_subnet_create_nic_selected']//i").click()

            # 勾选指定网卡名称
            self.implicit_wait("//*[@type='checkbox']")
            obj_checkbox_list = self.driver.find_elements_by_xpath("//*[@type='checkbox']/../input")
            for checkbox in obj_checkbox_list:
                if checkbox.is_selected():
                    self.execute_script_click(dom=checkbox)
            for eth_name in eth_name_list:
                self.find_element_by_xpath("//*[@title='%s']/../..//s" % eth_name).click()

            # 点击确定网卡
            self.find_element_by_xpath("//*[@id='subnet_create_nic_list_window-btn-0']").click()

        # 点击确定业务子网
        self.find_element_by_xpath("//*[@id='subnetCreateWindow-btn-0']").click()

        # 等待修改子网完成
        self.check_element_done(check_by_click=True)
        return subnet_name

    def delete_subnet(self, access_zone_name, subnet_name):
        """
        删除业务子网（会先删除对应的vip池）
        :param access_zone_name:testzone
        :param subnet_name:subnet
        :return:
        """
        log.info("delete subnet")

        # 定位到业务子网
        self.locate_subnet()

        # 选择访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 勾选待删除的业务子网
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 循环删除该业务子网下所有的vip地址池
        xpath = "//*[@id='vip_addr_pool_display']//*[@type='radio']/../input"
        time.sleep(3)

        while True:
            obj_list = self.driver.find_elements_by_xpath(xpath)
            # 如果业务子网下没有vip池
            if not obj_list:
                break

            if obj_list[0].is_selected() is False:
                self.execute_script_click(dom=obj_list[0])

            # 点击删除vip地址池
            self.find_element_by_xpath("//*[@id='vip_addr_pool_bn_delete']").click()

            # 勾选警告
            self.execute_script_click("//*[@id='riskCheckbox']")

            # 点击确定删除vip地址池
            self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id, 'riskComfirm')]").click()

            # 检查删除成功
            self.check_element_done(time_out=self.timeout_max_default)

        # 点击删除subnet
        self.find_element_by_xpath("//*[@id='subnet_bn_delete']").click()

        # 点击确认删除subnet
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除子网成功
        self.check_element_done(check_by_click=True)
        return

    def add_vip_pool(self, access_zone_name, subnet_name, domain_name, ip_address_list):
        """
        添加指定vip池
        :param access_zone_name:
        :param subnet_name:
        :param domain_name:  ip地址池的域名
        :param ip_address_list:  ["10.2.41.1", "10.2.41.50-60"] 支持单个地址和地址段
        :return:
        """
        log.info("add vip address pool")

        # 定位到业务子网
        self.locate_subnet()

        # 选择指定访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 勾选指定的业务子网
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击增加ip地址池
        self.find_element_by_xpath("//*[@id='vip_addr_pool_bn_create']").click()

        # 填写ip地址池域名
        self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_domain_name_id']", js_send_keys=domain_name)

        # 填写ip地址，入参为list表
        text = "\\n".join(ip_address_list)
        self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_ip_address_id']", js_send_keys=text)

        # 点击确定增加ip地址池
        self.find_element_by_xpath("//*[@id='VIPAddrPoolCreateWindow-btn-0']").click()

        # 检查添加完成
        self.check_element_done(time_out=self.timeout_max_default)
        return ip_address_list

    def delete_vip_pool(self, access_zone_name, subnet_name, domain_name):
        """
        删除指定的vip池，直接删除subnet也能自动删除对应的vip池
        :param access_zone_name:
        :param subnet_name:
        :param domain_name:
        :return:
        """
        log.info("delete vip pool")

        # 定位到业务子网
        self.locate_subnet()

        # 选择指定访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 勾选指定的业务子网
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 选择指定删除的vip池
        self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//s" % domain_name).click()

        # 点击删除
        self.find_element_by_xpath("//*[@id='vip_addr_pool_bn_delete']").click()

        # 勾选删除警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定删除
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id, 'riskComfirm')]").click()

        # 检查删除成功
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)
        return

    def modify_vip_pool(self, access_zone_name, subnet_name, domain_name, domain_name_modify=None,
                        ip_address_list=None, balance_strategy=None):
        """
        修改vip池
        :param balance_strategy: LB_ROUND_ROBIN(轮询) LB_CONNECTION_COUNT（连接数）
                                  LB_THROUGHPUT（带宽） LB_CPU_USAGE（cpu使用率）
        :param access_zone_name:
        :param subnet_name:
        :param domain_name:
        :param domain_name_modify:
        :param ip_address_list:
        :return:
        """
        log.info("modify vip pool")

        # 定位到业务子网
        self.locate_subnet()

        # 选择指定访问分区
        self.select_by_text("//*[@id='subnet_combo_box_current_access_zone_id']", access_zone_name, check=True)

        # 勾选指定的业务子网
        obj = self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//input" % subnet_name)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 选择指定修改的vip池
        self.find_element_by_xpath("//*[starts-with(text(),'%s')]/../..//s" % domain_name).click()

        # 点击修改
        self.find_element_by_xpath("//*[@id='vip_addr_pool_bn_update']").click()

        # 填写ip地址池域名
        if domain_name_modify is not None:
            self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_domain_name_id']",
                                       js_send_keys=domain_name_modify)

        # 填写ip地址，入参为list表
        if ip_address_list:
            text = "\\n".join(ip_address_list)
            self.find_element_by_xpath("//*[@id='ofs_vip_addr_pool_create_ip_address_id']", js_send_keys=text)

        if balance_strategy:
            self.select_by_val("//*[@id='ofs_vip_addr_pool_create_balancing_strategy_id']", balance_strategy)

        # 点击确定修改ip地址池
        self.find_element_by_xpath("//*[@id='VIPAddrPoolCreateWindow-btn-0']").click()

        # 勾选修改警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确认警告
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id, 'riskComfirm')]").click()

        # 检查添加完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)
        return


class HostManage(first_level_label):
    """
    auther：liuhe
    主机和主机组管理
    """

    def locate_host_group(self):
        """访问管理--->主机组"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_hostgroup']/a", check_by_click=True).click()
        return

    def locate_host(self):
        """访问管理--->主机"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_host']/a", check_by_click=True).click()
        return

    def create_host_group(self, host_group_name=None):
        log.info("will create host group")

        # 定位到主机组
        self.locate_host_group()

        # 点击创建按钮
        self.find_element_by_xpath("//*[@id='host_group_bn_create']").click()

        # 填写主机组名称
        self.find_element_by_xpath("//*[@id='host_group_name_id']", js_send_keys=host_group_name)

        # 点击确认添加成功
        self.find_element_by_xpath("//*[@id='ofs_host_group_window_id-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return host_group_name

    def update_host_group(self, be_upname, new_name):
        """
        auther:liuhe
        :param be_upname: str 被修改的主机组名称
        :param new_name: str 新主机组名称
        :return:
        """
        log.info("will update host group")

        # 定位到主机组
        self.locate_host_group()

        # 勾选指定待修改的名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % be_upname)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击修改
        self.find_element_by_xpath("//*[@id='host_group_bn_update']").click()

        if new_name is not None:
            self.find_element_by_xpath("//*[@id='host_group_name_id']", js_send_keys=new_name)

        # 点击确认添加成功
        self.find_element_by_xpath("//*[@id='ofs_host_group_window_id-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return new_name

    def delete_host_group(self, hg_name):
        """
        auther:liuhe
        :param hg_name: str 主机组名称
        :return:
        """
        log.info("will update host group")

        # 定位到主机组
        self.locate_host_group()

        # 勾选指定待修改的名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % hg_name)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击删除
        self.find_element_by_xpath("//*[@id='host_group_bn_delete']").click()

        # 勾选确认信息
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'riskComfirm')]").click()

        # 检查删除完成
        self.check_element_done()
        return

    def create_host(self, host_name, list_num, type_os):
        log.info("will create host")

        # 定位到主机
        self.locate_host()

        # 点击创建按钮
        self.find_element_by_xpath("//*[@id='host_bn_create']").click()

        # 填写主机名称
        self.find_element_by_xpath("//*[@id='ofs_host_name_id']", js_send_keys=host_name)

        # 选择主机组
        self.select_by_val("//*[@id='ofs_host_group_combo_id']", str(list_num))
        # 选择主机操作系统
        self.select_by_val("//*[@id='ofs_osType_combo_id']", str(type_os))
        # 点击确认添加成功
        self.find_element_by_xpath("//*[@id='ofs_create_host_window_id-btn-0']").click()
        # 检查添加完成
        self.check_element_done()
        return

    def delete_host(self, host_name):
        log.info("will delete host")

        # 定位到主机
        self.locate_host()

        # 勾选指定待删除的名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % host_name)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击删除按钮
        self.find_element_by_xpath("//*[@id='host_bn_delete']").click()
        # 点击确定删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除完成
        self.check_element_done()
        return
