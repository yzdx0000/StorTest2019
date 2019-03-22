# -*-coding:utf-8 -*

#######################################################
# 脚本作者：duyuli
# 日期：2018-11-23
# 脚本说明：界面自动化库函数
#######################################################
import os
import time
from multiprocessing import Process
import threading
from selenium import webdriver
from selenium.webdriver import ActionChains                   # double_click
from selenium.webdriver.support.select import Select          # 下来菜单选择
from selenium.webdriver.support.wait import WebDriverWait     # 智能等待
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException       # 导入指定异常

import log
import get_config
import common

class MyThread(threading.Thread):
    """重新定义带返回值的线程类"""
    result = None

    def __init__(self, target, args=(), exit_err=True):
        super(MyThread, self).__init__()   # 初始化线程类
        self.func = target
        self.args = args
        self.exitcode = 0          # 退出码
        self.exit_err = exit_err   # 线程异常退出是否抛出异常

    def run(self):
            try:
                self.result = self.func(*self.args)   # 获取返回值
            except Exception:
                self.exitcode = 1
                if self.exit_err:
                    raise

    def get_result(self):
            return self.result

def driver_firefox():
    driver = webdriver.Firefox()
    return driver

def init_web_driver(auto_connect=True, explorer_name=None, web_ip=None):
    """初始化浏览器"""
    driver = None
    if explorer_name is None:
        explorer_name = get_config.get_explorer_name()
    if web_ip is None:
        web_ip = get_config.get_web_ip()

    if explorer_name == "firefox":
        # selenium的bug会导致初始化失败，或者防止xmanager启动失败，添加重试
        for i in range(5):
            p1 = MyThread(target=driver_firefox, args=(), exit_err=False)
            p1.setDaemon(True)
            p1.start()
            p1.join(60)
            if 0 == p1.exitcode and p1.get_result() is not None:
                driver = p1.get_result()
                break
            else:
                log.info("set one daemon thread cause by init web driver")
                time.sleep(1)
            if i == 4:
                raise Exception("init web driver failed")

    elif explorer_name == "chrome":
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--no-sandbox')  # 启动浏览器添加的参数，root用户时添加
        chrome_options.add_argument('disable-infobars')  # 不弹出浏览器自带信息提示
        driver = webdriver.Chrome(chrome_options=chrome_options)
        driver.set_window_size(1300, 700)  # 默认窗口大小不利于观测，设置窗口大小
    else:
        raise Exception("WebUI explorer name must be firefox or chrome")

    driver.get("https://%s:6080" % web_ip)

    obj_web_base = Web_Base(driver)
    # 选择语言，输入用户名，密码
    Select(obj_web_base.find_element_by_xpath("//*[@id='login_select_language']")).select_by_value("en_US")
    Select(obj_web_base.find_element_by_xpath("//*[@id='login_select_language']")).select_by_value("zh_CN")

    # 切换语言会自动进行刷新，确保刷新成功后再操作
    for i in range(10):
        attr = obj_web_base.find_element_by_xpath("//*[@id='login_name']").get_attribute("placeholder")
        if attr in "输入您的用户名":
            break
        time.sleep(0.5)

    obj_web_base.find_element_by_xpath("//*[@id='login_name']", js_send_keys=get_config.get_web_login_name())
    obj_web_base.find_element_by_xpath("//*[@id='login_pwd']", js_send_keys=get_config.get_web_login_pwd())
    obj_web_base.find_element_by_xpath("//*[@id='login-btn']").click()

    # 点击连接
    if auto_connect:
        obj_web_base.find_element_by_xpath("//a[contains(text(),'连接')]").click()
    return driver


def quit_web_driver(driver):
    """退出WebUI"""
    """以防止上一个动作未执行完毕，强制等待"""
    time.sleep(2)
    driver.quit()
    return


class Web_Base(object):
    """WebUI测试基础类"""
    timeout_default = 60        # 默认超时时间
    timeout_max_default = 600   # 最大超时时间

    def __init__(self, driver):
        self.driver = driver

    def implicit_wait(self, xpath, time_out=timeout_default, presence=True, visibility=False):
        """
        智能等待，只要出现了字段就进行下一步操作,加入超时报错屏幕截图保存
        author:duyuli
        :param visibility: 所有对用户可见，使用较少，某些特殊情况下才会用到
        :param presence:所有加载完，经常使用
        :param xpath: //*[@id='xxxxxx']
        :param time_out: 默认最大等待时间
        :return:
        """
        location_login = (By.XPATH, xpath)

        if visibility:
            presence = False
            WebDriverWait(self.driver, time_out, 1).until(
                expected_conditions.visibility_of_all_elements_located(location_login))
            WebDriverWait(self.driver, time_out, 1).until(
                expected_conditions.element_to_be_clickable(location_login))

        if presence:
            try:
                WebDriverWait(self.driver, time_out, 1).until(
                    expected_conditions.presence_of_all_elements_located(location_login))
            except TimeoutException:
                # 超时异常则保存图片到日志目录下，方便分析
                self.save_screenshot_now()
                raise
        time.sleep(0.5)
        return

    def find_element_by_xpath(self, xpath, elements_num=0, time_out=timeout_default, check=False, check_by_click=False,
                              visibility=False, js_send_keys=None):
        """
        经常使用，1、重写一个方法加入时间的优化
                 2、加入js文本框输入方法
                 3、检查上一个动作是否完成
        author:duyuli
        :param check_by_click: 通过点击判断是否存在遮罩（只用于点击主界面）
        :param js_send_keys: 采用js语法替代selenuim的send_keys(),原因是chrome输入带数字1时失效
        :param visibility:另一种方式等待界面加载
        :param check:通过标签判断是否存在遮罩，在有折叠链接时，容易被干扰
        :param xpath:
        :param elements_num: 默认取多个对象中的第一个
        :param time_out:
        :return:
        """
        self.implicit_wait(xpath, time_out=time_out, visibility=visibility)

        if check:
            self.check_element_done(time_out=time_out)

        if check_by_click:
            self.check_element_done_by_click(time_out=time_out)

        obj = self.driver.find_elements_by_xpath(xpath)[elements_num]
        if js_send_keys:
            self.driver.execute_script("arguments[0].focus()", obj)  # 定位光标，相当于先点击一下的效果
            return self.driver.execute_script("arguments[0].value='%s'" % js_send_keys, obj)
        return obj

    def execute_script_click(self, xpath=None, dom=None, check=False, elements_num=0):
        # xpath 与 dom 必须填写一个
        if xpath:
            dom = self.find_element_by_xpath(xpath, check=check, elements_num=elements_num)
        self.driver.execute_script("arguments[0].click()", dom)
        return

    def check_element_done_by_click(self, xpath="//*[@id='frame-main-top-panel']", time_out=timeout_default):
        """
        判断遮罩，通过捕获异常的方式，判断是否执行完成，一般用在库函数的结尾
        author:duyuli
        :param xpath:
        :param time_out:
        :return:
        """
        count = 1
        while True:
            # noinspection PyBroadException
            try:
                self.driver.find_element_by_xpath(xpath).click()
            except Exception:
                # log.info("check for %s s" % (count * 5))
                if count > time_out:
                    log.info("check time out")
                    self.save_screenshot_now("error_msg")
                    raise Exception("time out")
                count += 1
                time.sleep(1)
                continue
            break

    def check_element_done(self, time_out=timeout_default, check_by_click=False):
        """判断遮罩,用于判断是否执行完成，一般用于库函数的结尾"""
        for i in range(time_out * 2):
            obj_list = self.driver.find_elements_by_xpath("//*[@class='frame-mask']/*")
            if not obj_list:
                break
            time.sleep(0.5)

            if (i + 1) == (time_out * 2):
                log.info("check element done time out time:%s s" % time_out)
                raise Exception("time out")

        if check_by_click:
            self.check_element_done_by_click()
        return

    def check_href_on_or_off(self, xpath, check_by_click=False):
        """
        检查折叠链接是否展开
        author:duyuli
        :param check_by_click:
        :param xpath:
        :return:
        """
        obj = self.find_element_by_xpath(xpath, check_by_click=check_by_click)
        class_attribute = obj.get_attribute("class")

        # 关闭状态
        if "icon-angle-right" in class_attribute:
            return False, obj

        # 展开状态
        if "icon-angle-down" in class_attribute:
            return True, obj

    def check_href_until_on(self, xpath, check_by_click=True):
        """
        检查折叠链接直到展开,解决点击链接偶尔不能展开的情况，多点几次
        author:duyuli
        :param check_by_click:
        :param xpath:
        :return:
        """
        for i in range(5):
            is_on_or_off, obj = self.check_href_on_or_off(xpath=xpath, check_by_click=check_by_click)
            if is_on_or_off:
                return
            obj.click()
            is_on_or_off, obj = self.check_href_on_or_off(xpath=xpath, check_by_click=check_by_click)
            if is_on_or_off:
                return
            time.sleep(0.5)
        raise Exception("check href until on failed")

    def move_scroll_bar(self, frame_js_path, element_js_path, scroll_bar_js_path=None, move_scroll_bar=True):
        """
        移动滚动条到框架中间位置
        :param move_scroll_bar: 是否移动或是返回移动值（多次移动时使用）
        :param frame_js_path:框架路径
        :param element_js_path:需定位的元素路径
        :param scroll_bar_js_path:滚动条上层控制路径（非滚动条路径）
        :return:
        """
        # 获取弹框中间位置
        frame_top = self.driver.execute_script("return " + frame_js_path + ".offset().top")
        frame_height = self.driver.execute_script("return " + frame_js_path + ".height()")
        frame_middle = int(frame_top) + int(frame_height)/2

        # 获取元素移动高度
        element_top = self.driver.execute_script("return " + element_js_path + ".offset().top")
        move_value = frame_middle - int(element_top)

        # 移动滚动条
        if move_scroll_bar:
            self.driver.execute_script(scroll_bar_js_path + ".css('top', %s)" % move_value)
        else:
            return move_value

    def move_scroll_bar_by_top(self, top):
        scroll_bar_js_path = "$($('.mCSB_container')[1])"
        self.driver.execute_script(scroll_bar_js_path + ".css('top', %s)" % top)
        return

    def save_screenshot_now(self, name="no_name"):
        time_now = time.strftime("%y-%m-%d_%H-%M-%S")
        self.driver.get_screenshot_as_file(os.path.join(log.log_file_dir, '%s_%s.png' % (time_now, name)))

    def select_by_val(self, xpath, val, check=False):
        if check:
            self.check_element_done()
        self.execute_script_click(xpath)
        self.execute_script_click(xpath="//*[@class='gv-combo-option']/li[@val='%s']" % val)
        return

    def select_by_text(self, xpath, text, check=False):
        if check:
            self.check_element_done()
        self.execute_script_click(xpath)
        self.execute_script_click(xpath="//*[@class='gv-combo-option']/li[starts-with(text(), '%s')]" % text)
        return


class First_Level_Label(Web_Base):
    """定位到一级标签"""
    def locate_home(self):
        """定位到首页"""
        xpath = "//*[@id='ofs_dashboard']/a"
        self.find_element_by_xpath(xpath, check_by_click=True).click()
        return

    def locate_manage_operation(self):
        """定位到管理运维"""
        xpath = "//*[@id='ofs_maintain']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_source_manage(self):
        """定位到资源管理"""
        xpath = "//*[@id='ofs_resourcepartitioning']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_access_manage(self):
        """定位到访问管理"""
        xpath = "//*[@id='ofs_access']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_protocol_manage(self):
        """协议管理"""
        xpath = "//*[@id='ofs_protocol']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_alarm_event(self):
        """告警事件"""
        xpath = "//*[@id='ofs_alarm']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_system_settings(self):
        """系统设置"""
        xpath = "//*[@id='ofs_settings']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_webui_info(self):
        """WebUI信息"""
        xpath = "//*[@id='ofs_webuiinfo']/a"
        self.find_element_by_xpath(xpath, check_by_click=True).click()
        return

    def get_cluster_time(self):
        """获取系统时间"""
        for i in range(10):
            time_cluster = self.find_element_by_xpath("//*[@id ='ofs_current_connect_cluster_time']", check=True).text
            if "20" in time_cluster:
                return time_cluster
            else:
                time.sleep(1)
        raise Exception("get cluster time failed")

    @staticmethod
    def check_time_earlier_or_later(time1, time2):
        """用来判断集群时间格式，用于检查事件"""
        # time1     eg:   2018-12-03 15:27:31
        list_time1 = time1.split()[0].split("-")
        list_time1.extend(time1.split()[1].split(":"))

        list_time2 = time2.split()[0].split("-")
        list_time2.extend(time2.split()[1].split(":"))

        int_time1, int_time2, a = 0, 0, 1

        for i in range(1, 7):
            int_time1 = int_time1 + int(list_time1[6 - i]) * a
            int_time2 = int_time2 + int(list_time2[6 - i]) * a
            a *= 60
        return int_time2 - int_time1


class System_Operation(First_Level_Label):
    """系统运维"""
    def locate_system_operation(self):
        """管理运维--->系统运维"""
        self.locate_manage_operation()
        self.find_element_by_xpath("//*[@id='ofs_system_maintain']/a", check_by_click=True).click()
        return

    def shutdown_system(self):
        log.info("shutdown system")

        # 定位到系统运维
        self.locate_system_operation()

        # 点击关闭系统
        self.find_element_by_xpath("//*[@id='ofs_system_maintain_systemshutdown_div']", check=True).click()

        # 点击确认关闭系统
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查关闭完成
        self.check_element_done(time_out=3600)

        # 留一个关闭系统的截图
        time.sleep(1)
        self.save_screenshot_now(name='shutdown_system')

        # 点击关闭完成后的确定信息
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()
        return

    def start_system(self):
        log.info("start system")

        # 定位到系统运维
        self.locate_system_operation()

        # 点击启动系统
        self.find_element_by_xpath("//*[@id='ofs_system_maintain_systemstart_div']", check=True).click()

        # 点击确定启动
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查启动成功
        self.check_element_done(time_out=3600)

        # 留一个启动系统的截图
        self.save_screenshot_now(name='start_system')

        # 点击完成后的确定信息
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()
        return


