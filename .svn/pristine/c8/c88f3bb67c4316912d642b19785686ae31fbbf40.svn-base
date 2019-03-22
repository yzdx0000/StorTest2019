#!/usr/bin/python
# -*- encoding=utf8 -*-

'''

'''
import os,time,re
import log
import datetime
import random
import get_config
import commands

# 获取当前路径
cur_dir = os.path.dirname(os.path.realpath(__file__))
logfile = cur_dir+'/logfile'
log.init(logfile, True)     # 初始化日志文件

# 测试用的进程数
#big_file_write_threads = get_config.big_file_write_threads_val  # 测试大文件进程数
#lit_file_write_threads = get_config.lit_file_write_threads_val  # 测试小文件进程数
rm_file_threads = get_config.rm_file_threads_val          # 删除操作进程数
# 测试用的文件数量
b_file_nums = get_config.b_file_nums_val            # 大文件数量
l_file_nums = get_config.l_file_nums_val          # 小文件数量
#b_file_size = get_config.b_file_size_val         # 每个大文件大小，单位：M或G
#l_file_size = get_config.l_file_size_val           # 每个小文件大小，单位：M或K
b_iorate = get_config.b_iorate_val                # 大文件码率
l_iorate = get_config.l_iorate_val                # 小文件每秒写的个数
# 测试的挂载点
mount_path = get_config.file_path_val
path_size = get_config.path_size_val
test_path_nums = get_config.test_path_nums
file_path = []
for i in range(test_path_nums):
    fpath = mount_path+'/qiekenao_'+str(i)
    file_path.append(fpath)
for fpath in file_path:
    if not os.path.exists(fpath):
        os.makedirs(fpath)
# 每个帧的大小，或每个io的大小
b_frame_size = get_config.b_frame_size_val           # 单位: KB
l_frame_size = get_config.l_frame_size_val             # 单位: KB
#iosize，不必修改
str_to_write = ("There is a very big baaaaaaaage!")
str_to_write_b = b_frame_size*1024/32*str_to_write
str_to_write_l = l_frame_size*1024/32*str_to_write
# 超时时间，超过该时间则删除文件
timeout = get_config.timeout_val

# 如果测试的目录不存在，则报错
if not os.path.exists(fpath):
    log.error("Sorry,I can't find your test path.")
    os._exit(1)
# 大文件写
def big_file_write(fpath,file_size,p_name,iorate):
    '''
    :Usage : 以固定码流写入大文件，文件到达设定大小则切换写下一个；如果1秒内未完成设置码率的写，则丢弃剩余的帧，并开始下一次设置码率的写
    :param file_size:测试的每个文件的大小
    :param iorate: 码率
    :p_name : 暂未使用
    :return:
    '''

    file_name = str(os.getpid())
    file_name = os.path.join(fpath, file_name)
    #pname = pipedir + str(p_name)
    if 'm' in file_size or 'M' in file_size:
        file_size = re.sub('[a-zA-Z]+','',file_size)
        write_nums = int(file_size)*1024/b_frame_size/iorate
    elif 'G' in file_size or 'g' in file_size:
        file_size = re.sub('[a-zA-Z]+', '', file_size)
        write_nums = int(file_size)*1024*1024/b_frame_size/iorate
    else:
        log.error("Got wrong file size unit, please input M or G.")
        raise Exception("Got wrong file size unit, please input M or G.")
    #Open pipe
    #p = os.open(pname, os.O_WRONLY)
    #Write test files.
    if write_nums != 0:
        t0 = time.time()
        t = 1
        for fileid in range(b_file_nums):
            # 大文件写成功的帧
            bw_suc_frame = 0
            # 大文件写，丢弃的帧
            bw_drop_frame = 0
            fname = file_name+'.'+str(fileid)
            f = os.open(fname,os.O_RDWR|os.O_CREAT)
            for write_num in range(write_nums):
                #Write setting number of frames,which is iorate
                for frame in range(iorate):
                    #Write one frame
                    ret = os.write(f,str_to_write_b)
                    if ret != len(str_to_write_b):
                        log.error("Write %s failed." %(fname))
#                        os.write(p,"%d write failed." %(os.getpid()))
                    bw_suc_frame += 1
                    #else:
                        #log.info("Write %s success." %(fname))
                    os.fsync(f)
                    e_time = time.time()
                    #Time to write one frame
                    span_t = e_time-t0
                    #If time to write iorate frames is larger than 1s,then drop the rest of frame
                    if span_t > t and frame != iorate-1:
                        lw_drop_frame = bw_drop_frame+iorate-frame-1
                        log.error("Big file: %s drop %d frame.##Exceed time per second:%f." %(fname,iorate-frame-1,span_t - t))
                        break
                # 如果1s内完成iorate个帧的写，则进入if语句，并延时直至1s结束
                if span_t -t <=0:
                    time.sleep(t-span_t)
                    t += 1
                # 如果1s内未完成iorate个帧的写，则进入else语句
                elif span_t - t  > 1:
                    # 跳过超时时间个iorate个帧的写
                    write_num = write_num+int(span_t-t)
                    # 打印跳过多少个iorate
                    lw_drop_frame = bw_drop_frame+int(span_t-t)*iorate
                    if int(span_t-t) !=0:
                        log.error("Big file: %s drop %d iorate.##Exceed time:%f." %(fname,int(span_t-t),span_t - t))
                    # 计算超时时间
                    t = int(span_t-t)+t+1
                else:
                    t += 1
            os.close(f)
