#!/bin/bash

path=$(pwd)
LOG=$path/dac_st.log
ELOG=$path/dac_error.log
# mnt="/mnt/parastor/"  # comment by zhanghan 20181126

clean_cache()
{
    sync
    echo 3 > /proc/sys/vm/drop_caches
}

# 1 dir; 2 file; 3 line; 4 ace
ace_check()
{
    cd $1

    ace=`getfacl $2 | sed -n "$3p" | sed s/[[:space:]]//g` &> /dev/null

    if [ $ace != $4 ]
    then
        echo "file: $1/$2, the $3 ace not eqive!!!, src: $4, get: $ace" >> $ELOG
    fi

    cd - &> /dev/null
}