class Node_Operation(First_Level_Label):
    """节点运维"""
    def locate_node_operation(self):
        """管理运维--->节点运维"""
        self.locate_manage_operation()
        self.find_element_by_xpath("//*[@id='ofs_node']/a", check_by_click=True).click()
        return

    def check_node_operate_bandwidth_iops(self):
        # 检查节点运维界面带宽、IOPS不为N/A
        log.info("check bandwidth and iops")

        # 定位到节点运维
        self.locate_node_operation()

        # 获取每个节点的带宽和iops标签对象
        bandwidth_xpath = "//*[@id='node_grid']//div[@class='kuma-uxtable-row-cells']/div[last()-3]"
        iops_xpath = "//*[@id='node_grid']//div[@class='kuma-uxtable-row-cells']/div[last()-2]"
        self.implicit_wait(bandwidth_xpath)
        bandwidth_obj_list = self.driver.find_elements_by_xpath(bandwidth_xpath)
        iops_obj_list = self.driver.find_elements_by_xpath(iops_xpath)

        # 检查bandwidth不为N/A
        for i in range(len(bandwidth_obj_list)):
            if "B/s" not in bandwidth_obj_list[i].text:
                raise Exception("check bandwidth is N/A failed and bandwidth:%s" % bandwidth_obj_list[i].text)
            if ":" not in iops_obj_list[i].text:
                raise Exception("check iops is N/A failed and iops:%s" % bandwidth_obj_list[i].text)

        log.info("check bandwidth and iops right")
        return

    def search_function_for_node_operation(self, search_option, name_value=None, healthy_state_value=None,
                                           running_state_value=None):
        """
        节点运维搜索功能
        :param search_option: eg name healthy_state running_state
        :param name_value:xxx
        :param healthy_state_value:None(全部) normal（正常） abnormal（异常） unknown（获取中）
        :param running_state_value:None（全部） normal（正常） abnormal（异常） deleting（删除中）
                                    reinstalling （重装中） shutdown （关闭） maintaining （维护中）
                                    prepare_maintaining （下线中）prepare_online（上线中） zombie（待移除） unknown（获取中）
        :return:
        """
        log.info("search function for node operation")

        # 定位的到节点运维
        self.locate_node_operation()
        xpath_select = "//*[@id='node_search_type_id']"
        xpath_search = "//*[@id='node_search_content_id']"

        self.select_by_val(xpath_select, search_option)

        # 按名称搜索
        if name_value:
            self.find_element_by_xpath(xpath_search, js_send_keys=name_value)

        # 按健康状态搜索
        if healthy_state_value:
            self.find_element_by_xpath(xpath_search + "/../input[1]", js_send_keys=healthy_state_value)
            self.find_element_by_xpath(xpath_search).click()
            healthy_state_text = self.find_element_by_xpath(
                xpath_search + "/../ul/li[@data='%s']" % healthy_state_value).text
            self.find_element_by_xpath(xpath_search, js_send_keys=healthy_state_text)
            self.check_element_done_by_click()

        # 按运行状态搜索
        if running_state_value:
            self.find_element_by_xpath(xpath_search + "/../input[1]", js_send_keys=running_state_value)
            self.find_element_by_xpath(xpath_search).click()
            running_state_text = self.find_element_by_xpath(
                xpath_search + "/../ul/li[@data='%s']" % running_state_value).text
            self.find_element_by_xpath(xpath_search, js_send_keys=running_state_text)
            self.check_element_done_by_click()

        # 点击搜索
        self.find_element_by_xpath(xpath_search + "/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return

    def remove_node(self, node_name):
        log.info("remove node")

        # 定位到节点运维
        self.locate_node_operation()

        # 选中指定删除的节点
        self.execute_script_click(xpath="//*[starts-with(text(), '%s')]/../../..//input" % node_name, check=True)

        # 点击删除
        self.find_element_by_xpath("//*[@id='node_bn_delete']").click()

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 输入警告信息
        self.find_element_by_xpath("//*[@id='riskText']").send_keys('YES')

        # 点击确认警告信息
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'riskComfirm')]").click()

        # 检查删除下发完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 点击刷新,循环检查已经删除成功
        for i in range(360):
            # 删除的超时时间设置为30分钟
            length = len(self.driver.find_elements_by_xpath("//*[starts-with(text(), '%s')]" % node_name))
            if not length:
                # 删除后检查重启
                for j in range(60):
                    node_control_ip = get_config.get_web_node_ip().split(",")[0]
                    flag = common.check_ping(node_control_ip)
                    if flag is False:
                        log.info("%s is rebooting" % node_control_ip)
                        break
                    if i == 59:
                        raise Exception("ping timeout 5 min")
                    time.sleep(5)
                log.info("delete node success")
                break
            time.sleep(5)
            if i == 359:
                raise Exception("remove node timeout 30min")
            self.find_element_by_xpath("//*[@id='node_bn_refresh']", check=True).click()
        return

    def add_node(self, node_control_ip, data_ip_list, update_to_node_pool_name=None):
        log.info("add node")

        # 判断该节点是否ping通
        for i in range(60):
            flag = common.check_ping(node_control_ip)
            if flag:
                log.info("check ping right")
                time.sleep(20)
                break
            if i == 59:
                raise Exception("ping timeout 5 min")
            time.sleep(5)

        log.info("start to add node")

        # 定位到节点运维
        self.locate_node_operation()

        # 点击添加节点
        self.find_element_by_xpath("//*[@id='node_bn_create']", check=True).click()

        # 输入管理ip
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_control_ip_id']", js_send_keys=node_control_ip)

        # 点击搜索节点信息
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_control_ip']//i").click()

        # 等待搜索完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 点击搜索数据ip
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_data_ip']//i").click()

        # 勾选指定数据ip
        xpath = "//*[@id='ofs_install_nodes_info_ip_select_checkboxGroup_id']//input"
        self.implicit_wait(xpath=xpath)
        obj_list = self.driver.find_elements_by_xpath(xpath)
        for obj in obj_list:
            if obj.get_attribute("value") not in data_ip_list:
                self.driver.execute_script("arguments[0].click()", obj)

        # 点击确定选择数据ip
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_ip_select_id-btn-0']").click()

        # 点击搜索共享盘
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_share_disks']//i").click()

        # 勾选共享盘
        vir_or_phy = get_config.get_web_machine()
        if vir_or_phy == "vir":
            share_disk_path = "//*[contains(text(),'%s GB')]/../..//input" % get_config.get_web_disk_size()
            self.implicit_wait(share_disk_path)
            obj_disks_list = self.driver.find_elements_by_xpath(share_disk_path)
            # 选择2块共享盘
            for i in range(2):
                self.execute_script_click(dom=obj_disks_list[i])

        else:
            share_disk_path = "//*[contains(text(),'SSD')]/../../div/label/input"
            self.implicit_wait(share_disk_path)
            obj_disks_list = self.driver.find_elements_by_xpath(share_disk_path)
            for obj_disks in obj_disks_list:
                self.execute_script_click(dom=obj_disks)

        # 点击确定勾选共享盘
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_disk_select_id-btn-0']").click()

        # 点击搜索数据盘
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_data_disks']//i").click()

        # 勾选数据盘
        if vir_or_phy == "vir":
            data_disk_path = "//*[contains(text(),'%s GB')]/../..//input" % get_config.get_web_disk_size()

        else:
            data_disk_path = "//*[contains(text(),'TB')]/../..//input"

        self.implicit_wait(data_disk_path)
        time.sleep(3)
        obj_data_disks_list = self.driver.find_elements_by_xpath(data_disk_path)
        if not obj_data_disks_list:
            self.save_screenshot_now("add_node_no_disk")
            raise Exception("add node no disk")
        for obj_data_disk in obj_data_disks_list:
            self.execute_script_click(dom=obj_data_disk)

        self.save_screenshot_now("add_node_disk")
        # 点击确定勾选数据盘
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_disk_select_id-btn-0']").click()

        # 选择扩容到的节点池
        if update_to_node_pool_name:
            self.select_by_text("//*[@id='ofs_install_nodepool']", update_to_node_pool_name)

        # 点击确定
        self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_addNode_id-btn-0']").click()

        # 点击确定警告
        if vir_or_phy == "vir":
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'warring')]").click()

        # 检查环境
        self.check_element_done(time_out=self.timeout_max_default)

        # 留一个检查环境的截图
        self.save_screenshot_now(name='check_environment')

        # 确认添加节点
        self.find_element_by_xpath("//*[@id='ofs_install_info_button_confirm_add']").click()

        # 检查添加完成
        self.check_element_done(time_out=1200)

        # 点击添加正确无报错
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'alert')]").click()

        return

    def remove_disk(self, node_name, data_disk=False, share_disk=False):
        log.info("remove disk")

        # 定位到节点运维
        self.locate_node_operation()

        # 点击磁盘所在的节点
        self.find_element_by_xpath("//*[starts-with(text(), '%s')]" % node_name).click()

        # 点击存储介质按钮
        for i in range(10):
            if len(self.driver.find_elements_by_xpath("//*[@id='storage_device_display']")):
                break
            self.find_element_by_xpath("//*[@id='tabCard']/li[4]").click()
            time.sleep(0.5)

        # 删除磁盘(删除最后一个)
        disk_name = None
        if data_disk:
            self.execute_script_click(xpath="//*[starts-with(text(), '数据')]/../../..//*[@title='查看更多']", elements_num=-1)
            disk_name = self.find_element_by_xpath("//*[@title='设备符']/../../div[2]/div").text
            self.execute_script_click(xpath="//*[@id='node_storage_view_more-btn-0']")
            self.find_element_by_xpath("//*[starts-with(text(), '数据')]/../../..//*[@id="
                                       "'ofs_nodedetails_disk_delete_link ofs-disk-operate']", elements_num=-1).click()
        if share_disk:
            self.execute_script_click(xpath="//*[starts-with(text(), '共享')]/../../..//*[@title='查看更多']", elements_num=-1)
            disk_name = self.find_element_by_xpath("//*[@title='设备符']/../../div[2]/div").text
            self.execute_script_click(xpath="//*[@id='node_storage_view_more-btn-0']")
            self.find_element_by_xpath("//*[starts-with(text(), '共享')]/../../..//*[@id="
                                       "'ofs_nodedetails_disk_delete_link ofs-disk-operate']", elements_num=-1).click()

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()
        self.check_element_done()

        # 检查重建完成
        log.info("remove disk wait data rebuild")
        for i in range(360):
            time.sleep(5)
            if not len(self.driver.find_elements_by_xpath("//*[starts-with(text(), '重建中')]")):
                break

        self.check_element_done(time_out=self.timeout_max_default)
        return disk_name

    def add_disk(self, node_name, disk_type, disk_name, storage_pool_name=None):
        """
        添加磁盘
        :param disk_name: 磁盘盘符
        :param node_name: vm153
        :param disk_type: DATA(数据盘)  SHARED（共享盘）
        :param storage_pool_name:
        :return:
        """
        log.info("add disk")

        # 定位到节点运维
        self.locate_node_operation()

        # 点击磁盘所在的节点
        self.find_element_by_xpath("//*[starts-with(text(), '%s')]" % node_name).click()

        for i in range(10):
            if len(self.driver.find_elements_by_xpath("//*[@id='storage_device_display']")):
                break
            self.find_element_by_xpath("//*[@id='tabCard']/li[4]").click()
            time.sleep(0.5)

        # 添加磁盘（最后一个未用磁盘）
        disk_objs = self.driver.find_elements_by_xpath("//*[starts-with(text(), '未用')]/../../..//*[@title='查看更多']")
        flag = 0
        for disk_obj in disk_objs:
            self.execute_script_click(dom=disk_obj)
            disk_name_current = self.find_element_by_xpath("//*[@title='设备符']/../../div[2]/div").text
            self.execute_script_click(xpath="//*[@id='node_storage_view_more-btn-0']")
            if disk_name == disk_name_current:
                self.find_element_by_xpath("//*[starts-with(text(), '未用')]/../../..//*[@id='"
                                           "ofs_nodedetails_disk_add_link ofs-disk-operate']", elements_num=flag).click()
                break
            flag += 1

        # 选择磁盘用途
        self.select_by_val("//*[@id='ofs_node_add_disk_type_id']", disk_type)

        # 选择关联存储池（添加元数据盘时不需要）
        if storage_pool_name:
            self.select_by_text("//*[@id='ofs_node_add_storage_pool_field']", storage_pool_name)

        # 点击确认添加
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_addRack_id-btn-0']").click()

        # 检查添加完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)

        return

    def get_node_name_list(self):
        # 定位到节点运维
        self.locate_node_operation()

        # 获取并返回节点名称列表
        node_name_list = []
        self.implicit_wait("//*[@class='ofs-link']")
        obj_node = self.driver.find_elements_by_xpath("//*[@class='ofs-link']")
        for node in obj_node:
            node_name_list.append(node.text)

        return node_name_list

    def get_node_total(self):
        # 获取界面节点个数统计
        self.locate_node_operation()

        # 获取节点个数
        time.sleep(3)
        node_numbers_str = self.find_element_by_xpath("//*[@class='kuma-page-total']").text
        node_numbers = int(node_numbers_str[1:-1])
        return node_numbers

    def get_node_operation_info(self, node_name):
        # 获取节点运维界面信息包括：健康状态、运行状态、ip信息、总容量、已用容量、可用容量、带宽、iops、服务状态、协议类型

        # 定位到节点运维
        self.locate_node_operation()

        # 获取单个节点信息
        time.sleep(3)
        value_list = []
        obj_list = self.driver.find_elements_by_xpath("//*[starts-with(text(), '%s')]/../../../div" % node_name)
        for i in range(len(obj_list) - 2):
            if i < 2:
                value_list.append(self.find_element_by_xpath(
                    "//*[starts-with(text(), '%s')]/../../../div[%s]/div/div" % (node_name, i + 3)).text)
            else:
                value_list.append(self.find_element_by_xpath(
                    "//*[starts-with(text(), '%s')]/../../../div[%s]/div" % (node_name, i + 3)).text)

        return value_list

    def get_node_operate_inside_node_base_info(self, node_name):
        # 获取节点运维界面单个节点进去后的基本信息、并检查点击+号后的各个参数

        # 定位到节点运维
        self.locate_node_operation()

        # 点击指定节点名称
        self.execute_script_click(xpath="//*[starts-with(text(), '%s')]" % node_name, check=True)

        # 获取基本信息:机型、位置、序列号、健康状态、运行状态
        model = self.find_element_by_xpath("//*[@id='nodedetail_model']").text
        position = self.find_element_by_xpath("//*[@id='nodedetail_node_position']").text
        serial_no = self.find_element_by_xpath("//*[@id='nodedetail_serial_no']").text
        health_state = self.find_element_by_xpath("//*[@id='nodedetail_healthy_state']").text
        running_state = self.find_element_by_xpath("//*[@id='nodedetail_running_state']").text

        # 点击+号展开各个参数
        for i in range(3):
            self.find_element_by_xpath("//*[@id='ofsChartAdd']").click()
            self.find_element_by_xpath("//*[@class='ofs-chart-unshow-ul']/*[1]").click()

        # 检查：带宽、iops、cpu、内存、协议带宽 不为空
        time.sleep(3)
        obj_list = self.driver.find_elements_by_xpath("//*[@id='emptyData']")
        if obj_list:
            self.save_screenshot_now()
            raise Exception("check node operation node inside error")

        return [model, position, serial_no, health_state, running_state]

    def get_node_operate_inside_node_network_device_info(self, node_name):
        # 获取节点运维界面单个节点进去后的网络设备信息

        # 定位到节点运维
        self.locate_node_operation()

        # 点击指定节点名称
        self.find_element_by_xpath("//*[starts-with(text(), '%s')]" % node_name).click()

        # 点击网络设备按钮
        time.sleep(0.5)
        self.find_element_by_xpath("//*[@id='tabCard']/li[3]", check_by_click=True).click()

        # 获取网络设备基本信息（没张网卡10条信息）
        time.sleep(1)
        value_info = []
        obj_list = self.driver.find_elements_by_xpath("//*[@id='nodedetail_network_grid']//ul/li/div/div/div")
        for obj in obj_list:
            value_info.append(obj.text)

        return value_info

    def get_node_operate_inside_node_storage_media_info(self, node_name):
        # 获取节点运维界面单个节点进去后的存储介质信息

        # 定位到节点运维
        self.locate_node_operation()

        # 点击指定节点名称
        self.find_element_by_xpath("//*[starts-with(text(), '%s')]" % node_name).click()

        # 点击存储介质按钮
        time.sleep(1)
        self.find_element_by_xpath("//*[@id='tabCard']/li[4]", check_by_click=True).click()

        # 获取存储介质基本信息（每条10个，7块磁盘就是10*7个项）
        time.sleep(3)
        value_info_1 = []
        obj_list = self.driver.find_elements_by_xpath("//*[@id='storage_device_display']//ul/li/div/div/div")
        i = 0
        for obj in obj_list:
            if obj in obj_list[2::11]:
                value_info_1.append(self.find_element_by_xpath(
                    "//*[@id='nodedetail_progress_bar_value_id']", elements_num=i).text)
                i += 1
                continue
            if obj in obj_list[10::11]:
                continue
            value_info_1.append(obj.text)

        # 再次获取信息，避免刷新导致的获取信息不正常
        time.sleep(2)
        value_info_2 = []
        obj_list = self.driver.find_elements_by_xpath("//*[@id='storage_device_display']//ul/li/div/div/div")
        i = 0
        for obj in obj_list:
            if obj in obj_list[2::11]:
                value_info_2.append(self.find_element_by_xpath(
                    "//*[@id='nodedetail_progress_bar_value_id']", elements_num=i).text)
                i += 1
                continue
            if obj in obj_list[10::11]:
                continue
            value_info_2.append(obj.text)

        # 排除未用磁盘，不做检查
        count = 0
        count_list = []
        for value1 in value_info_1:
            if value1 == "未用":
                count_list.append(count)
            count += 1

        # 比对更多信息
        obj_more_info_list = self.driver.find_elements_by_xpath(
            "//*[@id='ofs_nodedetails_disk_light_link ofs-disk-operate']/../div[3]")

        for i in count_list:
            i = int(i/10)
            del obj_more_info_list[i]

        for obj_more_info in obj_more_info_list:
            # 点击更多信息
            for i in range(5):
                if self.driver.find_elements_by_xpath("//*[@id='DISKcombo']"):
                    break
                self.check_element_done()
                obj_more_info.click()
                time.sleep(1)

            # 获取基本信息列表
            time.sleep(1)
            value_more_info = []
            obj_more_list = self.driver.find_elements_by_xpath(
                "//*[@id='nodedetail_storage_detail_grid']//ul/li/div/div/div")
            for obj_more in obj_more_list:
                value_more_info.append(obj_more.text)

            # 下拉滚动条
            frame_js_path = "$('.content-wrap')"
            element_js_path = "$('#DISKcombo')"
            scroll_bar_js_path = "$('#node_storage_view_more .mCSB_container')"
            self.move_scroll_bar(frame_js_path, element_js_path, scroll_bar_js_path)

            # 检查带宽和iops不为空
            for value in ["BANDWIDTH", "IOPS"]:
                self.select_by_val("//*[@id='DISKcombo']", value)
                for i in range(10):
                    if not self.driver.find_elements_by_xpath("//*[@id='emptyData']"):
                        break
                    if 9 == i:
                        self.save_screenshot_now()
                        raise Exception("check iops empty")
                    time.sleep(1)

            # 点击关闭
            self.find_element_by_xpath("//*[@id='node_storage_view_more-btn-0']").click()

        return value_info_1, value_info_2