#            os.write(p, "%d bwrite success" % (os.getpid()))
            log.info("Big file: %s write success frames:%d, and dropped frames:%d" %(fname,bw_suc_frame,bw_drop_frame))
    else:
        log.error("Please input a big file size.")
def lit_file_write(fpath,file_size,p_name,iorate):
    '''
    :Usage : Write file,and if write failed,then send message into the pipe
    :param file_name:
    :param file_size:
    :param iorate:
    :return:
    '''
    # 小文件写，成功的帧
    lw_suc_num = 0
    # 小文件写，丢弃的帧
    lw_drop_num = 0
    # File to write, start with PID
    file_name = str(os.getpid())
    file_name = os.path.join(fpath, file_name)
    # Pipe name, start with process num
#    pname = pipedir + str(p_name)
    # Judge iosize
    if 'M' in file_size or 'm' in file_size:
        file_size = re.sub('[a-zA-Z]+','',file_size)
        # 每个文件以l_frame_size块大小，需要写的次数
        write_nums = int(file_size)*1024/l_frame_size
    elif 'k' in file_size or 'K' in file_size:
        file_size = re.sub('[a-zA-Z]+','', file_size)
        # 每个文件以l_frame_size块大小，需要写的次数
        write_nums = int(file_size)/l_frame_size
    else:
        log.error("Got wrong file size unit, please input M or K.")
        raise Exception("Got wrong file size unit, please input M or K.")
#    p = os.open(pname, os.O_WRONLY)    # Open pipe file.
    # Write l_file_nums little files.
    # 每次循环写iorte个文件，如果在写iorate个文件的循环中，累计时间超过了1秒钟，则退出本次写循环
    # 开始写下一个iorate个文件；如果写iorate个文件未超出1秒，则等待至1秒，然后进行下一次写iorate
    # 个文件
    if write_nums >= 0:
        # Base time
        t0 = time.time()
        for fileid in range(1,l_file_nums/iorate+1):        # l_file_nums个文件，每次写iorate个
            for frame in range(iorate):
                fname = file_name + '.' + str(fileid)+'.'+str(frame)
                f = os.open(fname, os.O_RDWR | os.O_CREAT)
                for write_num in range(write_nums):
                    ret = os.write(f,str_to_write_l)
                    if ret != len(str_to_write_l):
                        log.error("Write %s failed." %(fname))
#                        os.write(p,"%d write failed." %(os.getpid()))
                os.fsync(f)
                os.close(f)
                lw_suc_num += 1
                e_time = time.time()
                span_t = e_time - t0
                if span_t  > fileid*1:
                    lw_drop_num = lw_drop_num + iorate - frame -1
                    log.error("Little file: %s drop the rest of files:%d.##Exceed time:%f." %(fname,iorate-frame-1,span_t-fileid))
                    break
            if fileid >= span_t:
                time.sleep(fileid-span_t)
#        os.write(p,"%d write success" %(os.getpid()))
        log.info("Little file:write %d files success, and dropped %d files." %(lw_suc_num,lw_drop_num))
    else:
        log.error("Please input a big file size.")

def remove_files(fpath):
    '''

    :param filename:
    :param timeout:
    :return:
    '''
    while True:
        lists = os.listdir(fpath)
        part_list = random.sample(lists,len(lists)/rm_file_threads)
        for i in part_list:
            file_to_rm = fpath+i
            if os.path.isfile(file_to_rm):
                mtime = datetime.datetime.fromtimestamp(os.path.getmtime(file_to_rm))
                ntime = datetime.datetime.now()
                if (ntime-mtime).seconds >= timeout:
                    if os.path.exists(file_to_rm):
                        os.remove(file_to_rm)
                        log.info("Remove %s." %(file_to_rm))
        new_lists = os.listdir(fpath)
        if len(lists) == len(new_lists):
            break
def check_path_size(fpath,psize,pipeout):
    '''
    :Usage:判断测试目录大小是否超出了设置阈值
    :param fpath: 测试的目录
    :param psize: 设置的阈值
    :return: None
    '''
    while True:
        cmd = ("du -sh %s 2> /dev/null| awk '{print $1}'" %(fpath))
        res,output = commands.getstatusoutput(cmd)
        if 'G' in output:
            cur_size = output.split('G')[0]
            if float(cur_size) >= float(psize):
                print "###############Change test path.#################"
                os.write(pipeout, 'break')
        time.sleep(10)
def ctrlc(b_pool):
    for p in b_pool:
        p.terminate
