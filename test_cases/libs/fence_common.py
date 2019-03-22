#!/usr/bin/python
# -*- encoding=utf8 -*-
import common
import log
import os
import re
import subprocess
import threading
import time
import signal
import make_fault
import utils_path
import random



""
#readme:
#unistor的配置文件中的ip要改
""
class Fence():
    def __init__(self):
        pass
    def command(self, cmd, node_ip=None, timeout=None):
        """
        执行shell命令
        """
        if node_ip:
            cmd1 = 'ssh %s "%s"' % (node_ip, cmd)
        else:
            cmd1 = cmd

        if timeout is None:
            process = subprocess.Popen(
                cmd1,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT)
            output, unused_err = process.communicate()
            retcode = process.poll()
            return retcode, output
        else:
            result = [None, 0, "", "Timeout"]

            def target(result):
                p = subprocess.Popen(
                    cmd1,
                    shell=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    preexec_fn=os.setsid)
                result[0] = p
                (result[2], result[3]) = p.communicate()
                result[1] = p.returncode

            thread = threading.Thread(target=target, kwargs={'result': result})
            thread.start()
            thread.join(timeout)
            if thread.is_alive():
                # Timeout
                p = result[0]
                wait_time = 5
                while p is None:
                    time.sleep(1)
                    p = result[0]
                    wait_time -= wait_time
                    if wait_time == 0:
                        print 'Create process for cmd %s failed.' % cmd
                        exit(1)
                os.killpg(os.getpgid(p.pid), signal.SIGTERM)
                print 'Process %d is killed.' % p.pid
                thread.join()
            return result[1], result[2]

    def check_err_msg(self, stdout):
        """
        :author:      liuyzhb
        :date:        2019.03.12
        :description: 判断detail_err_msg中的信息是否为空
        :return:
        """
        stdout = common.json_loads(stdout)
        log.info('stdout is %s' %stdout)
        detail_err_msg = stdout['detail_err_msg']
        log.info('detail_err_msg is %s' % detail_err_msg)
        if detail_err_msg == "":
            return 0,None
        else:
            return -1,stdout

    def get_fence_current(self):
        value = common.get_param_current("MGR", "fence_enable")
        return value


    def fence_enable(self):
        """
        :author:      liuyzhb
        :date:        2019.03.12
        :description: 进行fence开关开启,仅开启
        :return:
        """
        rc,stdout = common.update_param("MGR", "fence_enable",1)
        rc, detail_err_msg = self.check_err_msg(stdout)
        return rc, detail_err_msg

    def fence_disable(self):
        """
       :author:      liuyzhb
       :date:        2019.03.12
       :description: 进行fence开关关闭,仅关闭
       :return:
       """
        rc, stdout = common.update_param("MGR", "fence_enable", 0)
        rc, detail_err_msg = self.check_err_msg(stdout)
        return rc, detail_err_msg
    def add_fence_service(self,sender_type = "oRole", node_id = 1, service_type = "oPara", force = "true", **kwargs):
        """
        :author:      liuyzhb
        :date:        2019.03.12
        :description: 主动执行fence命令
        :param sender_type:发起fence操作的进程
        :param service_type:被fence的进程
        :param node_id:被fence的进程所在的节点id
        :param force:是否强制fence，true为强制，false为非强制
        :return:
        """
        rc,stdout = common.add_fence_service(sender_type, node_id , service_type, force)
        rc, detail_err_msg = self.check_err_msg(stdout)
        return  rc, detail_err_msg

    def get_master_of_ojmgs(self):
        """
        :author:      liuyzhb
        :date:        2019.03.13
        :description: 获取ojmgs主节点
        :return:如果获取成功，返回rc和node_id,如果获取失败，则返回rc和None
        """
        rc, stdout = common.get_master()
        rc, detail_err_msg = self.check_err_msg(stdout)
        stdout = common.json_loads(stdout)
        common.judge_rc(rc, 0, "get_master_of_ojmgsfailed!!!!! \nstdout: %s" % detail_err_msg, exit_flag=False)
        if rc == 0:
            node_id = stdout['result']['node_id']
            log.info('node_id of master ojmgs is %s' % str(node_id))
            return  rc,node_id
        else:
            return -1, None


    def get_master_of_zk(self):
        """
        :author:      liuyzhb
        :date:        2019.03.13
        :description: 获取zk主节点
        :return:如果获取成功，返回0和node_id,如果获取失败，则返回-1和None
        """
        # 获取所有点的node_id
        node = common.Node()
        nodeips= node.get_nodes_ip()
        for i in range(3):
            for i in range(len(nodeips)):
                ip = nodeips[i]
                rc,mode = common.get_zk_status(ip)
                log.info('ip:%s,mode:%s' %(ip,mode))
                if rc == 0 and mode != None and mode.find("leader")>=0:
                    node = common.Node()
                    master_id = node.get_node_id_by_ip(ip)
                    log.info('node_id of master zk is %s' % str(master_id))
                    return 0,master_id
                else:
                    pass
            time.sleep(10)
        log.error('find all node for 10 times,but donnot find zk master')
        return -1, None

    def if_master_unified(self):
         """
         :author:      liuyzhb
         :date:        2019.03.14
         :description: 判断oJmgs、oRole、zk的主是否相同
         :return:     如果相同则返回0 。否则返回-1
         """
         # 获取所有点的node_id
         rc1, node_id_ojmgs = self.get_master_of_ojmgs()
         common.judge_rc(rc1, 0, "get_master_of_ojmgs failed!!!\n", exit_flag=False)
         rc2, node_id_orole = common.get_orole_master()
         common.judge_rc(rc2, 0, "get_orole_master status failed!!!\n", exit_flag=False)
         rc3, node_id_zk = self.get_master_of_zk()
         common.judge_rc(rc3, 0, "get_master_of_zk status failed!!!\n", exit_flag=False)
         log.info ('node_id of master ojmgs is %s' %str(node_id_ojmgs))
         log.info('node_id of master orole is %s' % str(node_id_orole))
         log.info('node_id of master zk is %s' % str(node_id_zk))
         if str(node_id_ojmgs) == str(node_id_orole) == str(node_id_zk):
             log.info('master of oJmgs\oRole\zk is unified')
             return 0
         else:
             return -1

    def get_process_status(self, node_ip, process):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 判断某个节点指定进程的状态
        :return:     查询到的进程状态：如Ssl、D、Z等状态
        """
        cmd = "ps aux | grep %s | grep -v grep" % process
        rc, stdout = common.run_command(node_ip, cmd)
        pro_stat = re.split(r' +', stdout)[7]
        return pro_stat

    def get_process_state(self, node_id, process):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 判断某个parastor节点指定服务的状态
        :return:     查询到的parastor节点服务的状态：如SERV_STATE_OK、SERV_STATE_READY等
        """
        rc, stdout = common.get_services(node_id)
        if rc != 0:
            return False
        services_info = common.json_loads(stdout)
        service_lst = services_info['result']['nodes']
        service_node = service_lst[0]
        service_node_lst = service_node['services']
        for service in service_node_lst:
            if service['service_type'] == process:
                log.info(
                    "node %s: %s's status is %s" %
                    (service['node_id'],
                     service['service_type'],
                        service['inTimeStatus']))
                return (
                    service['node_id'],
                    service['service_type'],
                    service['inTimeStatus'])
        log.info("node %s: process %s is not exit" %
                 (service_node_lst[0]['node_id'], process))
        return (service_node_lst[0]['node_id'], process, "None")

    def kill_process(self, node_ip, process):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: kill指定节点的指定进程
        :return:     无返回值
        """
        pidof_pro = [
            'oStor',
            'oPara',
            'oRole',
            'oMgcd',
            'oJob',
            'oOss',
            'oOms',
            'oCnas']
        flag = False
        for pro in pidof_pro:
            if pro in process:
                flag = True
                break
        if flag:
            ps_cmd = "pidof %s" % process
            rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
            if "" == stdout:
                return
            kill_cmd = ("kill -9 %s" % stdout)
            rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
            if rc != 0:
                log.error(
                    "node: %s, cmd: %s (process:%s) failed. \nstdout: %s \n" %
                    (node_ip, kill_cmd, process, stdout))
            else:
                log.info(
                    "node: %s, cmd: %s (process:%s) successed. \nstdout: %s \n" %
                    (node_ip, kill_cmd, process, stdout))
        else:
            ps_cmd = ("ps -ef|grep %s | grep -v grep" % process)
            rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
            if "" == stdout:
                return
            lines = stdout.split('\n')
            for line in lines:
                if line:
                    vars = line.split()
                    pid = vars[1]
                    kill_cmd = ("kill -9 %s" % pid)
                    rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
                    if rc != 0:
                        log.error(
                            "Execute command: \"%s\" failed. \nstdout: %s \n" %
                            (kill_cmd, stdout))
                    else:
                        log.info(
                            "Execute command: \"%s\" successed. \nstdout: %s \n" %
                            (kill_cmd, stdout))
        return

    # def kill_process_in_loop(self, interval, kill_times, node_ip, process):
    #     """
    #     :author:      zhanghan
    #     :date:        2019.03.14
    #     :parameters: interval：循环kill进程的时间间隔，int类型
    #                  kill_times：循环kill进程的次数，int类型
    #                  node_ip：节点ip
    #                  process：待kill的进程
    #     :description: kill指定节点的指定进程，循环多次执行
    #     :return:     无返回值
    #     """
    #     for times in range(kill_times):
    #         time.sleep(interval)
    #         self.kill_process(node_ip, process)
    #
    #     return
    #
    # def kill_process_and_rename(self, node_ip, process, rename_hold_time):
    #     """
    #     :author:      zhanghan
    #     :date:        2019.03.14
    #     :parameters：rename_hold_time：修改进程名称的维持时间，int类型
    #     :description: kill指定节点的指定进程，进程被kill前先将其名称rename，防止被自动拉起，超过指定时间后再将其名称恢复，恢复后进程可以被正常拉起
    #     :return:     0(执行成功)/-3(进程名称指定错误，不进行操作)/-2(进程不存在，不进行操作)/-1(重命名进程失败)
    #     """
    #     log.info("start fault")
    #     pidof_pro1 = ['oStor', 'oPara', 'oRole', 'oMgcd', 'oJob', 'oCnas']
    #     pidof_pro2 = ['oOss', 'oOms']
    #     pidof_pro = pidof_pro1 + pidof_pro2
    #     flag = False
    #     for pro in pidof_pro:
    #         if pro in process:
    #             flag = True
    #             break
    #     if flag:
    #         ps_cmd = "pidof %s" % process
    #         rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
    #         if "" == stdout:
    #             return -2
    #         for num in range(3):
    #             if process not in pidof_pro2:
    #                 cmd_rename = "mv /home/parastor/bin/%s /home/parastor/bin/%s_bak" % (
    #                     process, process)
    #             else:
    #                 if "oOms" == process:
    #                     cmd_rename = "mv /home/parastor/oms/%s /home/parastor/oms/%s_bak" % (
    #                         process, process)
    #                 else:
    #                     cmd_rename = "mv /home/parastor/oss/%s /home/parastor/oss/%s_bak" % (
    #                         process, process)
    #             rc, output = self.command(cmd_rename, node_ip, timeout=60)
    #             if 0 == rc:
    #                 break
    #             else:
    #                 time.sleep(1)
    #         else:
    #             log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % ("kill_process_and_rename", process))
    #             return -1
    #         kill_cmd = ("kill -9 %s" % stdout)
    #         rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
    #         if rc != 0:
    #             log.error(
    #                 "node: %s, cmd: %s (process:%s) failed. \nstdout: %s \n" %
    #                 (node_ip, kill_cmd, process, stdout))
    #         else:
    #             log.info(
    #                 "node: %s, cmd: %s (process:%s) successed. \nstdout: %s \n" %
    #                 (node_ip, kill_cmd, process, stdout))
    #         time.sleep(rename_hold_time)
    #         for num in range(3):
    #             if process not in pidof_pro2:
    #                 cmd_rename_bak = "mv /home/parastor/bin/%s_bak /home/parastor/bin/%s" % (
    #                     process, process)
    #             else:
    #                 if "oOms" == process:
    #                     cmd_rename_bak = "mv /home/parastor/oms/%s_bak /home/parastor/oms/%s" % (
    #                         process, process)
    #                 else:
    #                     cmd_rename_bak = "mv /home/parastor/oss/%s_bak /home/parastor/oss/%s" % (
    #                         process, process)
    #             rc, output = self.command(cmd_rename_bak, node_ip, timeout=60)
    #             if 0 == rc:
    #                 break
    #             else:
    #                 time.sleep(1)
    #         else:
    #             log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
    #             "kill_process_and_rename", process + '_bak'))
    #             return -1
    #     else:
    #         ps_cmd = ("ps -ef|grep %s | grep -v grep" % process)
    #         rc, stdout = self.command(ps_cmd, node_ip, timeout=60)
    #         if "" == stdout:
    #             return -2
    #         for num in range(3):
    #             if ("oJmw" == process) or ("oJmgs" == process):
    #                 cmd_rename = "mv /home/parastor/bin/%s /home/parastor/bin/%s_bak" % (
    #                     process, process)
    #             elif "ctdb" == process:
    #                 cmd_rename = "mv /home/parastor/cnas/smb/bin/%s /home/parastor/cnas/smb/bin/%s_bak" % (
    #                     process, process)
    #             elif "zk" == process:
    #                 cmd_rename = "mv /home/parastor/tools/deployment/zk_crond.py /home/parastor/tools/deployment/zk_crond_bak.py"
    #             else:
    #                 log.error(
    #                     "Process %s is not right, please check process name!!!" %
    #                     process)
    #                 return -3
    #             rc, output = self.command(cmd_rename, node_ip, timeout=60)
    #             if 0 == rc:
    #                 break
    #             else:
    #                 time.sleep(1)
    #         else:
    #             log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
    #                 "kill_process_and_rename", process))
    #             return -1
    #         lines = stdout.split('\n')
    #         for line in lines:
    #             if line:
    #                 vars = line.split()
    #                 pid = vars[1]
    #                 kill_cmd = ("kill -9 %s" % pid)
    #                 rc, stdout = self.command(kill_cmd, node_ip, timeout=60)
    #                 if rc != 0:
    #                     log.error(
    #                         "Execute command: \"%s\" failed. \nstdout: %s \n" %
    #                         (kill_cmd, stdout))
    #                 else:
    #                     log.info(
    #                         "Execute command: \"%s\" successed. \nstdout: %s \n" %
    #                         (kill_cmd, stdout))
    #         time.sleep(rename_hold_time)
    #         for num in range(3):
    #             if ("oJmw" == process) or ("oJmgs" == process):
    #                 cmd_rename_bak = "mv /home/parastor/bin/%s_bak /home/parastor/bin/%s" % (
    #                     process, process)
    #             elif "ctdb" == process:
    #                 cmd_rename_bak = "mv /home/parastor/cnas/smb/bin/%s_bak /home/parastor/cnas/smb/bin/%s" % (
    #                     process, process)
    #             elif "zk" == process:
    #                 cmd_rename_bak = "mv /home/parastor/tools/deployment/zk_crond_bak.py /home/parastor/tools/deployment/zk_crond.py"
    #             else:
    #                 log.error(
    #                     "Process %s is not right, please check process name!!!" %
    #                     process)
    #                 return -3
    #             rc, output = self.command(cmd_rename_bak, node_ip, timeout=60)
    #             if 0 == rc:
    #                 break
    #             else:
    #                 time.sleep(1)
    #         else:
    #             log.info("Function:%s, operation rename process:%s excuted 3 times, all failed!" % (
    #                 "kill_process_and_rename", process + '_bak'))
    #             return -1
    #     return 0

    def fault_in_master_node(
            self,
            node_ip,
            fault_script_path,
            fault_operation,
            zk_num,
            mgr_ip,
            fault_node,
            kill_process=None,
            fault_num=1):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 调用ReliableTest_x.x.py故障脚本执行故障
        :parameters: node_ip：本节点(StorTest)节点的ip
                     fault_script_path：ReliableTest_x.x.py故障脚本的位置
                     fault_operation：故障类型，取值范围：0-10，int类型
                     zk_num：集群zk节点的数量，int类型
                     mgr_ip：管理节点ip
                     fault_node：做故障的集群节点ip
                     kill_process：待kill的进程名称，默认值为None，表示不做进程故障
                     fault_num：故障的次数，默认值为1，int类型
        :return:     一对元组(故障执行的返回值, 输出的内容)
        """
        if None == kill_process:
            cmd_fault = "python %s -o %d -z %d -n %d  -i %s -b %s" % (
                fault_script_path, fault_operation, zk_num, fault_num, mgr_ip, fault_node)
        else:
            if '4' == str(fault_operation):
                cmd_fault = "python %s -o %s -p %s -z %d -n %s  -i %s -b %s" % (fault_script_path, str(
                    fault_operation), kill_process, zk_num, str(fault_num), mgr_ip, fault_node)
            else:
                log.info(
                    "The fault operation is (-o %s), not (-o 4)'kill process', please check!" %
                    str(fault_operation))
                return
        rc, output = common.run_command(node_ip, cmd_fault)
        return rc, output

    def get_fence_events(
            self,
            category="FENCE_EVENT",
            event_code="0x03050001"):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 获取fence事件的输出结果
        :return:     一对元组(获取fence事件结果的返回值, 获取到的fence事件输出信息(pscli执行输出信息))
        """
        rc, stdout = common.get_events(category, event_code=event_code)
        if 0 != rc:
            log.error("Function: \"%s\" failed. \nstdout: %s \n" %
                      ("get_fence_events", stdout))

        return rc, stdout

    def get_all_fence_events_list(
            self,
            category="FENCE_EVENT",
            event_code="0x03050001"):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 获取fence事件的输出结果，以列表的形式返回
        :return:     一对元组(获取fence事件结果的返回值(0表示成功，-1表示失败), 获取到的fence事件输出信息(列表的形式，空列表表示失败))
        """
        rc, stdout = self.get_fence_events(
            category="FENCE_EVENT", event_code="0x03050001")
        fence_events_list = list()
        if 0 != rc:
            log.error("Function: \"%s\" failed. \nstdout: %s \n" %
                      ("get_fence_events", stdout))
            return -1, []
        else:
            msg_info = common.json_loads(stdout)
            msg_list = msg_info["result"]["events"]
            for msg_list_num in range(len(msg_list)):
                fence_events_dict = dict()
                fence_events_param_dict = dict()
                for key in msg_list[msg_list_num]:
                    if "<type 'unicode'>" == str(
                            type(msg_list[msg_list_num][key])):
                        fence_events_dict[key.encode(
                            "utf-8")] = (msg_list[msg_list_num][key]).encode("utf-8")
                    else:
                        fence_events_dict[key.encode(
                            "utf-8")] = msg_list[msg_list_num][key]
                    if "params" == key.encode("utf-8"):
                        sub_msg = msg_list[msg_list_num]["params"]
                        for num in range(len(sub_msg)):
                            fence_events_param_dict[sub_msg[num]["name"].encode(
                                "utf-8")] = sub_msg[num]["value"].encode("utf-8")
                fence_events_dict["params"] = fence_events_param_dict
                fence_events_list.append(fence_events_dict)

        return 0, fence_events_list

    def check_fence_event(
            self,
            make_fence_time_stamp,
            fence_node_id=None,
            fence_process=None):
        """
        :author:      zhanghan
        :date:        2019.03.14
        :description: 查询fence事件
        :parameters: make_fence_time_stamp：触发fence的故障时间，时间戳格式，如"1552616897"，str类型
                     fence_node_id：fence的节点id，默认值为None，表示不进行检查，可以指定该参数，指定后，则检查，str类型
                     fence_process：fence的进程名称，默认值为None，表示不进行检查，可以指定该参数，指定后，则检查，str类型
        :return:     0(查询fence成功，fence成功)/-1(查询fence成功，fence失败)/-2(查询fence失败)/-3(参数传递有误)/1(获取fence事件失败)
        """
        rc, fence_events_list = self.get_all_fence_events_list(
            category="FENCE_EVENT", event_code="0x03050001")
        if 0 != rc:
            log.info("Function: \"%s\" failed. \nstdout: %s \n" %
                     ("get_all_fence_events_list", fence_events_list))
            return_value = 1
        else:
            if None != (fence_node_id and fence_process):
                for fence_event in fence_events_list:
                    if (int(make_fence_time_stamp) <= int(
                            fence_event["startTimeShort"])):
                        if (fence_node_id == fence_event["params"]["node-id"]) and (
                                fence_process == fence_event["params"]["service-type"]):
                            if 0 == len(fence_event["details"]):
                                log.info(
                                    "Function: \"%s\", Node_id:%s, fence_process:%s, fence success!" %
                                    ("check_fence_event", fence_node_id, fence_process))
                                return_value = 0
                                break
                            else:
                                log.error(
                                    "Function: \"%s\", Node_id:%s, fence_process:%s, fence failed, the error info is %s" %
                                    ("check_fence_event", fence_node_id, fence_process, fence_event["details"]))
                                return_value = -1
                                break
                else:
                    log.error(
                        "Function: \"%s\", Node_id:%s, fence_process:%s, fence failed, can not find fence event!" %
                        ("check_fence_event", fence_node_id, fence_process))
                    return_value = -2
            elif (None == fence_node_id) and (None == fence_process):
                for fence_event in fence_events_list:
                    if (int(make_fence_time_stamp) <= int(
                            fence_event["startTimeShort"])):
                        if 0 == len(fence_event["details"]):
                            log.info(
                                "Function: \"%s\", fence success!" %
                                ("check_fence_event"))
                            return_value = 0
                            break
                        else:
                            log.error(
                                "Function: \"%s\", fence failed, the error info is %s" %
                                ("check_fence_event", fence_event["details"]))
                            return_value = -1
                            break
                else:
                    log.error(
                        "Function: \"%s\", fence failed, can not find fence event!" %
                        ("check_fence_event"))
                    return_value = -2
            else:
                log.info(
                    "Function: \"%s\", parameters error! 'fence_node_id':%s 'fence_process':%s. Both of 'fence_node_id' and 'fence_process' should be all None or not None" %
                    ("check_fence_event", fence_node_id, fence_process))
                return_value = -3

        return return_value
		
		
    def fence_prepare(self):
        """
        :author:      liuyzhb
        :date:        2019.03.15
        :description: fence 操作之前先准备环境。如果环境中fence没有开，则先开fence
        :return:如果获取成功，返回0和node_id,如果获取失败，则返回-1和None
        """
        value = common.get_param_current("MGR", "fence_enable")
        if value == 0:
            rc, stdout = self.fence_enable()
            common.judge_rc(rc, 0, "enable_fence failed!!! \nstdout: %s \nprepare failed !!!!!" % stdout)
        else:
            log.info('fence_prepare finish success!!!')

    def part_net_down(self, node_id, num_of_eth, num_of_fault,time_of_repair):
        """
        :author:      liuyzhb
        :date:        2019.03.16
        :description: 給指定的一个节点执行断一个数据网，执行num次
        :return:
        """
        # 根据node_id获取node_ip
        node = common.Node()
        node_ip = node.get_node_ip_by_id(node_id)
        # 获取节点的数据网对应网口的网卡和mask的list
        node = common.Node()
        eth_name_list, data_ip_list, mask_list = node.get_node_eth(node_id)
        log.info('eth_list of node_id %s is %s' % (str(node_id), eth_name_list))
        log.info('data_ip_list of node_id %s is %s' % (str(node_id), data_ip_list))
        log.info('mask_list of node_id %s is %s' % (str(node_id), mask_list))
        randomdigit = random.sample(range(len(eth_name_list)), num_of_eth )
        log.info('randomdigit is %s' %randomdigit)
        for i in randomdigit:
            # 获取随机网卡名
            choose_eth = eth_name_list[i]
            choose_mask = mask_list[i]
            log.info('choose_eth is %s' % choose_eth)
            log.info('choose_mask is %s' % choose_mask)
            # 给选出来的网卡执行断网
            rc = make_fault.down_eth(node_ip, choose_eth)
            if rc != 0:
                return -1
            log.info('down net %s in num %d finish' %(choose_eth, i))

        time.sleep(time_of_repair)
        for i in randomdigit:
            # 获取随机网卡名
            choose_eth = eth_name_list[i]
            choose_mask = mask_list[i]
            rc = make_fault.up_eth(node_ip, choose_eth, choose_mask)
            if rc != 0:
                return -1
            log.info('down net %s in num %d finish' % (choose_eth, i))


    def get_fault_type_and_time(self,fautrun_log):
        """
        :author:      liuping
        :date:        2019.03.21
        :description: 获取执行故障的节点、类型和时间
        :return: 返回元组，元组的每一个元素都是列表，元素的第一个元素为故障的节点列表，第二个元素为故障时间列表，
        第三个元素为故障类型列表
        """
        lines = []
        with open(fautrun_log, 'r') as f:
            lines1 = f.readlines()
            for line in lines1[:-1]:
                lines.append(line.replace('\n', ''))
        fault_time_lst = []
        fault_nodeip_lst =[]
        fault_type_lst = []
        obj_node = common.Node()
        node_ip_lst = obj_node.get_nodes_ip()
        for line in lines:
            if '************************************************************' in line:
                index1 = lines.index(line)
        for line in lines[index1+1:]:
            for node_ip in node_ip_lst:
                if ('INFO' in line) and (node_ip in line) and ('node' in line) :
                    #去掉宕机日志中，ping所在的行
                    if 'ping' not in line:
                        fault_time = line.split('[')[2].split(']')[0]
                        fault_time = '20'+ fault_time
                        fault_nodeip = node_ip
                        fault_type = line[(line.index(node_ip)+len(node_ip)):].replace(',','').lstrip()
                        fault_time_lst.append(fault_time)
                        fault_nodeip_lst.append(fault_nodeip)
                        fault_type_lst.append(fault_type)
        #对于拔数据盘和共享盘而言，只记录pullout disk的时间,断网只记录down的操作
        for i in range(len(fault_type_lst)-1,-1,-1):
            if 'insert disk' in fault_type_lst[i] or 'delete' in fault_type_lst[i] or 'add' in fault_type_lst[i]:
                fault_type_lst.pop(i)
                fault_time_lst.pop(i)
                fault_nodeip_lst.pop(i)
        for i in range(len(fault_type_lst) - 1, -1, -1):
            if 'ifconfig' in fault_type_lst[i] and 'up' in fault_type_lst[i]:
                fault_type_lst.pop(i)
                fault_time_lst.pop(i)
                fault_nodeip_lst.pop(i)
        return fault_nodeip_lst,fault_time_lst,fault_type_lst




if __name__ == "__main__":
    log_file_path = log.get_log_path("Fence_function_debug")
    log.init(log_file_path, True)
    fence = Fence()

    a = fence.get_fault_type_and_time('/home/FaultRun_0.2/2019-03-20-14-10-50_faultrun.log')
    print a[0]
    print a[1]
    print a[2]