class Job_Manage(First_Level_Label):
    """任务管理"""
    def locate_job_manage(self):
        """管理运维--->任务管理"""
        self.locate_manage_operation()
        xpath = "//*[@id='ofs_jobengine']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return

    def locate_job_overview(self):
        """管理运维--->任务管理--->任务概览"""
        self.locate_job_manage()
        self.find_element_by_xpath("//*[@id='ofs_jobengine_overview']/a", check_by_click=True).click()
        return

    def locate_job_config(self):
        """管理运维--->任务管理--->任务配置"""
        self.locate_job_manage()
        self.find_element_by_xpath("//*[@id='ofs_jobengine_types']/a", check_by_click=True).click()
        return

    def locate_job_history(self):
        """管理运维--->任务管理--->历史任务"""
        self.locate_job_manage()
        self.find_element_by_xpath("//*[@id='ofs_jobengine_history']/a", check_by_click=True).click()
        return

    def search_function_for_job_overview(self, search_option, type_value=None, state_value=None, priority_value=None,
                                         impact_value=None):
        """
        任务概览搜索功能接口
        :param search_option:搜索类型 eg  type（任务名称） state（运行状态） priority（优先级） impact（影响度）
        :param type_value:           eg JOB_ENGINE_REPAIR JOB_ENGINE_REBUILD JOB_ENGINE_BALANCE 等等共9个
        :param state_value:          eg JOB_ENGINE_WAIT JOB_ENGINE_ACTIVE JOB_ENGINE_PAUSE
        :param priority_value:       eg 0 1 2 等等共11个
        :param impact_value:         eg HIGH MIDDLE LOW
        :return:
        """
        log.info("search function for job overview")

        # 定位到任务概览
        self.locate_job_overview()

        xpath_select = "//*[@id='jobengine_search_type_id']"
        xpath_text = "//*[@id='jobengine_search_content_id']"

        # 选择搜索类型
        self.select_by_val(xpath_select, search_option)

        # 按任务名称搜索、按运行状态搜索、按优先级搜索、按影响度搜索
        for option in [type_value, state_value, priority_value, impact_value]:
            if option:
                self.find_element_by_xpath(xpath_text + "/../input[1]", js_send_keys=option)
                self.find_element_by_xpath(xpath_text).click()
                option_text = self.find_element_by_xpath(xpath_text + "/../ul/li[@data='%s']" % option).text
                self.find_element_by_xpath(xpath_text, js_send_keys=option_text)
                self.check_element_done_by_click()
                break

        # 点击搜索
        self.find_element_by_xpath(xpath_text + "/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return

    def search_function_for_job_config(self, search_option, type_value=None, priority_value=None, impact_value=None,
                                       state_value=None):
        """
        任务配置搜索功能接口
        :param search_option:搜索类型 eg  type（任务名称） state（运行状态） priority（优先级） impact（影响度）
        :param type_value:           eg JOB_ENGINE_REPAIR JOB_ENGINE_REBUILD JOB_ENGINE_BALANCE 等等共9个
        :param state_value:          eg JOB_ENGINE_WAIT JOB_ENGINE_ACTIVE JOB_ENGINE_PAUSE
        :param priority_value:       eg 0 1 2 等等共11个
        :param impact_value:         eg HIGH MIDDLE LOW
        :return:
        """
        log.info("search function for job config")

        # 定位到任务概览
        self.locate_job_config()

        xpath_select = "//*[@id='jobengine_types_search_type_id']"
        xpath_text = "//*[@id='jobengine_types_search_content_id']"

        # 选择搜索类型
        self.select_by_val(xpath_select, search_option)

        # 按任务名称搜索、按运行状态搜索、按优先级搜索、按影响度搜索
        for option in [type_value, state_value, priority_value, impact_value]:
            if option:
                self.find_element_by_xpath(xpath_text + "/../input[1]", js_send_keys=option)
                self.find_element_by_xpath(xpath_text).click()
                option_text = self.find_element_by_xpath(xpath_text + "/../ul/li[@data='%s']" % option).text
                self.find_element_by_xpath(xpath_text, js_send_keys=option_text)
                self.check_element_done_by_click()
                break

        # 点击搜索
        self.find_element_by_xpath(xpath_text + "/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return

    def search_function_for_job_history(self, search_option, type_value=None, result_value=None):
        """
        历史任务搜索接口
        :param search_option: eg type  result
        :param type_value:    eg JOB_ENGINE_REPAIR JOB_ENGINE_REBUILD JOB_ENGINE_BALANCE 等等共9个
        :param result_value:  eg 0(成功) -1（失败）
        :return:
        """
        log.info("search function for job history")

        # 定位到历史任务
        self.locate_job_history()

        xpath_select = "//*[@id='jobengine_history_search_type_id']"
        xpath_text = "//*[@id='jobengine_history_search_content_id']"

        # 选择搜索类型
        self.select_by_val(xpath_select, search_option)

        # 按任务名称搜索、按运行状态搜索、按优先级搜索、按影响度搜索
        for option in [type_value, result_value]:
            if option:
                self.find_element_by_xpath(xpath_text + "/../input[1]", js_send_keys=option)
                self.find_element_by_xpath(xpath_text).click()
                option_text = self.find_element_by_xpath(xpath_text + "/../ul/li[@data='%s']" % option).text
                self.find_element_by_xpath(xpath_text, js_send_keys=option_text)
                self.check_element_done_by_click()
                break

        # 点击搜索
        self.find_element_by_xpath(xpath_text + "/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return


class Params_Config(First_Level_Label):
    """参数配置"""
    def locate_params_config(self):
        """管理运维--->参数配置"""
        self.locate_manage_operation()
        self.find_element_by_xpath("//*[@id='ofs_params']/a", check_by_click=True).click()
        return

    def search_function_for_params_config(self, name, name_value):
        # 参数配置搜索功能
        log.info("search function for params config")

        # 定位到参数配置
        self.locate_params_config()

        # 选择按名称搜索
        self.select_by_val("//*[@id='ofs_params_search_type_id']", name)

        # 输入名称值
        self.find_element_by_xpath("//*[@id='ofs_params_search_content_id']", js_send_keys=name_value)

        # 点击搜索
        self.find_element_by_xpath("//*[@id='ofs_params_search_content_id']/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return


class Node_Pool(First_Level_Label):
    """节点池"""
    def locate_node_pool(self):
        """资源管理--->节点池"""
        self.locate_source_manage()
        self.find_element_by_xpath("//*[@id='ofs_nodepool']/a", check_by_click=True).click()
        return

    def search_function_for_node_pool(self, search_option, name_value=None, redundancy_ratio_value=None,
                                      nodelist_value=None, remark_value=None):
        """
        节点池搜索功能接口
        :param search_option:name（名称） redundancy_ratio（冗余配比） nodelist（节点列表） remark（备注）
        :param name_value:
        :param redundancy_ratio_value:
        :param nodelist_value:
        :param remark_value:
        :return:
        """
        log.info("search function for node pool")

        # 定位到节点池
        self.locate_node_pool()

        # 选择搜索类型
        self.select_by_val("//*[@id='nodepool_search_type_id']", search_option)

        # 输入搜索条件
        for option in [name_value, redundancy_ratio_value, nodelist_value, remark_value]:
            if option:
                self.find_element_by_xpath("//*[@id='nodepool_search_content_id']", js_send_keys=option)
                break

        # 点击搜索
        self.find_element_by_xpath("//*[@id='nodepool_search_content_id']/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return

    def create_node_pool(self, mode, erasure_codes_value=None, replica_num=None,
                         stripe_width=None, node_parity_num=None):
        """
        创建节点池
        :param mode: erasure_codes（纠删码）  replication（副本）
        :param erasure_codes_value:4+2:1
        :param replica_num:2
        :param stripe_width:1
        :param node_parity_num:1
        :return:
        """
        log.info("create node pool")

        # 定位到节点池
        self.locate_node_pool()

        # 点击创建节点池
        self.find_element_by_xpath("//*[@id='nodepool_bn_create']", check_by_click=True).click()

        # 点击全部添加
        self.find_element_by_xpath("//*[@id='nodepool_bn_addnode_all']").click()
        time.sleep(1)

        # 勾选自动划分节点池
        self.execute_script_click(xpath="//*[@id='nodepool_auto_divide_id']")

        # 拖动滚动条
        self.move_scroll_bar_by_top(-200)

        # 选择纠删码或者冗余配比
        self.select_by_val("//*[@id='ofs_nodepool_redundancy_level_id']", mode)

        if mode == "erasure_codes":
            time.sleep(1)
            if not self.driver.find_elements_by_xpath("//*[@val='%s']" % erasure_codes_value):
                # 点击查看更多
                self.find_element_by_xpath("//*[@id='ofs_nodepool_nmb_more']").click()

                # 需要下拉，采用js方式直接选中
                js = "$(\"[title='%s']\").parent().parent().find('input').click()" % erasure_codes_value
                self.driver.execute_script(js)

                # 点击确定选中纠删码
                self.find_element_by_xpath("//*[@id='all_nmb_window-btn-0']").click()

        if mode == "replication":
            # 点击查看更多
            self.find_element_by_xpath("//*[@id='ofs_nodepool_r_node_more']").click()

            # 选择副本数
            self.select_by_val("//*[@id='all_replicationDiv_r_div_id']", str(replica_num))

            # 选择条带宽度
            self.select_by_val("//*[@id='all_replicationDiv_stripwidth_div_id']", str(stripe_width))

            # 选择冗余节点数
            self.select_by_val("//*[@id='all_replicationDiv_r_node_parity_div_id']", str(node_parity_num))

            # 点击确定该副本
            self.find_element_by_xpath("//*[@id='all_replication_window-btn-0']").click()

        # 点击预览
        self.find_element_by_xpath("//*[@id='nodepool_create_window-btn-0']").click()

        # 点击确定预览
        self.find_element_by_xpath("//*[@id='ofs_nodepool_preview_window-btn-0']", check=True).click()

        # 点击确定创建
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查创建完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)
        return

    def update_node_pool(self, name, node_name_list):
        """
        扩容节点池
        :param name: NodePool_1
        :param node_name_list: ["vm44", "vm43"]
        :return:
        """
        log.info("update node pool")

        # 定位到节点池
        self.locate_node_pool()

        # 勾选指定名称的节点池
        self.execute_script_click(xpath="//*[@title='%s']/../..//input" % name, check=True)

        # 点击扩容
        self.find_element_by_xpath("//*[@id='nodepool_bn_update']").click()

        # 勾选指定扩容的节点
        for node_name in node_name_list:
            self.execute_script_click(xpath="//div[@title='%s']/../..//input" % node_name)

        # 点击添加
        self.find_element_by_xpath("//*[@id='nodepool_bn_addnode']").click()

        # 点击确定
        self.find_element_by_xpath("//*[@id='nodepool_update_window-btn-0']").click()

        # 检查扩容完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 留一个启动成功或者失败的截图
        self.save_screenshot_now(name='update_node_pool')

        # 点击确定启动成功
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'alert')]").click()
        self.check_element_done()
        return

    def get_node_pool_names(self):
        # 定位到节点池
        self.locate_node_pool()

        # 获取节点池名称
        node_pool_names = []
        self.implicit_wait("//*[@class='default-cell']")
        obj_list = self.driver.find_elements_by_xpath("//*[@class='default-cell']")
        for obj in obj_list:
            node_pool_names.append(obj.text)
        return node_pool_names

    def get_node_pool_count(self):
        # 获取界面节点池数目统计
        stdout = self.find_element_by_xpath("//*[@class='kuma-page-total']").text
        node_pool_count = int(stdout[1:-1])
        return node_pool_count


class Storage_Pool(First_Level_Label):
    """存储池"""
    def locate_storage_pool(self):
        """资源管理--->存储池"""
        self.locate_source_manage()
        self.find_element_by_xpath("//*[@id='ofs_storagepool']/a", check_by_click=True).click()
        return

    def search_function_for_storage_pool(self, search_option, name_value=None, type_value=None):
        # search_option:  eg  name(名称) type（服务类型）
        # type_value:     eg  SHARED FILE BLOCK OBJECT
        log.info("search function for storage pool")

        # 定位到存储池
        self.locate_storage_pool()

        xpath_select = "//*[@id='storagepool_search_type_id']"
        xpath_text = "//*[@id='storagepool_search_content_id']"

        # 选择搜索类型
        self.select_by_val(xpath_select, search_option)

        # 按名称搜索
        if name_value:
            self.find_element_by_xpath(xpath_text, js_send_keys=name_value)

        # 按服务类型搜索
        if type_value:
            self.find_element_by_xpath(xpath_text + "/../input[1]", js_send_keys=type_value)
            self.find_element_by_xpath(xpath_text).click()
            option_text = self.find_element_by_xpath(xpath_text + "/../ul/li[@data='%s']" % type_value).text
            self.find_element_by_xpath(xpath_text, js_send_keys=option_text)
            self.check_element_done_by_click()

        # 点击搜索
        self.find_element_by_xpath(xpath_text + "/../i").click()

        # 检查搜索完成
        self.check_element_done()
        return

    def create_storage_pool(self, name, service_type, disk_all=True):
        """
        创建存储池
        :param service_type: 服务类型  eg FILE（文件）  OBJECT（对象）
        :param name: 存储池名称
        :param disk_all: 磁盘全选或者部分(True 为全选)
        :return:
        """
        log.info("create storage pool")

        # 定位到存储池
        self.locate_storage_pool()

        # 点击创建
        self.find_element_by_xpath("//*[@id='storagepool_bn_create']").click()

        # 输入存储池名称
        self.find_element_by_xpath("//*[@id='storagepool_input_name']", js_send_keys=name)

        # 点击选择节点池
        self.execute_script_click(xpath="//*[@id='storagepool_bn_select_nodepool']")

        # 勾选节点池（默认全选，如果有需要，再进行修改）
        time.sleep(2)
        dom = self.find_element_by_xpath("//*[@type='checkbox']", elements_num=1)
        self.execute_script_click(dom=dom)

        # 点击确定节点池
        self.find_element_by_xpath("//*[@id='storagepool_select_nodepool_window-btn-0']").click()

        # 点击选择硬盘
        self.find_element_by_xpath("//*[@id='storagepool_bn_select_disk']").click()

        # 勾选硬盘
        if disk_all is False:
            # 全部展开
            time.sleep(1)
            js = "var q = $('#storagepool_select_disk_wrapper li');q.each(function(index,value)" \
                 "{if ($(value).css('display') == 'none'){$(value).css('display', 'block')}})"
            self.driver.execute_script(js)

            disk_part_value_xpath = "//*[contains(text(), '/dev')]/../..//input"
            self.implicit_wait(disk_part_value_xpath)
            disk_list = self.driver.find_elements_by_xpath(disk_part_value_xpath)

            for disk_dom in disk_list[::2]:
                # 勾选硬盘
                self.execute_script_click(dom=disk_dom)

        if disk_all:
            self.execute_script_click(xpath="//*[@id='selectAllCheckbox']")

        # 点击确定选择硬盘
        self.find_element_by_xpath("//*[@id='storagepool_select_disk_window-btn-0']").click()

        # 选择服务类型
        self.select_by_val("//*[@id='storagepool_usage']", service_type)

        # 点击确定创建
        self.find_element_by_xpath("//*[@id='storagepool_create_window-btn-0']").click()

        # 检查创建完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)

        return

    def expand_storage_pool(self, storage_pool_name, disk_all=True):
        log.info("expand storage pool")

        # 定位到存储池
        self.locate_storage_pool()

        # 选中需扩容的存储池
        self.execute_script_click(xpath="//*[@title='%s']/../..//input" % storage_pool_name, check=True)

        # 点击扩容
        self.find_element_by_xpath("//*[@id='storagepool_bn_expand']").click()

        # 点击选择节点池
        self.find_element_by_xpath("//*[@id='storagepool_bn_select_nodepool']").click()

        # 勾选全部节点池
        for i in range(10):  # 避免全选点击后子项未加载完成的情况
            if len(self.driver.find_elements_by_xpath("//*[@type='checkbox']")) > 2:
                self.execute_script_click(xpath="//*[@type='checkbox']", elements_num=1)
                break
            time.sleep(0.5)

        # 点击确定
        self.find_element_by_xpath("//*[@id='storagepool_select_nodepool_window-btn-0']").click()

        # 点击选择磁盘
        self.find_element_by_xpath("//*[@id='storagepool_bn_select_disk']").click()

        # 点击勾选全部
        if disk_all:
            self.execute_script_click(xpath="//*[@id='selectAllCheckbox']")
        else:
            # 全部展开
            time.sleep(1)
            js = "var q = $('#storagepool_select_disk_wrapper li');q.each(function(index,value)" \
                 "{if ($(value).css('display') == 'none'){$(value).css('display', 'block')}})"
            self.driver.execute_script(js)

            disk_part_value_xpath = "//*[contains(text(), '/dev')]/../..//input"
            self.implicit_wait(disk_part_value_xpath)
            disk_list = self.driver.find_elements_by_xpath(disk_part_value_xpath)

            for disk_dom in disk_list[::2]:
                # 勾选硬盘
                self.execute_script_click(dom=disk_dom)

        # 点击确定选择硬盘
        self.find_element_by_xpath("//*[@id='storagepool_select_disk_window-btn-0']").click()

        # 点击确定扩容
        self.find_element_by_xpath("//*[@id='storagepool_expand_window-btn-0']").click()

        # 检查扩容完成
        self.check_element_done(check_by_click=True)
        return

    def delete_storage_pool(self, storage_pool_name):
        log.info("delete storage pool")

        # 定位到存储池
        self.locate_storage_pool()

        # 选中指定的存储池
        self.execute_script_click("//*[@title='%s']/../..//input" % storage_pool_name, check=True)

        # 点击删除
        self.find_element_by_xpath("//*[@id='storagepool_bn_delete']").click()

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除成功
        self.check_element_done()
        return

    def get_storage_pool_names(self):
        # 定位到存储池
        self.locate_storage_pool()

        # 获取存储池名称
        storage_pool_names = []
        self.implicit_wait("//*[@class='default-cell']")
        obj_list = self.driver.find_elements_by_xpath("//*[@class='default-cell']")
        for obj in obj_list:
            storage_pool_names.append(obj.text)
        return storage_pool_names

    def get_storage_pool_count(self):
        # 获取界面存储数目统计
        stdout = self.find_element_by_xpath("//*[@class='kuma-page-total']").text
        storage_pool_count = int(stdout[1:-1])
        return storage_pool_count


class File(First_Level_Label):
    """文件"""
    def locate_file(self):
        """定位到文件：  资源管理 ---> 文件"""
        self.locate_source_manage()
        xpath = "//*[@id='ofs_res_file']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return


class File_System(File):
    """文件系统"""
    def locate_file_system(self):
        """定位到文件：  资源管理--->文件--->文件系统"""
        self.locate_file()
        self.find_element_by_xpath("//*[@id='ofs_file_system']/a", check_by_click=True).click()
        return

    def create_volume(self, volume_name, storage_name, volume_quota_limit=None):
        log.info("create volume")

        # 定位到文件系统
        self.locate_file_system()

        # 点击创建
        self.find_element_by_xpath("//*[@id='volume_bn_create']", check_by_click=True).click()

        # 输入名称
        self.find_element_by_xpath("//*[@id='volume_create_name_field']", js_send_keys=volume_name)

        # 选择关联的存储池
        self.select_by_text("//*[@id='volume_create_storagepool_field']", storage_name)

        # 限制卷容量
        if volume_quota_limit:
            self.execute_script_click("//*[@id='create_volume_quota_cal_type']")
            self.find_element_by_xpath("//*[@id='volume_create_capacity_field']", js_send_keys=volume_quota_limit)

        # 点击确定创建文件系统
        self.find_element_by_xpath("//*[@id='volume_create_window-btn-0']").click()

        # 检查创建完成
        self.check_element_done(time_out=self.timeout_max_default, check_by_click=True)

        return

    def delete_volumes(self, volume_name_list):
        log.info("delete volumes")

        # 定位到文件系统
        self.locate_file_system()

        # 循环删除文件系统文件系统
        for volume_name in volume_name_list:
            self.execute_script_click("//*[@title='%s']/../..//input" % volume_name, check=True)

            # 点击删除
            self.find_element_by_xpath("//*[@id='volume_bn_delete']").click()

            # 输入警告信息
            self.find_element_by_xpath("//*[@id='riskText']", js_send_keys="CONFIRM")
            self.driver.execute_script("$('#riskText').trigger('input')")  # 触发change事件

            # 点击确定警告
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'riskComfirm')]").click()

            # 检查删除完成
            self.check_element_done(check_by_click=True)
        return

    def update_volume(self, volume_limit_name, volume_quota_limit):
        log.info("update volume")

        # 定位到文件系统
        self.locate_file_system()

        # 选中指定的卷名称
        self.find_element_by_xpath("//*[@title='%s']/../..//s" % volume_limit_name, check_by_click=True).click()

        # 点击修改
        self.find_element_by_xpath("//*[@id='volume_bn_modify']").click()

        # 输入修改的卷配额大小
        time.sleep(0.5)
        self.find_element_by_xpath(
            "//*[@id='volume_create_capacity_field']", check=True, js_send_keys=volume_quota_limit)

        # 点击确定修改配额
        self.find_element_by_xpath("//*[@id='volume_modify_window-btn-0']").click()

        # 检查修改完成
        self.check_element_done()
        return

    def get_volume_names(self):
        # 定位到卷
        self.locate_file_system()

        # 获取卷名称
        volume_names = []
        self.implicit_wait("//*[@class='default-cell']")
        obj_list = self.driver.find_elements_by_xpath("//*[@class='default-cell']")
        for obj in obj_list[::2]:
            volume_names.append(obj.text)
        return volume_names

    def get_volume_count(self):
        # 获取界面卷数目统计
        stdout = self.find_element_by_xpath("//*[@class='kuma-page-total']").text
        volume_count = int(stdout[1:-1])
        return volume_count


