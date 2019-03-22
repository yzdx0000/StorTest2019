#!/bin/bash

path=$(pwd)
LOG=$path/dac_st.log
ELOG=$path/dac_error.log

# nfs_serv_ip='10.2.43.151'
# nfs_serv_exp_path='/mnt/parastor'
# nfs_cli_mnt_path='/mnt/zhanghan'
# nfs_serv_ip=$1
# nfs_serv_exp_path=$2
# nfs_cli_mnt_path=$3   # comment by zhanghan 20181127

# username1='du1'
# username2='du2'
# username3='du3'
# groupname1='dg1'
# groupname2='dg2'
# groupname3='dg3'   # comment by zhanghan 20181126

clean_cache()
{
    sync
    echo 3 > /proc/sys/vm/drop_caches
}
