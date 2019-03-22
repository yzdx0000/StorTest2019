#!/bin/bash

source ./config.sh
date=`date +%Y-%m-%d-%H:%M:%S`
index=0
nums=1  # changed by zhanghan 20181127
# add by zhanghan 20181126
username1=$1
username2=$2
username3=$3
groupname1=$4
groupname2=$5
groupname3=$6
nfs_serv_ip=$7
nfs_serv_exp_path=$8
nfs_cli_mnt_path=$9

#total=0
#pass=0
#fail=0

if [ $# -ne 9 ]
then
    echo "[Usage]: $0 username1 username2 username3 groupname1 groupname2 groupname3 nfs_serv_ip nfs_serv_exp_path nfs_cli_mnt_path"
    exit 1
fi

main()
{
    while [ $index -ne $nums ]
    do
        echo -e "############# $index test, start time: $date ###############\n" >> $LOG
        echo -e "############# $index test, start time: $date ###############\n" >> $ELOG

        clean_cache
        sh $path/dac_nfsd_gfkd_poc.sh $username1 $username2 $username3 $nfs_serv_ip $nfs_serv_exp_path $nfs_cli_mnt_path

        clean_cache
        sh $path/dac_nfsd_st.sh $username1 $username2 $username3 $groupname1 $groupname2 $groupname3 $nfs_serv_ip $nfs_serv_exp_path $nfs_cli_mnt_path

        index=`expr $index + 1`
    done
}
main