class Access_Manage(First_Level_Label):
    """访问管理"""
    def locate_auth_provider(self):
        """访问管理--->认证服务器"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_authprovider']/a", check_by_click=True).click()
        return

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

    def locate_user_group(self):
        """访问管理--->用户/用户组"""
        self.locate_access_manage()
        self.find_element_by_xpath("//*[@id='ofs_usergroup']/a", check_by_click=True).click()
        return

    def add_auth_provider_ad(self, name, domain_name, dns_addresses, username, password, services_for_unix=None,
                             check=False):
        """
        添加ad认证服务器
        :param name:服务器名称
        :param domain_name:adtest
        :param dns_addresses:10.2.41.251
        :param username:administrator
        :param password:111111
        :param services_for_unix:RFC2307
        :param check:是否测试连接
        :return:
        """
        log.info("add authorize provider AD")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击AD按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'AD')]", check_by_click=True).click()

        # 点击添加
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_add_button']").click()

        # 填写认证服务器相关信息
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_name_id']", js_send_keys=name)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_domain_name_id']", js_send_keys=domain_name)
        self.find_element_by_xpath(
            "//*[@id='ofs_auth_provider_ad_operation_primary_dns_ipaddress_id']", js_send_keys=dns_addresses)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_domain_admin_name_id']",
                                   js_send_keys=username)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_domain_admin_password_id']",
                                   js_send_keys=password)

        if services_for_unix:
            self.select_by_val("//*[@id='ofs_auth_provider_ad_operation_services_for_unix_id']", services_for_unix)

        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def update_auth_provider_ad(self, name_being_updated, name=None, domain_name=None,
                                dns_addresses=None, username=None, password=None, check=False):
        """
        修改AD认证服务器
        :param name_being_updated:待修改的服务器名称
        :param name:服务器名称
        :param domain_name:adtest
        :param dns_addresses:10.2.41.251
        :param username:administrator
        :param password:111111
        :param check:是否测试连接
        :return:
        """
        log.info("update AD authorize provider")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击AD按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'AD')]", check_by_click=True).click()

        # 勾选指定待修改的名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name_being_updated)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击修改
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_update_button']").click()

        # 填写认证服务器相关信息
        if name is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_name_id']", js_send_keys=name)
        if domain_name is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_domain_name_id']", domain_name)
        if dns_addresses is not None:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ad_operation_primary_dns_ipaddress_id']", js_send_keys=dns_addresses)
        if username is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_domain_admin_name_id']",
                                       js_send_keys=username)
        if password is not None:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ad_operation_domain_admin_password_update_id']/..//i").click()
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ad_operation_domain_admin_password_update_id']", js_send_keys=password)

        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def delete_auth_provider_ad(self, name):
        log.info("delete AD authorize provider")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击AD按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'AD')]", check=True).click()

        # 勾选指定待删除的名称
        obj_name = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name)
        if obj_name.is_selected() is False:
            self.execute_script_click(dom=obj_name)

        # 点击删除
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ad_delete_button']").click()

        # 点击确定删除
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除完成
        self.check_element_done()
        return

    def add_auth_provider_ldap(self, name, base_dn, ip_addresses, port=None, bind_dn=None, bind_password=None,
                               domain_password=None, user_search_path=None, group_search_path=None, check=None):
        """
        添加ldap认证服务器
        :param name:
        :param base_dn:dc=test,dc=com
        :param ip_addresses:10.2.41.181
        :param port:
        :param bind_dn:
        :param bind_password:
        :param domain_password:
        :param user_search_path:ou=user,dc=abc,dc=com
        :param group_search_path:ou=group,dc=abc,dc=com
        :param check:测试连接
        :return:
        """
        log.info("add authorize provider LDAP")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击LDAP按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'LDAP')]", check=True).click()

        # 点击添加
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_add_button']").click()

        # 填写LDAP相关信息
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_name_id']", js_send_keys=name)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_primary_ipaddress_id']",
                                   js_send_keys=ip_addresses)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_base_dn_id']", js_send_keys=base_dn)
        if port:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_port_id']", js_send_keys=port)
        if bind_dn:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_bind_dn_id']", js_send_keys=bind_dn)
        if bind_password:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_bind_password_id']", js_send_keys=bind_password)
        if domain_password:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_domain_password_id']", js_send_keys=domain_password)
        if user_search_path:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_user_search_path_id']", js_send_keys=user_search_path)
        if group_search_path:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_group_search_path_id']", js_send_keys=group_search_path)

        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def update_auth_provider_ldap(self, name_to_be_update, name, base_dn=None, ip_addresses=None, port=None,
                                  bind_dn=None, bind_password=None, domain_password=None, user_search_path=None,
                                  group_search_path=None, check=None):
        """
        修改ldap认证服务器
        :param name_to_be_update:需要修改的服务器名称
        :param name:修改后的名称
        :param base_dn:
        :param ip_addresses:
        :param port:
        :param bind_dn:
        :param bind_password:
        :param domain_password:
        :param user_search_path:
        :param group_search_path:
        :param check:
        :return:
        """
        log.info("update authorize provider ldap")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击LDAP按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'LDAP')]", check=True).click()

        # 勾选指定的ldap认证服务器名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name_to_be_update)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击修改
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_update_button']").click()

        # 填写ldap相关信息
        if name:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_name_id']", js_send_keys=name)
        if ip_addresses:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_primary_ipaddress_id']", js_send_keys=ip_addresses)
        if base_dn is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_base_dn_id']", js_send_keys=base_dn)
        if port is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_port_id']", js_send_keys=port)
        if bind_dn is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_bind_dn_id']", js_send_keys=bind_dn)
        if bind_password is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_bind_password_update']//i").click()
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_bind_password_update_id']", js_send_keys=bind_password)
        if domain_password is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_domain_password_update']//i").click()
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_domain_password_update_id']", js_send_keys=domain_password)

        if user_search_path is not None:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_user_search_path_id']", js_send_keys=user_search_path)

        if group_search_path is not None:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_ldap_operation_group_search_path_id']", js_send_keys=group_search_path)

        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def delete_auth_provider_ldap(self, name):
        log.info("delete authorize provider ldap")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击LDAP按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'LDAP')]", check=True).click()

        # 勾选待删除的服务器名称
        obj_delete = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name)
        if obj_delete.is_selected() is False:
            self.execute_script_click(dom=obj_delete)

        # 点击删除
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_ldap_delete_button']").click()

        # 点击确认删除LDAP
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除成功
        self.check_element_done()
        return

    def add_auth_provider_nis(self, name, domain_name, ip_addresses, check=None):
        """
        添加NIS服务器
        :param name:
        :param domain_name:nistest
        :param ip_addresses:10.2.41.247
        :param check:
        :return:
        """
        log.info("add authorize provider nis")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击NIS按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'NIS')]", check=True).click()

        # 点击添加
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_add_button']").click()

        # 输入NIS认证服务器相关信息
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_name_id']", js_send_keys=name)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_domain_name_id']",
                                   js_send_keys=domain_name)
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_primary_ipaddress_id']",
                                   js_send_keys=ip_addresses)
        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def update_auth_provider_nis(self, name_to_be_updated, name=None, domain_name=None, ip_addresses=None, check=None):
        """
        修改NIS认证服务器
        :param name_to_be_updated: 需要修改的认证服务器的名称
        :param name:
        :param domain_name:
        :param ip_addresses:
        :param check:
        :return:
        """
        log.info("update authorize provider nis")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击NIS按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'NIS')]", check=True).click()

        # 勾选指定的nis认证服务器名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name_to_be_updated)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击修改
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_update_button']").click()

        # 输入NIS认证服务器相关信息
        if name is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_name_id']", js_send_keys=name)
        if domain_name is not None:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_domain_name_id']",
                                       js_send_keys=domain_name)
        if ip_addresses is not None:
            self.find_element_by_xpath(
                "//*[@id='ofs_auth_provider_nis_operation_primary_ipaddress_id']", js_send_keys=ip_addresses)
        if check:
            self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_test_connection']").click()
            self.implicit_wait("//*[starts-with(text(), '连接成功')]")

            # 点击确定,如果未连接成功，会超时报错
            self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'info')]").click()

        # 点击确认添加认证服务器
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_operation_window-btn-0']").click()

        # 检查添加完成
        self.check_element_done()
        return

    def delete_auth_provider_nis(self, name_to_be_deleted):
        log.info("delete authorize provider nis")

        # 定位到认证服务器
        self.locate_auth_provider()

        # 点击NIS按钮
        self.find_element_by_xpath("//a[starts-with(text(), 'NIS')]", check=True).click()

        # 勾选指定的nis认证服务器名称
        obj_update = self.find_element_by_xpath("//*[@title='%s']/../..//input" % name_to_be_deleted)
        if obj_update.is_selected() is False:
            self.execute_script_click(dom=obj_update)

        # 点击删除
        self.find_element_by_xpath("//*[@id='ofs_auth_provider_nis_delete_button']").click()

        # 点击确认删除NIS
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查删除成功
        self.check_element_done()
        return

    def create_access_zone(self, name, auth_provider_name=None, nodes_all=False, node_hostname_list=None,
                           enable_nas=False, nfs=False, smb=False, ftp=False, s3=False):
        """
        author:duyuli
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
            for i in range(10):    # 避免全选点击后子项未加载完成的情况
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
        s3_xpath = "//*[@id='protocolSetting-object-s3-box']"

        smb_obj = self.find_element_by_xpath(smb_xpath)
        nfs_obj = self.find_element_by_xpath(nfs_xpath)
        ftp_obj = self.find_element_by_xpath(ftp_xpath)
        s3_obj = self.find_element_by_xpath(s3_xpath)

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

            if s3_obj.is_selected():
                self.execute_script_click(dom=s3_obj)

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

        if s3:
            if s3_obj.is_selected() is False:
                self.execute_script_click(xpath=s3_xpath)
        else:
            if s3_obj.is_selected():
                self.execute_script_click(xpath=s3_xpath)

        # 单击完成
        self.find_element_by_xpath("//*[@id='access_zone_create_window_step2-btn-1']").click()

        # 单击确定创建  starts-with  contains
        self.find_element_by_xpath("//div[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 等待创建完成
        log.info("wait enable nas")
        self.check_element_done(time_out=600, check_by_click=True)
        return

    def delete_access_zone(self, name):
        """
        :param name:
        :return:
        """
        log.info("begin to delete access zone")

        # 定位到访问分区
        self.locate_access_zone()

        is_enable_nas_start_stat = False

        # 勾选待删除的访问分区
        self.find_element_by_xpath("//div[starts-with(text(),'%s')]/../../div/label/s" % name, check=True).click()

        # 点击服务设置
        self.find_element_by_xpath("//*[@id='access_zone_bn_protocol_setting']").click()

        # smb nfs ftp s3 等服务置为空
        smb_xpath = "//*[@id='protocolSetting-nas-smb-box']"
        nfs_xpath = "//*[@id='protocolSetting-nas-nfs-box']"
        ftp_xpath = "//*[@id='protocolSetting-nas-ftp-box']"
        s3_xpath = "//*[@id='protocolSetting-object-s3-box']"

        smb_obj = self.find_element_by_xpath(smb_xpath)
        nfs_obj = self.find_element_by_xpath(nfs_xpath)
        ftp_obj = self.find_element_by_xpath(ftp_xpath)
        s3_obj = self.find_element_by_xpath(s3_xpath)

        if smb_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(smb_xpath)  # box 类型反选
        if nfs_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(nfs_xpath)
        if ftp_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(ftp_xpath)
        if s3_obj.is_selected():
            is_enable_nas_start_stat = True
            self.execute_script_click(s3_xpath)

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

        return

    def disable_or_enable_nas(self, access_zone_name, smb=False, nfs=False, ftp=False, s3=False):
        # 停用nas协议，默认关闭nas
        log.info("disable or enable nas")

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

        if s3:
            obj_s3 = self.find_element_by_xpath("//*[@id='protocolSetting-object-s3-box']")
            if obj_s3.is_selected() is False:
                self.execute_script_click(dom=obj_s3)

        else:
            obj_s3 = self.find_element_by_xpath("//*[@id='protocolSetting-object-s3-box']")
            if obj_s3.is_selected():
                self.execute_script_click(dom=obj_s3)

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
                      eth_name_list, domain_name, ip_address_pool_list):
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

        # 点击确定增加ip地址池
        self.find_element_by_xpath("//*[@id='VIPAddrPoolCreateWindow-btn-0']").click()

        # 检查添加完成
        self.check_element_done(time_out=1200, check_by_click=True)
        return

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
        return

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
        return

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

    def create_group_user(self, group_name, user_name, auth_provider_name):
        log.info("begin to create group user")

        # 定位到用户/用户组
        self.locate_user_group()

        # 选择域名服务器
        self.select_by_text("//*[@id='user_group_main_tab_combo_id']", auth_provider_name, check=True)

        # 点击用户组
        self.find_element_by_xpath("//*[@id='tabCard']/li[2]/a").click()

        # 点击创建用户组
        self.find_element_by_xpath("//*[@id='group_tab_bn_create']/i").click()

        # 输入用户组name
        self.find_element_by_xpath("//*[@id='ofs_user_group_group_create_group_name_id']", js_send_keys=group_name)

        # 点击确定创建用户组
        self.find_element_by_xpath("//*[@id='group_create_window-btn-0']").click()

        # 检查用户组创建完成
        self.check_element_done()

        # 点击用户按钮
        self.find_element_by_xpath("//*[@id='tabCard']/li[1]/a").click()

        # 点击创建用户
        self.find_element_by_xpath("//*[@id='user_tab_bn_create']/i").click()

        # 输入用户name，passwd， 选择主组
        self.find_element_by_xpath("//*[@id='ofs_user_group_user_create_username_id']", js_send_keys=user_name)
        self.find_element_by_xpath("//*[@id='ofs_user_group_user_create_password_id']", js_send_keys="111111")
        self.find_element_by_xpath("//*[@id='ofs_user_group_user_create_main_group']/div/i").click()
        self.find_element_by_xpath("//*[@title='%s']/../../div/label/s" % group_name).click()

        # 点击确定选择主组
        self.find_element_by_xpath("//*[@id='user_group_main_group_list_window-btn-0']").click()

        # 点击确定创建用户
        self.find_element_by_xpath("//*[@id='user_create_window-btn-0']").click()

        # 等待创建完成
        self.check_element_done(check_by_click=True)
        return

    def delete_group_user(self, group_name, user_name, auth_provider_name, all_user=True):
        log.info("begin to delete group user")

        # 定位到用户/用户组
        self.locate_user_group()

        # 选择域名服务器
        self.select_by_text("//*[@id='user_group_main_tab_combo_id']", auth_provider_name, check=True)

        # 点击用户按钮
        self.find_element_by_xpath("//*[@id='tabCard']/li[1]/a").click()

        # 勾选指定删除的用户名
        if all_user:
            self.find_element_by_xpath("//*[@id='subnet_grid']/div[2]/div/div/div/div/div/div/label/s").click()
        else:
            self.find_element_by_xpath("//*[@title='%s']/../../div/label/s" % user_name).click()

        # 点击删除
        self.find_element_by_xpath("//*[@id='user_tab_bn_delete']/i").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定删除用户
        self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()

        # 点击关闭
        for i in range(31):
            if i == 30:
                raise Exception("close user delete failed")
            if self.find_element_by_xpath("//*[@id='executeStatus-0']").text == "成功":
                self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()
                break
            else:
                time.sleep(1)

        # 点击用户组按钮
        self.find_element_by_xpath("//*[@id='tabCard']/li[2]/a").click()

        # 点击指定用户组
        self.find_element_by_xpath("//*[@title='%s']" % group_name).click()

        # 点击删除
        self.find_element_by_xpath("//*[@id='group_tab_bn_delete']/i").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定删除group
        self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()

        # 等待删除成功
        self.check_element_done()
        return


