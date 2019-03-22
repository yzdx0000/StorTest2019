#!/bin/bash
#设置源码目录
export SRC_CODE_DIR=/home/StorTest/src_code/P300
#获取数据IP

datas=`pscli --command=get_node_stat --ids=1 | grep data | awk -F ' ' '{print $1}' | cut -d . -f 1-3`
for i in `pscli --command=get_node_stat --ids=1 | grep data | awk -F ' ' '{print $1}' | awk -F '(' '{print $1}'`
do
    mgr_data=$i,$mgr_data
done
mgr_data=`echo $mgr_data | sed -r 's/,$//g'`
for i in $*
do
    j=`echo $i | sed -r 's/\[|,|u|\]//g'`
    cli_data=`echo $j | cut -d . -f 4`
    data_ip=''
    for ip in $datas
    do
        data_ip=$ip"."$cli_data,$data_ip
    done
    cli_data_ip=`echo $data_ip | sed -r 's/,$//g'`
    echo "============================ Authorize client data ip is $cli_data_ip"
    #pscli --command=create_client_auth --auth_info="{\"ip\":\"$j\",\"volume_ids\":[17]}"
    pscli --command=create_client_auth --ip=$j --volume_ids=17 --auto_mount=true --atime=false --posix_acl=false --sync=false
    if [ $? -ne 0 ]
    then
        echo echo "===================================== Authorize $j failed."
        exit 1
    fi
    echo "===================================== Unzip client package on $j"
    ssh $j "mkdir /home/deploy;cd /home/deploy;rm -rf parastor-3.0.0-client*;cp $SRC_CODE_DIR/code/bin/parastor-3.0.0-client* ./;tar -xvf parastor-3.0.0-client* 1> /dev/null;"
    if [ $? -ne 0 ]
    then
        echo echo "===================================== Unzip $j failed."
        exit 1
    fi
   # echo "===================================== Uninstall client on $j"
   # ssh $j "/home/deploy/client/uninstall.py"
   # if [ $? -ne 0 ]
   # then
   #     echo echo "===================================== Uninstall client on $j failed."
   #     exit 1
   # fi
    echo "===================================== Install client on $j, mgr data ip is $mgr_data"
    ssh $j "/home/deploy/client/install.py --ips=$mgr_data"
    if [ $? -ne 0 ]
    then
        echo echo "===================================== Install client on $j failed."
        exit 1
    fi
   # ssh $j "mkdir /mnt/parastor/;mount -t parastor nodev /mnt/parastor/ -o sysname=p300 -o fsname=parastor"
done

#echo "==== install client"
#ssh 10.20.0.30 /home/deploy/client/install.py --ips=10.20.0.34
#ssh 10.20.0.31 /home/deploy/client/install.py --ips=10.20.0.34
#ssh 10.20.0.30 mount -t parastor nodev /mnt/parastor/ -o sysname=p300 -o fsname=parastor
#ssh 10.20.0.31 mount -t parastor nodev /mnt/parastor/ -o sysname=p300 -o fsname=parastor
