#!/usr/bin/python
# -*-coding:utf-8 -*


import os
import random
import ConfigParser
import commands
import xml.dom.minidom

config_path = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(config_path, 'job_fault.xml')

##############################################################################
# ##name  :      get_job_fault_info
# ##parameter:
# ##author:      duyuli
# ##date  :      2019.01.11
# ##Description: 获取nis鉴权服务器的地址
##############################################################################

def get_job_stages_total(job_name):
    # 获取每个job的阶段数
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    job_name_xml = config_info.getElementsByTagName(job_name)[0]
    total = job_name_xml.getElementsByTagName("stages")[0].firstChild.nodeValue
    return int(total.strip())

def get_job_fault_info(job_name, stage):
    """
    获取job相关配置
    :param job_name:create_node_pools
    :param stage:1
    :return:
    """
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    job_name_xml = config_info.getElementsByTagName(job_name)[0]
    stage_xml = job_name_xml.getElementsByTagName("stage_%s" % stage)[0]
    faults_xml = stage_xml.getElementsByTagName("fault")
    stage_fault_list = []
    for fault_xml in faults_xml:
        fault_value = fault_xml.firstChild.nodeValue
        stage_fault_list.append(fault_value)
    return stage_fault_list

def get_node_ip_power_off_list():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    node_ip_xml_list = config_info.getElementsByTagName("node_ip_power_off")
    node_ip_list = []
    for node_ip_xml in node_ip_xml_list:
        node_ip = node_ip_xml.firstChild.nodeValue
        node_ip_list.append(node_ip)
    return node_ip_list

def get_node_ip_remove_list():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    node_ip_xml_list = config_info.getElementsByTagName("node_ip_remove")
    node_ip_list = []
    for node_ip_xml in node_ip_xml_list:
        node_ip = node_ip_xml.firstChild.nodeValue
        node_ip_list.append(node_ip)
    return node_ip_list

def get_stage_set():
    config_info = xml.dom.minidom.parse(CONFIG_FILE)
    stage_set_list = config_info.getElementsByTagName("stage_set")
    stage_set = stage_set_list[0].firstChild.nodeValue
    return int(stage_set)