class Quota(Access_Manage, File):
    """目录配额"""

    def locate_dir_quota(self):
        """资源管理 ---> 文件 ---> 目录配额"""
        self.locate_file()
        self.find_element_by_xpath("//*[@id='ofs_quota']/a", check_by_click=True).click()
        return

    def create_quota(self, path, auth_provider_name=None, user_type=None, user_or_group_name=None,
                     logical_quota_cal_type=None, logical_hard_threshold=None, logical_soft_threshold=None,
                     logical_grace_time=None, logical_suggest_threshold=None,
                     filenr_quota_cal_type=None, filenr_hard_threshold=None, filenr_soft_threshold=None,
                     filenr_grace_time=None, filenr_suggest_threshold=None):
        """
        :author:duyuli
        :path :      eg  volume:/quota_test_dir
        :time:20181123
        :阈值设定单位：  logical_hard_threshold（GB）
                        logical_grace_time（天）
                        filenr_hard_threshold（千）
        :return:
        """
        log.info("begin to create quota")

        # 定位到配额
        self.locate_dir_quota()

        volume_name = path.split(":")[0]
        path_list = path.split(":")[1].split("/")[1:]

        # 创建配额
        self.find_element_by_xpath("//*[@id='quota_bn_create']", check=True).click()

        # 创建配额 -> 路径
        self.find_element_by_xpath("//*[@id='quota_operate_path_input']/div/i").click()

        # 选择卷,选择卷时需要双击
        obj_stdout = self.find_element_by_xpath("//*[@class='default-cell' and @title='%s']" % volume_name)
        ActionChains(self.driver).double_click(obj_stdout).perform()

        # 选择具体路径
        for path_quota in path_list:
            obj_stdout = self.find_element_by_xpath("//*[@class='default-cell' and @title='%s']" % path_quota)
            ActionChains(self.driver).double_click(obj_stdout).perform()

        # 单击确定路径
        self.find_element_by_xpath("//*[@id='fs_file_path_browse_window-btn-0']", check=True).click()

        # 选择认证服务器
        if auth_provider_name:
            self.select_by_text("//*[@id='ofs_quota_operate_auth_provider_combo']", auth_provider_name)

            # 选择用户、用户组
            self.select_by_val("//*[@id='ofs_quota_operate_user_type_combo']", user_type)
            self.find_element_by_xpath("//*[@id='quota_operate_user_input']/div/child::node()[last()]").click()

            # 勾选用户或用户组
            self.execute_script_click(xpath="//*[@title='%s']/../../div/label/input" % user_or_group_name)

            # 点击确定
            self.find_element_by_xpath("//*[@id='ofs_auth_get_user_list_window-btn-0']").click()

        # 拖动滚动条
        for i in range(5):
            js = "$(\"div[id='ofs_quota_create_window']\").find('.mCSB_container').css('top', '-390px')"
            self.driver.execute_script(js)
            if self.find_element_by_xpath("//*[@id='filenr_quota_cal_type_combo']").is_displayed():
                break
            time.sleep(0.5)

        # 选择不同类型的配额，逻辑空间阈值
        if logical_quota_cal_type == "QUOTA_COMPUTE":
            self.select_by_val("//*[@id='logical_quota_cal_type_combo']", "QUOTA_COMPUTE")

        if logical_quota_cal_type == "QUOTA_LIMIT":
            self.select_by_val("//*[@id='logical_quota_cal_type_combo']", "QUOTA_LIMIT")

            if logical_hard_threshold:
                # 采用js（不用send_keys()）主要是解决send.keys()在chrome浏览器中兼容性不好的情况
                js_hard = "$('#logical_hard_threshold_field').val(%s)" % logical_hard_threshold
                self.driver.execute_script(js_hard)

            if logical_soft_threshold:
                js_soft = "$('#logical_soft_threshold_field').val(%s)" % logical_soft_threshold
                self.driver.execute_script(js_soft)

                js_time = "$('#logical_grace_time_field').val(%s)" % logical_grace_time
                self.driver.execute_script(js_time)

            if logical_suggest_threshold:
                js_suggest = "$('#logical_suggest_threshold_field').val(%s)" % logical_suggest_threshold
                self.driver.execute_script(js_suggest)

        # 选择不同类型的配额，inode阈值
        if filenr_quota_cal_type == 'QUOTA_COMPUTE':
            self.select_by_val("//*[@id='filenr_quota_cal_type_combo']", "QUOTA_COMPUTE")

        if filenr_quota_cal_type == 'QUOTA_LIMIT':
            self.select_by_val("//*[@id='filenr_quota_cal_type_combo']", "QUOTA_LIMIT")

            if filenr_hard_threshold:
                js_nr_hard = "$('#filenr_hard_threshold_field').val(%s)" % filenr_hard_threshold
                self.driver.execute_script(js_nr_hard)

            if filenr_soft_threshold:
                js_nr_soft = "$('#filenr_soft_threshold_field').val(%s)" % filenr_soft_threshold
                self.driver.execute_script(js_nr_soft)

                js_time = "$('#filenr_grace_time_field').val(%s)" % filenr_grace_time
                self.driver.execute_script(js_time)

            if filenr_suggest_threshold:
                js_nr_suggest = "$('#filenr_suggest_threshold_field').val(%s)" % filenr_suggest_threshold
                self.driver.execute_script(js_nr_suggest)

        # 单击确定创建配额
        self.find_element_by_xpath("//*[@id='ofs_quota_create_window-btn-0']").click()

        # 等待创建完成
        self.check_element_done()
        return

    def modify_quota(self, path, logical_quota_cal_type, logical_hard_threshold=None, logical_soft_threshold=None,
                     logical_grace_time=None, logical_suggest_threshold=None,
                     filenr_quota_cal_type=None, filenr_hard_threshold=None, filenr_soft_threshold=None,
                     filenr_grace_time=None, filenr_suggest_threshold=None):
        log.info("modefy quota")

        # 定位到配额
        self.locate_dir_quota()

        # 勾选指定路径配额
        self.execute_script_click(xpath="//*[@title='%s']/../../..//input" % path, check=True)

        # 点击修改
        self.find_element_by_xpath("//*[@id='quota_bn_modify']/i").click()

        # 拖动滚动条
        for i in range(5):
            js = "$(\"div[id='ofs_quota_update_window']\").find('.mCSB_container').css('top', '-390px')"
            self.driver.execute_script(js)
            if self.find_element_by_xpath("//*[@id='filenr_quota_cal_type_combo']").is_displayed():
                break
            time.sleep(0.5)

        # 选择不同类型的配额，逻辑空间阈值
        if logical_quota_cal_type == "QUOTA_COMPUTE":
            self.select_by_val("//*[@id='logical_quota_cal_type_combo']", "QUOTA_COMPUTE")

        if logical_quota_cal_type == "QUOTA_LIMIT":
            self.select_by_val("//*[@id='logical_quota_cal_type_combo']", "QUOTA_LIMIT")

            if logical_hard_threshold is not None:
                js = "$('#logical_hard_threshold_field').val(%s)" % logical_hard_threshold
                self.driver.execute_script(js)

            if logical_soft_threshold is not None:
                js_soft = "$('#logical_soft_threshold_field').val(%s)" % logical_soft_threshold
                self.driver.execute_script(js_soft)

                js_time = "$('#logical_grace_time_field').val(%s)" % logical_grace_time
                self.driver.execute_script(js_time)

            if logical_suggest_threshold is not None:
                js_time = "$('#logical_suggest_threshold_field').val(%s)" % logical_suggest_threshold
                self.driver.execute_script(js_time)

        # 选择不同类型的配额，inode阈值
        if filenr_quota_cal_type == 'QUOTA_COMPUTE':
            self.select_by_val("//*[@id='filenr_quota_cal_type_combo']", "QUOTA_COMPUTE")

        if filenr_quota_cal_type == 'QUOTA_LIMIT':
            self.select_by_val("//*[@id='filenr_quota_cal_type_combo']", "QUOTA_LIMIT")

            if filenr_hard_threshold is not None:
                js_time = "$('#filenr_hard_threshold_field').val(%s)" % filenr_hard_threshold
                self.driver.execute_script(js_time)

            if filenr_soft_threshold is not None:
                js_time = "$('#filenr_soft_threshold_field').val(%s)" % filenr_soft_threshold
                self.driver.execute_script(js_time)

                js_time = "$('#filenr_grace_time_field').val(%s)" % filenr_grace_time
                self.driver.execute_script(js_time)

            if filenr_suggest_threshold is not None:
                js_time = "$('#filenr_suggest_threshold_field').val(%s)" % filenr_suggest_threshold
                self.driver.execute_script(js_time)

        # 单击确定创建配额
        self.find_element_by_xpath("//*[@id='ofs_quota_update_window-btn-0']").click()

        # 等待创建完成
        self.check_element_done()
        return

    def delete_quota(self, path):
        """
        :author:duyuli
        :time:20181123
        :path : eg   volume:/quota_test_dir
        :return:
        """
        log.info("begin to delete quota")

        # 定位到配额
        self.locate_dir_quota()

        # 勾选指定路径配额
        self.find_element_by_xpath("//*[@class='default-cell' and @title='%s']/../../div/label/s" % path,
                                   check=True).click()

        # 勾选删除
        self.find_element_by_xpath("//*[@id='quota_bn_delete']").click()

        # 点击确定
        self.find_element_by_xpath("//*[contains(@id,'btn-0')]").click()

        # 等待删除成功
        self.check_element_done()
        return

    def get_quota_used_capacity(self, quota_path):
        # 检查配额已用容量
        log.info("check quota used capacity")

        # 定位到配额
        self.locate_dir_quota()

        # 查看已用容量并返回
        text_value = self.find_element_by_xpath(
            "//*[@title='%s']/../../../div[5]/div" % quota_path, check_by_click=True).text
        used_capacity = text_value.split()[-2]

        return used_capacity

    def check_quota_until_valid(self, quota_path):
        # 检查配额生效

        # 定位到配额
        self.locate_dir_quota()

        # 检查直到配额生效
        for i in range(300):
            # 点击刷新
            self.execute_script_click(xpath="//*[@id='quota_bn_refresh']", check=True)

            text_value = self.find_element_by_xpath(
                "//*[@title='%s']/../../../div[7]/div" % quota_path, check_by_click=True).text
            if text_value == "生效":
                break
            time.sleep(2)
            if i == 299:
                raise Exception("check quota until valid timeout 10min")
        return


