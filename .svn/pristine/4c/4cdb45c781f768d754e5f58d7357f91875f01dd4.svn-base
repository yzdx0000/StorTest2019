#!/usr/bin/python
# -*- encoding=utf8 -*-

import os
import subprocess
import signal
import threading
import time


def system(my_cmd):
    """The sdtout and stderr will be the default."""

    rc, stdout, stderr = sh(my_cmd)
    return rc


def sh(cmd, raise_exception=False, timeout=None):
    """Execute a shell command, return the result.
    he stdout and stderr are collected and can be read later.
    Run the cmd and return the (returncode, stdout, stderr).
    raise_exception: if raise_exception is True, if the returncode is not 0,
                     an exception that contains the stdout and the stderr 
                     information will be raised.
    Args:
        cmd: A shell command that you want to run. For example 'ls'.
        raise_exception: If raise_exception is True, this function will raise
            an exception if the exit code of the shell command is not 0.
        timeout: If the timeout is not None, and the the shell command can not 
            be finished during the timeout, the child shell process will be 
            terminated.
    Returns:
        A tuple with 3 elements will be returned. The tuple contains:
        (exit code of the command, the standard output of the command, 
        the stdandard error ouput of the comamd).
    """

    if timeout is None:
        p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE)
        stdoutdata, stderrdata = p.communicate()
        if raise_exception and p.returncode != 0:
            raise Exception("Execute cmd:%s failed.\nstdout:%s\nstderr:%s" %
                            (cmd, stdoutdata, stderrdata))
        return p.returncode, stdoutdata, stderrdata
    else:
        result = [None, 0, "", "Timeout"]

        def target(result):
            p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE,
                                 stderr=subprocess.PIPE, preexec_fn=os.setsid)
            result[0] = p
            (result[2], result[3]) = p.communicate()
            result[1] = p.returncode
            if raise_exception and p.returncode != 0:
                raise Exception("Execute cmd:%s failed.\nstdout:%s\nstderr:%s" %
                                (cmd, result[2], result[3]))

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
            if raise_exception:
                raise Exception("Execute cmd:%s failed, timeout:%d." % (
                    cmd, timeout))
        return result[1], result[2], result[3]


def ssh(host, cmd, timeout=None):
    """Execute a command over ssh. 
    Returns
        The (result code, stdout, stderr).
    """

    cmd_separator = "'"
    if '"' in cmd and "'" in cmd:
        print """cmd:%s can not contain both " and '. """
    if "'" in cmd:
        cmd_separator = '"'

    ssh_cmd = "ssh -o ConnectTimeout=15 -o StrictHostKeyChecking=no -o \
           TcpKeepAlive=yes -o ServerAliveInterval=30 -o ServerAliveCountMax=3\
            -o BatchMode=yes %s %s%s%s" % (host, cmd_separator, cmd,
                                           cmd_separator)
    return sh(ssh_cmd, timeout=timeout)


def ssh2(host_ips, cmd):
    """Execute a command over ssh on a host.

    Args:
        cmd: The shell command to be executed on hosts.
        host_ips: A list of IPs of the destination host.
            
    Returns:
        A tuple of (result_code, stdout, stderr).      
        If all IPs in host_ips are unavailable, then the result of cmd on last 
        host is returned. 
    """
    for ip in host_ips:
        index = ip.find('@')

        print "index" + str(index)
        if index != -1:
            ip = ip[index+1:]
        print "ip" + ip

    available_ips = [ip for ip in host_ips if ping(ip[ip.find('@')+1:] if ip.find('@') != -1 else ip)]
    if len(available_ips) == 0:
        return ssh(host_ips[-1], cmd)
    else:
        return ssh(available_ips[0], cmd)


def scp(file_or_dir, dest_host, dest_path):
    """Copy a file or directory to remote host through scp command."""

    if not os.path.exists(file_or_dir):
        print '%s does not exist.' % file_or_dir
        return 1
    if os.path.isfile(file_or_dir):
        my_cmd = 'scp %s %s:%s' % (file_or_dir, dest_host, dest_path)
    elif os.path.isdir(file_or_dir):
        my_cmd = 'scp -r %s %s:%s' % (file_or_dir, dest_host, dest_path)

    return system(my_cmd)


def scp2(file_or_dir, dest_host_ips, dest_path):
    """Another version of scp, the destination can have more than one 
    IP, and this function will copy the file or directory to the 
    destination throuth any of the avaliable ip.

    Args:
        file_or_dir: A file for dir path.
        dest_host_ips: The IPs of the destination host.
        dest_path: The path on the destination host that the file 
                   should be copied.

    Returns:
        0 if succeed, otherwise a non-zero value is returned.
    """

    available_ips = [ip for ip in dest_host_ips if ping(ip)]
    if len(available_ips) == 0:
        return 1
    else:
        return scp(file_or_dir, available_ips[0], dest_path)


def scp3(file_or_dir, dest_hosts, dest_path):
    """Another version of scp, the dest_hosts should a list of IPs,
    and this function will copy the file or directory to all of the 
    destinations. 

    Args:
        file_or_dir: A file for dir path.
        dest_hosts: A list of IPs, each IP represents a host.
        dest_path: The path on the destination host that the file 
                   should be copied.

    Returns:
        0 if succeed, otherwise a non-zero value is returned.
    """

    if not os.path.exists(file_or_dir):
        print '%s does not exist.' % file_or_dir
        return 1
    if os.path.isfile(file_or_dir):
        my_cmd = 'scp %s ' % file_or_dir
    elif os.path.isdir(file_or_dir):
        my_cmd = 'scp -r %s ' % file_or_dir

    dest_str = " ".join(["%s:%s" % (d, dest_path) for d in dest_hosts])
    my_cmd += dest_str

    return system(my_cmd)


def execute_file(host, file, dest_dir='/tmp'):
    """Execute a file on remote node. 
    
    Returns:
        The (result code, stdout, stderr).
    """

    rc = scp(host, file, dest_dir)
    if rc:
        print 'Scp file:%s to host:%s failed.' % (file, host)
        return (rc, "", "")

    filename = os.path.basename(file)
    my_cmd = '%s/%s' % (dest_dir, filename)
    (rc, stdout, stderr) = ssh(host, my_cmd)

    # Delete the file on remote node.
    my_cmd = 'rm -rf %s/%s' % (dest_dir, filename)
    ssh(host, my_cmd)

    return (rc, stdout, stderr)


def gen_ping_cmd(ip):
    """Generate a ping command, which can be used to check whether the 
    ip can be reached.
    """

    return "ping -i 0.2 -w 2 -W 2 -c 5 -q %s" % ip


def ping(ip):
    """If the ip can be successfully reached by ping command, return 
    True, otherwise return False.
    """

    cmd = gen_ping_cmd(ip)
    rc = system(cmd)
    if rc == 0:
        return True
    else:
        return False
