#!/bin/bash

source ./acl_common.sh
date=`date +%Y-%m-%d-%H:%M:%S`
index=0

if [ $# -ne 3 ]
then
    echo "$0 another_client_ip run_times test_path"
    exit 1
fi

# opara_ip=$1
cli_ip=$1
nums=$2
test_path=$3   # add by zhanghan 20181126

main()
{
    while [ $index -ne $nums ]
    do
        echo -e "############# $index test, start time: $date ###############\n" >> $LOG
        echo -e "############# $index test, start time: $date ###############\n" >> $ELOG

        clean_cache
        sh $path/acl_chmod.sh  $test_path

        clean_cache
        sh $path/acl_inherit.sh  $test_path

        clean_cache
        sh $path/acl_permission.sh  $test_path

        clean_cache
        sh $path/acl_permission_ext.sh  $test_path

        clean_cache
        sh $path/acl_group_mode.sh  $test_path

        clean_cache
        sh $path/acl_set_get.sh  $test_path

        clean_cache
        sh $path/xattr_test.sh  $cli_ip  $test_path

        index=`expr $index + 1`
    done
}
main