class protocol_file(First_Level_Label):
    """文件系统协议"""
    def locate_protocol_file(self):
        """协议管理--->文件"""
        self.locate_protocol_manage()
        xpath = "//*[@id='ofs_protocol_file']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return


class Protocol_Object(First_Level_Label):
    """对象协议"""
    def locate_protocol_object(self):
        """协议管理--->对象"""
        self.locate_protocol_manage()
        xpath = "//*[@id='ofs_protocol_object']/a/child::node()[last()]"
        self.check_href_until_on(xpath)
        return


class Client_Auth(protocol_file):
    """授权客户端"""
    def locate_posix(self):
        """协议管理--->文件--->posix"""
        self.locate_protocol_file()
        self.find_element_by_xpath("//*[@id='ofs_posix']/a", check_by_click=True).click()
        return

    def create_posix_auth(self, volume_name_list, client_ips_list):
        """
        输入单个或者多个ip的list
        :param volume_name_list: volume1
        :param client_ips_list: eg   ["10.2.42.101-110", "10.2.42.101"]
        :return:
        """
        log.info("add client posix authorize")

        # 定位到POSIX
        self.locate_posix()

        # 点击添加按钮
        self.find_element_by_xpath("//*[@id='posix_bn_create']", check=True).click()

        # 点击选择文件系统
        self.find_element_by_xpath("//*[@id='posix_select_volume_button']").click()

        # 勾选文件系统
        for volume_name in volume_name_list:
            self.find_element_by_xpath("//*[@title='%s']/../..//s" % volume_name).click()

        # 点击确定
        self.find_element_by_xpath("//*[@id='posix_volume_window-btn-0']").click()

        # 输入授权的ip
        text = "\\n".join(client_ips_list)
        self.find_element_by_xpath("//*[@id='posix_config_ip_input']", js_send_keys=text)

        # 点击确定添加
        self.find_element_by_xpath("//*[@id='posix_add_window-btn-0']").click()

        # 检查创建完成
        self.check_element_done()
        return

    def delete_posix_auth(self, client_ips_list):
        """
        输入单个或者多个ip的list
        :param client_ips_list: ["10.2.42.101-110", "10.2.42.101"]
        :return:
        """
        log.info("delete client auth")

        # 定位到POSIX
        self.locate_posix()

        # 10.2.42.101,10.2.42.106-110
        client_ips = ",".join(client_ips_list)

        # 勾选指定授权ip
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % client_ips, check=True)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击删除
        self.find_element_by_xpath("//*[@id='posix_bn_delete']").click()

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 检查删除成功
        self.check_element_done(check_by_click=True)
        return

    def update_posix_auth(self, volume_name, volume_name_list=None, client_ips_list=None, auto_mount=True):
        log.info("update posix authorize")

        # 定位到posix授权
        self.locate_posix()

        # 勾选指定文件系统
        self.find_element_by_xpath(
            "//*[starts-with(text(), '%s')]/../..//s" % volume_name, check_by_click=True).click()

        # 点击修改
        self.execute_script_click(xpath="//*[@id='posix_bn_update']")

        if volume_name_list:
            # 点击选择文件系统(有遮挡，采用js的点击动作)
            self.execute_script_click(xpath="//*[@id='posix_select_volume_button']")

            # 勾选文件系统
            for volume_name in volume_name_list:
                self.execute_script_click(xpath="//*[@title='%s']/../..//input" % volume_name)

            # 点击确定
            self.find_element_by_xpath("//*[@id='posix_volume_window-btn-0']").click()

        if client_ips_list:
            # 输入授权的ip
            text = "\\n".join(client_ips_list)
            self.find_element_by_xpath("//*[@id='posix_config_ip_input']", js_send_keys=text)

        # 修改自动挂载
        obj_auto_mount = self.find_element_by_xpath("//*[@id='posix_config_attr_auto_mount']")
        if auto_mount:
            if obj_auto_mount.is_selected() is False:
                self.execute_script_click(dom=obj_auto_mount)
        else:
            if obj_auto_mount.is_selected():
                self.execute_script_click(dom=obj_auto_mount)

        # 点击确定修改
        self.find_element_by_xpath("//*[@id='posix_update_window-btn-0']").click()

        # 检查修改完成
        self.check_element_done()
        return


class Nas_Protocol(protocol_file):
    """nas文件系统协议"""
    def locate_smb(self):
        """协议管理--->文件--->smb"""
        self.locate_protocol_file()
        self.find_element_by_xpath("//*[@id='ofs_smb']/a", check_by_click=True).click()
        return

    def locate_nfs(self):
        """协议管理--->文件--->nfs"""
        self.locate_protocol_file()
        self.find_element_by_xpath("//*[@id='ofs_nfs']/a", check_by_click=True).click()
        return

    def locate_ftp(self):
        """协议管理--->文件--->ftp"""
        self.locate_protocol_file()
        self.find_element_by_xpath("//*[@id='ofs_ftp']/a", check_by_click=True).click()
        return


class Alarms_Events(First_Level_Label):
    """告警事件"""
    def locate_current_alarms(self):
        """告警事件--->实时告警"""
        self.locate_alarm_event()
        self.find_element_by_xpath("//*[@id='ofs_currentalarms']/a", check_by_click=True).click()
        return

    def locate_all_events(self):
        """告警事件--->所有事件"""
        self.locate_alarm_event()
        self.find_element_by_xpath("//*[@id='ofs_allevents']/a", check_by_click=True).click()
        return

    def check_alarms(self, name, timeout=600):
        """检查告警"""
        # 定位到实时告警
        self.locate_current_alarms()

        count = 1
        while True:
            # 超时则退出
            if count * 3 >= timeout:
                log.info("check alarms timeout")
                raise Exception("check alarms failed")

            obj = self.driver.find_elements_by_xpath("//*[starts-with(text(),'%s')]" % name)
            if len(obj) != 0:
                log.info("check alarms right")
                break
            else:
                time.sleep(3)
                count += 1

                # 有可能上次刷新还未显示完毕
                self.check_element_done(time_out=timeout)

                self.driver.find_element_by_xpath("//*[@id='ofs_alarm_active_refresh']").click()
        return

    def check_events(self, event_name, time1, timeout=300):
        """检查事件"""
        # 定位到事件
        self.locate_all_events()

        # 点开100条/页
        self.find_element_by_xpath("//*[@class='kuma-select2-arrow']", check_by_click=True).click()

        # 选择100条/页
        self.find_element_by_xpath("//*[starts-with(text(),'100条/页')]").click()

        count = 1
        while True:
            # 超时则退出
            if count * 3 >= timeout:
                log.info("check alarms timeout")
                raise Exception("check alarms failed")

            obj = self.driver.find_elements_by_xpath("//*[starts-with(text(),'%s')]" % event_name)

            if len(obj) != 0:
                # 判断时间在脚本执行后
                time2 = self.find_element_by_xpath(
                    "//*[starts-with(text(),'%s')]/../../../div[4]/div" % event_name).text
                if self.check_time_earlier_or_later(time1, time2) > 0:
                    log.info("check events right")
                    break

            time.sleep(3)
            count += 1

            # 有可能上次刷新还未显示完毕
            self.check_element_done(time_out=timeout)

            self.driver.find_element_by_xpath("//*[@id='ofs_all_event_refresh']").click()
        return

    def all_events_search_function(self, happen_time, desc_or_level, start_time=None, end_time=None, description=None,
                                   level=None):
        """
        所有事件界面搜索功能
        :param happen_time:     unlimited(不限) or custom(自定义)
        :param desc_or_level:   desc(描述) or level(等级)
        :param start_time:      2018-12-15 11:19:22
        :param end_time:        2018-12-15 11:19:22
        :param description:     （输入搜索的关键字）
        :param level:           None（全部）or 0（提示）or 1（警告）or 2（严重）or 3（致命）
        :return:
        """
        log.info("all events search function")

        # 定位到所有事件
        self.locate_all_events()

        # 选择发生时间
        self.select_by_val("//*[@id='ofs_all_event_search_start_time_label_id']", happen_time, check=True)

        if start_time:
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_start_time_start_id']", js_send_keys=start_time)

        if end_time:
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_start_time_end_id']", js_send_keys=end_time)

        # 选择描述或者等级搜索
        self.select_by_val(xpath="//*[@id='ofs_all_event_search_type_id']", val=desc_or_level)

        if description:
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_content_id']", js_send_keys=description)

        level_name = None
        if level:
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_content_id']").click()
            level_name = self.find_element_by_xpath(
                "//*[@id='ofs_all_event_search']//ul/li[%s]" % (int(level) + 2)).text
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_content_id']", js_send_keys=level_name)
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_content_id']/../input[@type='hidden']",
                                       js_send_keys=level)
            self.find_element_by_xpath("//*[@id='ofs_all_event_search_content_id']/..//li[@data='%s']" % level).click()

        # 点击搜索
        self.find_element_by_xpath("//*[@id='ofs_all_event_search']//i").click()

        # 如果搜索结果为空,暂无数据
        time.sleep(2)
        obj_search_list = self.driver.find_elements_by_xpath(
            "//*[@id='ofs_all_event_grid_id']//div[@class='kuma-uxtable-body-scroll kuma-uxtable-no-v-scroll']/div/div")
        if obj_search_list:
            log.info("no search result")
            return

        # 检查按时间搜索的正确性
        if happen_time == "custom":
            # 第一页第一条搜索项
            first_menu_time = self.find_element_by_xpath("//*[@id='ofs_all_event_table']//li[1]/div/div[4]/div").text

            # 最后一页最后一条搜索项
            self.find_element_by_xpath(
                "//*[@id='ofs_all_event_table']//ul[contains(@class, 'kuma-page')]/li[last()-1]").click()
            last_menu_time = self.find_element_by_xpath(
                "//*[@id='ofs_all_event_table']//ul/child::node()[1]/div/div[4]/div").text

            if self.check_time_earlier_or_later(start_time, first_menu_time) > 0 > self.check_time_earlier_or_later(
                    end_time, last_menu_time):
                log.info("check event search by time right")

            else:
                log.info("failed %s %s %s %s" % (start_time, first_menu_time, last_menu_time, end_time))
                raise Exception("check event search by time failed")

        # 检查按 描述 搜索的正确性
        if desc_or_level == "desc" and description:
            xpath = "//*[@id='ofs_all_event_table']//li/div/div[3]/div/a"
            self.implicit_wait(xpath)
            obj_list = self.driver.find_elements_by_xpath(xpath)
            for obj in obj_list:
                if description != obj.text:
                    log.info("%s %s" % (description, obj.text))
                    raise Exception("check event search by description failed")
            log.info("check event search by description right")

        # 检查按 等级 搜索的正确性
        if desc_or_level == "level" and level:
            xpath = "//*[@id='ofs_all_event_table']//li/div/div[2]/div/font"
            self.implicit_wait(xpath)
            obj_list = self.driver.find_elements_by_xpath(xpath)
            for obj in obj_list:
                if level_name != obj.text:
                    log.info("%s %s" % (level_name, obj.text))
                    raise Exception("check event search by level failed")
            log.info("check event search by level right")

        # 检查搜索完成
        self.check_element_done()
        return


class Nas(Access_Manage, Nas_Protocol):
    """nas"""
    def create_smb_share(self, path, access_zone_name, share_name, auth_access_control, user_name=None,
                         group_name=None):
        """
        :param path:                 volume1:smb_share
        :param access_zone_name:     testzone
        :param share_name:           share_smb
        :param auth_access_control:  ro
                                      rw
                                      full_control
        :param user_name:            user_name
        :param group_name:           group_name
        :return:
        """
        log.info("create smb share")

        # 定位到smb
        self.locate_smb()

        path_list = []
        volume_name = path.split(":")[0]
        path_list.append(volume_name)
        path_list.extend(path.split(":")[1].split("/")[1:])

        # 选择访问分区
        self.select_by_text("//*[@id='ofs_accesszone_selector']", access_zone_name, check=True)

        # 点击创建
        self.find_element_by_xpath("//*[@id='smb_bn_create']").click()

        # 填写共享名称
        self.find_element_by_xpath("//*[@id='smb_operate_step1_name']", js_send_keys=share_name)

        # 点击共享目录
        self.find_element_by_xpath("//*[@id='smb_operate_step1_path_div']//i[@class='icon-search']").click()

        # 选择共享目录
        for dir_smb in path_list:
            obj = self.find_element_by_xpath("//*[@title='%s']" % dir_smb)
            ActionChains(self.driver).double_click(obj).perform()

        # 点击确定共享目录
        self.find_element_by_xpath("//*[@id='fs_file_path_browse_window-btn-0']", check=True).click()

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_smb_create_window-btn-0']").click()

        # 点击完成共享
        self.find_element_by_xpath("//*[@id='ofs_smb_create_step2_window-btn-1']").click()

        # 点击确定完成
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 勾选该smb共享
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % path)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击添加用户
        self.find_element_by_xpath("//*[@id='smb_auth_bn_add_div']/i").click()

        # 选中用户或用户组
        user_or_group_name = None
        if user_name:
            obj = self.find_element_by_xpath("//*[@id='ofs_auth_user_type_user']")
            if obj.is_selected() is False:
                self.execute_script_click(dom=obj)
            user_or_group_name = user_name

        if group_name:
            obj = self.find_element_by_xpath("//*[@id='ofs_auth_user_type_group']")
            if obj.is_selected() is False:
                self.execute_script_click(dom=obj)
            user_or_group_name = user_name

        # 点击搜索名称
        self.find_element_by_xpath("//*[@id='ofs_auth_user_searcher_div']//i").click()

        # 选中用户组或用户
        self.find_element_by_xpath("//*[@title='%s']/../../div/label/s" % user_or_group_name).click()

        # 点击确定用户用户组
        self.find_element_by_xpath("//*[@id='ofs_auth_get_user_list_window-btn-0']").click()

        # 选择权限
        self.move_scroll_bar_by_top("-66")
        self.select_by_val("//*[@id='ofs_auth_access_control_checkbox']", auth_access_control)

        # 点击确定添加
        self.find_element_by_xpath("//*[@id='ofs_smb_add_auth_window-btn-0']").click()

        # 点击确定
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 检查完成
        self.check_element_done()
        return

    def delete_smb_share(self, path):
        log.info("delete smb share")

        # 定位到smb
        self.locate_smb()

        # 勾选指定路径的smb
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % path, check=True)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击删除
        self.find_element_by_xpath("//*[@id='smb_bn_delete']").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]").click()

        # 检查完成
        self.check_element_done()
        return

    def create_nfs_share(self, path, access_zone_name, share_name, auth_access_control, client_nfs_ip):
        """
        :param path:                   eg    volume1:/quota_test_dir
        :param access_zone_name:       eg    testzone
        :param share_name:             eg    nfs_share
        :param auth_access_control:    eg    ro
                                        eg    rw
        无删除和重命名权限               eg    rw_nodelsacl
        :param client_nfs_ip:          eg    *
                                        eg    10.2.42.102/22
        :return:
        """
        log.info("create nfs share")

        # 定位到nfs
        self.locate_nfs()

        path_list = []
        volume_name = path.split(":")[0]
        path_list.append(volume_name)
        path_list.extend(path.split(":")[1].split("/")[1:])

        # 选择访问分区
        self.select_by_text("//*[@id='ofs_nfs_access_selector']", access_zone_name)

        # 点击创建
        self.find_element_by_xpath("//*[@id='nfs_bn_create']").click()

        # 填写共享名称
        self.find_element_by_xpath("//*[@id='nfs_operate_step1_name']", js_send_keys=share_name)

        # 点击共享目录
        self.find_element_by_xpath("//*[@id='nfs_operate_step1_path_div']//i[@class='icon-search']").click()

        # 选择共享目录
        for dir_nfs in path_list:
            obj = self.find_element_by_xpath("//*[@title='%s']" % dir_nfs)
            ActionChains(self.driver).double_click(obj).perform()

        # 点击确定共享目录
        self.find_element_by_xpath("//*[@id='fs_file_path_browse_window-btn-0']", check=True).click()

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_nfs_create_window-btn-0']").click()

        # 点击完成共享
        self.find_element_by_xpath("//*[@id='ofs_nfs_create_step2_window-btn-1']").click()

        # 点击确定完成
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 勾选该nfs共享
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % path, check_by_click=True)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击添加nfs客户端
        self.find_element_by_xpath("//*[@id='nfs_client_bn_add_div']/i").click()

        # 填写nfs client ip
        self.find_element_by_xpath("//*[@id='ofs_nfs_client_ip_address']", js_send_keys=client_nfs_ip)

        # 选择权限
        self.select_by_val("//*[@id='ofs_nfs_client_permission_level']", auth_access_control)

        # 点击确定添加
        self.find_element_by_xpath("//*[@id='ofs_nfs_add_client_window-btn-0']").click()

        # 点击确定
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'comfirm')]").click()

        # 检查完成
        self.check_element_done()
        return

    def delete_nfs_share(self, path):
        log.info("delete nfs share")

        # 定位到nfs
        self.locate_nfs()

        # 勾选指定路径的nfs
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % path, check=True)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击删除
        self.find_element_by_xpath("//*[@id='nfs_bn_delete']").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确认删除
        self.execute_script_click(xpath="//*[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]")

        # 检查完成
        self.check_element_done()
        return

    def create_ftp_share(self, path, access_zone_name, user_name):
        log.info("create ftp share")

        # 定位到ftp
        self.locate_ftp()

        path_list = []
        volume_name = path.split(":")[0]
        path_list.append(volume_name)
        path_list.extend(path.split(":")[1].split("/")[1:])

        # 选择访问分区
        self.select_by_text("//*[@id='ofs_accesszone_selector']", access_zone_name, check=True)

        # 点击创建
        self.find_element_by_xpath("//*[@id='ftp_bn_create']").click()

        # 点击共享目录
        self.find_element_by_xpath("//*[@id='ftp_operate_path_div']//i[@class='icon-search']").click()

        # 选择共享目录
        for dir_ftp in path_list:
            obj = self.find_element_by_xpath("//*[@title='%s']" % dir_ftp)
            ActionChains(self.driver).double_click(obj).perform()

        # 点击确定共享目录
        self.find_element_by_xpath("//*[@id='fs_file_path_browse_window-btn-0']", check=True).click()

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_ftp_create_window-btn-0']").click()

        # 点击添加用户
        self.find_element_by_xpath("//*[@id='ftp_operate_step2_add_bn']").click()

        # 点击搜索
        self.find_element_by_xpath("//*[@id='ofs_auth_user_searcher_div']//i").click()

        # 勾选指定用户
        self.find_element_by_xpath("//*[@title='%s']/../..//s" % user_name).click()

        # 点击确定用户
        self.find_element_by_xpath("//*[@id='ofs_auth_get_user_list_window-btn-0']").click()

        # 点击确定授权
        self.find_element_by_xpath("//*[@id='ofs_ftp_add_auth_window-btn-0']").click()

        # 点击完成共享
        self.find_element_by_xpath("//*[@id='ofs_ftp_create_step2_window-btn-1']").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]").click()

        # 点击关闭执行结果
        for i in range(31):
            if i == 30:
                raise Exception("close user delete failed")
            if self.find_element_by_xpath("//*[@id='executeStatus-0']").text == "成功":
                self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'msgbox')]").click()
                break
            else:
                time.sleep(1)
        return

    def delete_ftp_share(self, path):
        log.info("delete ftp share")

        # 定位到ftp
        self.locate_ftp()

        # 勾选指定路径的nfs
        obj = self.find_element_by_xpath("//*[@title='%s']/../..//input" % path, check=True)
        if obj.is_selected() is False:
            self.execute_script_click(dom=obj)

        # 点击删除
        self.find_element_by_xpath("//*[@id='ftp_bn_delete']").click()

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确认删除
        self.find_element_by_xpath("//*[contains(@id,'btn-0') and starts-with(@id,'riskComfirm')]").click()

        # 检查完成
        self.check_element_done(check_by_click=True)
        return


class System_Install(First_Level_Label):
    """系统安装"""

    def install_parastor(self, tar_path, parastor_name, control_ip_list, data_ip_dict, vir_pyh, cabinet_name="cabinet",
                         cabinet_start_num="1", cabinet_end_num="2", cabinet_height="42"):
        """
        部署系统
        :param vir_pyh: 是否为虚拟机
        :param tar_path:安装包路径
        :param parastor_name:
        :param control_ip_list:
        :param data_ip_dict:{"10.2.42.151": ["20.xxx", "30.xxx"], "10.2.42.152": ["20.xxx", "30.xxx"]}
        :param cabinet_name:机柜名称
        :param cabinet_start_num:
        :param cabinet_end_num:
        :param cabinet_height:
        :return:
        """
        log.info("start to install parastor")

        path_list = tar_path.split('/')[1:]

        # 点击部署新系统
        self.find_element_by_xpath("//*[@id='ofs_select_storage_system_deploy_new']", check=True).click()

        # 点击浏览
        self.find_element_by_xpath("//*[@id='ofs_install_browse_file']").click()

        # 选择路径
        for dirname in path_list:
            if dirname == path_list[-1]:
                for i in range(5):
                    self.find_element_by_xpath("//*[contains(text(),'%s')]" % dirname).click()
                    if self.driver.execute_script("return $('#ofs_file_explorer_selected_file_id').val()"):
                        break
                    if i == 4:
                        raise Exception("tar path is wrong")
                    time.sleep(1)
                break
            self.find_element_by_xpath("//*[contains(text(),'%s')]/../../span" % dirname).click()

        # 点击确定路径
        self.find_element_by_xpath("//*[@id='ofs_file_explorer_window-btn-0']").click()

        # 点击确定选择安装文件
        self.find_element_by_xpath("//*[@id='ofs_install_select_install_file_widow-btn-0']").click()

        # 等待解压完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 输入存储系统名称
        self.find_element_by_xpath("//*[@id='ofs_install_system_name_id']", js_send_keys=parastor_name)

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_install_system_desc_next_button']").click()

        # 点击添加机柜
        time.sleep(1)
        self.execute_script_click(xpath="//*[@id='ofs_install_rack_info_addRack']", check=True)

        # 勾选批量添加机柜、填写相关信息
        self.execute_script_click(xpath="//*[@id='ofs_install_batch_add_rack_checkbox_id']")
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_rack_name_prefix_id']", js_send_keys=cabinet_name)
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_rack_start_number_id']",
                                   js_send_keys=cabinet_start_num)
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_rack_end_number_id']", js_send_keys=cabinet_end_num)
        self.select_by_val(xpath="//*[@id='ofs_install_rack_info_rack_height_id']", val=cabinet_height)

        # 点击确定添加机柜
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_addRack_id-btn-0']").click()

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_install_rack_info_button_next']").click()

        # 循环添加节点
        log.info("start to add node")
        for control_ip in control_ip_list:
            # 点击添加节点
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_addNode']").click()

            # 输入管理ip
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_control_ip_id']", js_send_keys=control_ip)

            # 点击刷新，搜索节点信息
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_control_ip']//i").click()

            # 等待搜索完成
            self.check_element_done(time_out=self.timeout_max_default)

            # 点击搜索数据ip
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_data_ip']//i").click()

            # 勾选指定数据ip
            data_ip_list = data_ip_dict[control_ip]
            xpath = "//*[@id='ofs_install_nodes_info_ip_select_checkboxGroup_id']//input"
            self.implicit_wait(xpath=xpath)
            obj_list = self.driver.find_elements_by_xpath(xpath)
            for obj in obj_list:
                if obj.get_attribute("value") not in data_ip_list:
                    self.execute_script_click(dom=obj)

            # 点击确定选择数据ip
            self.execute_script_click(xpath="//*[@id='ofs_install_nodes_info_ip_select_id-btn-0']")

            # 点击搜索共享盘
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_share_disks']//i").click()

            # 勾选共享盘
            if vir_pyh == "vir":
                share_disk_path = "//*[contains(text(),'%s GB')]/../..//input" % get_config.get_web_disk_size()
                self.implicit_wait(share_disk_path)
                obj_disks_list = self.driver.find_elements_by_xpath(share_disk_path)
                for i in range(2):
                    self.execute_script_click(dom=obj_disks_list[i])
            else:
                share_disk_path = "//*[contains(text(),'SSD')]/../../div/label/input"
                self.implicit_wait(share_disk_path)
                obj_disks_list = self.driver.find_elements_by_xpath(share_disk_path)
                for obj_disks in obj_disks_list:
                    self.execute_script_click(dom=obj_disks)

            # 点击确定勾选共享盘
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_disk_select_id-btn-0']").click()

            # 点击搜索数据盘
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_data_disks']//i").click()
            if vir_pyh == "vir":
                # 勾选数据盘
                data_disk_path = "//*[contains(text(),'%s GB')]/../..//input" % get_config.get_web_disk_size()
                self.implicit_wait(data_disk_path)
                obj_data_disks_list = self.driver.find_elements_by_xpath(data_disk_path)
                for obj_data_disk in obj_data_disks_list:
                    self.execute_script_click(dom=obj_data_disk)

            else:
                # 勾选数据盘
                data_disk_path = "//*[contains(text(),'TB')]/../..//input"
                self.implicit_wait(data_disk_path)
                obj_data_disks_list = self.driver.find_elements_by_xpath(data_disk_path)
                for obj_data_disk in obj_data_disks_list:
                    self.execute_script_click(dom=obj_data_disk)

            # 点击确定勾选数据盘
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_disk_select_id-btn-0']").click()

            # 点击确定添加节点
            self.find_element_by_xpath("//*[@id='ofs_install_nodes_info_addNode_id-btn-0']").click()

            # 点击确定警告
            if vir_pyh == "vir":
                self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'warring')]").click()

                # 检查添加完成
                self.check_element_done(time_out=self.timeout_max_default)

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_install_node_info_button_next']").click()

        # 点击下一步
        self.find_element_by_xpath("//*[@id='ofs_install_parameter_info_button_next']").click()

        # 等待检查环境
        self.check_element_done(time_out=self.timeout_max_default)

        # 留一个检查环境的截图
        self.save_screenshot_now(name='check_environment')

        # 点击开始安装
        log.info("start to install")
        self.find_element_by_xpath("//*[@id='ofs_install_info_button_install']").click()

        # 等待安装完成
        self.check_element_done(time_out=3600)

        # 留一个部署完成的截图
        self.save_screenshot_now(name='install')

        # 点击确认安装成功
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()
        return

    @staticmethod
    def check_ping_util(node_ip, ping_flag=True):
        # 检查卸载完毕
        for i in range(1800):
            if ping_flag:
                if common.check_ping(node_ip):
                    log.info("ping %s success" % node_ip)
                    break

            if ping_flag is False:
                if common.check_ping(node_ip) is False:
                    log.info("shutdown %s success" % node_ip)
                    break

            time.sleep(1)
            log.info("wait ping %s %s s" % (node_ip, i))
            if i == 1799:
                log.info("node ip: ping %s error " % node_ip)
                raise Exception("ping timeout 30min")
        return

    @staticmethod
    def uninstall_system(mode="AUTO_REBOOT"):
        # 卸载系统
        log.info("uninstall system")
        '''
        # 点击断开
        self.find_element_by_xpath("//*[@id='ofs_select_storage_system_panel_id']//a", elements_num=1).click()

        # 点击确认断开
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查断开完成
        self.check_element_done(time_out=self.timeout_max_default)
        '''
        # 卸载系统
        cmd = "/home/parastor/tools/deployment/uninstall --mode=%s" % mode
        p1 = Process(target=common.pscli_run_command, args=(cmd,))

        # mode为重启类型
        if mode == "AUTO_REBOOT":
            p1.daemon = True
            p1.start()
            log.info("wait uninstall done")
            th_lst = []
            for node_ip in get_config.get_allparastor_ips():
                th = common.MyThread(target=System_Install.check_ping_util, args=(node_ip, False))
                th_lst.append(th)

            for th in th_lst:
                th.start()

            for th in th_lst:
                th.join()
                if th.exitcode != 0:
                    raise Exception("wait reboot failed")

            # 检查重启完毕
            log.info("shutdown success and wait reboot")
            th_lst = []
            for node_ip in get_config.get_allparastor_ips():
                th = common.MyThread(target=System_Install.check_ping_util, args=(node_ip, True))
                th_lst.append(th)

            for th in th_lst:
                th.start()

            for th in th_lst:
                th.join()
                if th.exitcode != 0:
                    raise Exception("wait reboot failed")

        # mode 为不重启类型
        else:
            p1.start()
            p1.join()
            if p1.exitcode != 0:
                raise Exception("uninstall cluster failed!!!!!!")
            log.info("uninstall success")

        time.sleep(10)
        return

    @staticmethod
    def uninstall_webui():
        """卸载webui"""
        parastor_ips = get_config.get_allparastor_ips()
        for ip in parastor_ips:
            webui_path = "/opt/gridview/webui/deployment/uninstall_local_webui.py"
            rc, stdout = common.run_command(ip, "ls %s" % webui_path)
            if rc == 0:
                rc1, stdout = common.run_command(ip, "python %s" % webui_path)
                common.judge_rc(rc1, 0, "uninstall webui")
        return

    @staticmethod
    def install_webui():
        """安装webui"""
        parastor_ip_one = get_config.get_parastor_ip()
        vir_ip = get_config.get_web_ip()
        webui_path = get_config.get_web_pkg_position()   # /home/deploy
        cmd = "ls %s | grep parastor_gui_installer | grep tar" % webui_path
        rc, webui_name_tar = common.run_command(parastor_ip_one, cmd)
        common.judge_rc(rc, 0, "no webui tar")

        cmd1 = "cd %s;tar -xf %s" % (webui_path, webui_name_tar.strip())
        virt_ip = get_config.get_web_ip()
        netcard_name = get_config.get_web_eth_name_ctrl()
        subnet_mask = get_config.get_web_network_mask()
        parameter = "--virt_ip=%s --netcard_name=%s --subnet_mask=%s" % (virt_ip, netcard_name, subnet_mask)
        cmd2 = "python %s/parastor_gui_installer/webui/deployment/install_local_webui.py %s" % (webui_path, parameter)
        rc1, stdout = common.run_command(parastor_ip_one, cmd1)
        common.judge_rc(rc1, 0, "tar -xf webui")
        rc2, stdout = common.run_command(parastor_ip_one, cmd2)
        common.judge_rc(rc2, 0, "install webui")

        # 检查ping
        for i in range(600):
            log.info("ping %s" % vir_ip)
            if common.check_ping(vir_ip):
                break
            if i == 599:
                raise Exception("check ping vir ip failed")
            time.sleep(1)
        time.sleep(60)
        return

    def modify_system_ip(self, cluster_name, node_name, ctrl_ip=None, data_ip_list=None):
        log.info("modify system ip")

        # 点击断开
        self.find_element_by_xpath("//*[@id='ofs_select_storage_system_panel_id']//a", elements_num=1).click()

        # 点击确认断开
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查断开完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 2、点击关闭后台系统
        self.find_element_by_xpath("//*[@id='ofs_select_storage_system_entire_shutdown']").click()

        # 输入一个节点的控制ip
        ctrl_ip_one = get_config.get_parastor_ip()
        self.find_element_by_xpath("//input[@id='ofs_entire_shutdown_node_ip_input']", js_send_keys=ctrl_ip_one)

        # 点击关闭系统
        self.find_element_by_xpath("//*[@id='ofs_entire_shutdown_cluster_window-btn-0']").click()

        # 点击确认关闭系统
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查关闭完成
        self.check_element_done(time_out=3600)

        # 点击确认完成信息（直接跳到修改系统ip）
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 3、修改系统ip，选中待修改的系统
        self.execute_script_click(xpath="//*[@title='%s']/../..//input" % cluster_name)

        # 点击确认选择
        self.find_element_by_xpath("//*[@id='ofs_choose_cluster_window-btn-0']").click()

        # 输入修改的控制ip
        if ctrl_ip:
            self.find_element_by_xpath(
                "//*[@title='%s']/../..//input" % node_name, elements_num=0, js_send_keys=ctrl_ip)

        # 点击刷新
        self.execute_script_click(xpath="//*[@title='%s']/../..//i" % node_name, elements_num=0)

        # 点击搜索数据ip
        self.execute_script_click("//*[@title='%s']/../..//i" % node_name, elements_num=1, check=True)

        # 勾选数据ip
        for data_ip in data_ip_list:
            self.execute_script_click(xpath="//*[starts-with(text(), '%s')]/../..//input" % data_ip)

        # 点击确定
        self.find_element_by_xpath("//*[@id='ofs_choose_data_ip_window-btn-0']").click()

        # 点击确认
        self.execute_script_click("//*[@id='ofs_config_ip_button_confirm']", check=True)

        # 勾选警告
        self.execute_script_click("//*[@id='riskCheckbox']")

        # 点击确定
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'riskComfirm')]").click()

        # 等待修改完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 留一个成功的截图
        self.save_screenshot_now("modify_data_ip")

        # 点击确定启动系统
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 检查启动完成
        self.check_element_done(time_out=self.timeout_max_default)

        # 点击确认启动成功
        self.find_element_by_xpath("//*[contains(@id, 'btn-0') and starts-with(@id, 'comfirm')]").click()

        # 该过程会重启webui
        time.sleep(120)
        while True:
            try:
                quit_web_driver(self.driver)
                self.driver = init_web_driver(auto_connect=False)
            except Exception:
                log.info("wait reboot webui")
                time.sleep(20)
                continue
            break

        # 点击新建连接
        self.find_element_by_xpath("//*[@id='ofs_select_storage_system_connect_exist']").click()

        # 输入新建连接ip
        system_one_ip = get_config.get_parastor_ip()
        self.find_element_by_xpath("//*[@id='ofs_connect_exists_system_string_id']", js_send_keys=system_one_ip)

        # 点击连接
        self.find_element_by_xpath("//*[@id='ofs_connect_exists_system_btn']").click()

        # 等待操作完成
        self.check_element_done(check_by_click=True)

        quit_web_driver(self.driver)

        return

class Home(First_Level_Label):
    """首页类，包含首页中的检查项"""

    def get_cluster_name(self):
        # 获取首页右上角系统名称和集群概览系统名称

        # 定位到首页
        self.locate_home()

        # 获取界面右上角名称
        cluster_name1 = self.find_element_by_xpath("//*[@id='ofs_current_connect_cluster_name']").text

        # 获取集群概览名称
        cluster_name2 = self.find_element_by_xpath("//*[@id='dashboard_cluster_name']").text

        return cluster_name1, cluster_name2

    def get_data_health_run_stat(self):
        # 获取首页上数据状态、健康状态、运行状态、节点个数

        # 定位到首页
        self.locate_home()

        # 获取首页上数据状态、健康状态、运行状态、节点总数
        time.sleep(3)
        data_stat = self.find_element_by_xpath("//*[@id='dashboard_cluster_data']").text
        health_stat = self.find_element_by_xpath("//*[@id='dashboard_cluster_healthy']").text
        run_stat = self.find_element_by_xpath("//*[@id='dashboard_cluster_running']").text
        node_total = int(self.find_element_by_xpath("//*[@id='dashboard_cluster_nodes']").text)

        return data_stat, health_stat, run_stat, node_total

    def get_node_pool_storage_volume_total(self):
        # 获取首页上节点池数、存储池数、卷数

        # 定位到首页
        self.locate_home()

        # 获取首页上节点池数、存储池数、卷数
        time.sleep(3)
        node_pool_total = self.find_element_by_xpath("//*[@id='dashboard_resources_nodepool_num_value']").text
        storage_total = self.find_element_by_xpath("//*[@id='dashboard_resources_storagepool_num_value']").text
        volume_total = self.find_element_by_xpath("//*[@id='dashboard_resources_volume_num_value']").text

        return int(node_pool_total), int(storage_total), int(volume_total)

    def check_cluster_performance_normal(self):
        # 定位到首页
        self.locate_home()

        # 检查带宽是否正常
        select_list = ["BANDWIDTH", "IOPS", "CPU", "MEMORY", "DELAY"]
        for select in select_list:
            self.select_by_val("//*[@id='ofs_dashboard_cluster_performancecombo']", select)

            time.sleep(2)
            obj_list = self.driver.find_elements_by_xpath("//*[@id='emptyData']")
            if obj_list:
                log.info("check %s is empty" % select)
                self.save_screenshot_now()
                raise Exception("check cluster performance failed")

        return
