#!/bin/bash

source ./acl_common.sh
# dir=$mnt/permission_ext_test
dir=$1/permission_ext_test  # changed by zhanghan 20181126

permission_ext_test1()
{
    f=$1/f1

    su u1 -c "touch $f; sync"
    su u1 -c "chmod 000 $f"

    su u1 -c "stat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test1 test failed: " >> $ELOG
        echo "read $f attr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test1 test finish!" >> $LOG
}

permission_ext_test2()
{
    f=$1/f2

    su u1 -c "touch $f; sync"
    su u1 -c "chmod 000 $f"

    su u1 -c "getfattr $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test2 test failed: " >> $ELOG
        echo "read $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test2 test finish!" >> $LOG
}

permission_ext_test3()
{
    f=$1/f3

    su u1 -c "touch $f; sync"
    su u1 -c "chmod 000 $f"

    su u1 -c "setfattr -n user.abc -v 134567890 $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test3 test failed: " >> $ELOG
        echo "write $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test3 test finish!" >> $LOG
}

permission_ext_test4()
{
    f=$1/f4
    touch $f
    setfacl -m user:u1:--- $f
    sync

    su u1 -c "stat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test4 test failed: " >> $ELOG
        echo "read $f attr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test4 test finish!" >> $LOG
}

permission_ext_test5()
{
    f=$1/f5
    touch $f
    setfacl -m user:u1:--- $f
    sync

    su u1 -c "setfattr -n user.abc -v 134567890 $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test5 test failed: " >> $ELOG
        echo "write $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test5 test finish!" >> $LOG
}

permission_ext_test6()
{
    f=$1/f6
    touch $f
    setfacl -m user:u1:--- $f
    sync

    su u1 -c "getfattr $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test6 test failed: " >> $ELOG
        echo "read $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test6 test finish!" >> $LOG
}

permission_ext_test7()
{
    f=$1/f7
    touch $f
    setfacl -m group:g1:--- $f
    sync

    su u1 -c "stat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test7 test failed: " >> $ELOG
        echo "read $f attr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test7 test finish!" >> $LOG
}

permission_ext_test8()
{
    f=$1/f8
    touch $f
    setfacl -m group:g1:--- $f
    sync

    su u1 -c "setfattr -n user.abc -v 134567890 $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test8 test failed: " >> $ELOG
        echo "write $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test8 test finish!" >> $LOG
}

permission_ext_test9()
{
    f=$1/f9
    touch $f
    setfacl -m group:g1:--- $f
    sync

    su u1 -c "getfattr $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test9 test failed: " >> $ELOG
        echo "read $f xattr permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test9 test finish!" >> $LOG
}

permission_ext_test10()
{
    d=$1/d10
    mkdir $d
    setfacl -m user:u1:-wx $d
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 2 ]
    then
        echo "permission_ext_test10 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi

    su u1 -c "cd $d; touch f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test10 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test10 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test10 test finish!" >> $LOG
}

permission_ext_test11()
{
    d=$1/d11
    mkdir $d
    setfacl -m user:u1:r-x $d
    sync

    f=$d/f1
    touch $f
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test11 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test11 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; touch f2" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test11 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test11 test finish!" >> $LOG
}

permission_ext_test12()
{
    d=$1/d12
    mkdir $d
    setfacl -m user:u1:rw- $d
    sync

    su u1 -c "cd $d" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test12 test failed: " >> $ELOG
        echo "enter directory $d permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test12 test finish!" >> $LOG
}

permission_ext_test13()
{
    d=$1/d13
    mkdir $d
    setfacl -m group:g1:-wx $d
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 2 ]
    then
        echo "permission_ext_test13 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi

    su u1 -c "cd $d; touch f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test13 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test13 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test13 test finish!" >> $LOG
}

permission_ext_test14()
{
    d=$1/d14
    mkdir $d
    setfacl -m group:g1:r-x $d
    sync

    f=$d/f1
    touch $f
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test14 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test14 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; touch f2" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test14 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test14 test finish!" >> $LOG
}

permission_ext_test15()
{
    d=$1/d15
    mkdir $d
    setfacl -m group:g1:rw- $d
    sync

    su u1 -c "cd $d" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test15 test failed: " >> $ELOG
        echo "enter directory $d permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test15 test finish!" >> $LOG
}

permission_ext_test16()
{
    d=$1/d16
    mkdir $d
    setfacl -m other::-wx $d
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 2 ]
    then
        echo "permission_ext_test16 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi

    su u1 -c "cd $d; touch f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test16 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test16 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test16 test finish!" >> $LOG
}

permission_ext_test17()
{
    d=$1/d17
    mkdir $d
    setfacl -m other::r-x $d
    sync

    f=$d/f1
    touch $f
    sync

    su u1 -c "ls $d" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test17 test failed: " >> $ELOG
        echo "list directory $d permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; rm -rf f1" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test17 test failed: " >> $ELOG
        echo "directory $d delete file permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cd $d; touch f2" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test17 test failed: " >> $ELOG
        echo "directory $d create file permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test17 test finish!" >> $LOG
}

permission_ext_test18()
{
    d=$1/d18
    mkdir $d
    setfacl -m other::rw- $d
    sync

    su u1 -c "cd $d" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test18 test failed: " >> $ELOG
        echo "enter directory $d permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test18 test finish!" >> $LOG
}

permission_ext_test19()
{
    f=$1/f19
    touch $f
    setfacl -m user:u1:-wx $f
    sync

    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test19 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test19 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test19 test finish!" >> $LOG
}

permission_ext_test20()
{
    f=$1/f20
    touch $f
    setfacl -m user:u1:r-x $f
    sync

    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test20 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test20 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test20 test finish!" >> $LOG
}

permission_ext_test21()
{
    f=$1/f21
    touch $f
    setfacl -m group:g1:-wx $f
    sync

    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test21 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test21 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test21 test finish!" >> $LOG
}

permission_ext_test22()
{
    f=$1/f22
    touch $f
    setfacl -m group:g1:r-x $f
    sync

    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test22 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test22 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test22 test finish!" >> $LOG
}

permission_ext_test23()
{
    f=$1/f23
    touch $f
    setfacl -m other::-wx $f
    sync

    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test23 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test23 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test23 test finish!" >> $LOG
}

permission_ext_test24()
{
    f=$1/f24
    touch $f
    setfacl -m other::r-x $f
    sync

    su u1 -c "cat $f" &> /dev/null
    if [ $? -ne 0 ]
    then
        echo "permission_ext_test24 test failed: " >> $ELOG
        echo "read file $f permission error!!!" >> $ELOG
    fi
    
    su u1 -c "echo abc > $f" &> /dev/null
    if [ $? -ne 1 ]
    then
        echo "permission_ext_test24 test failed: " >> $ELOG
        echo "write file $f permission error!!!" >> $ELOG
    fi
        
    echo "permission_ext_test24 test finish!" >> $LOG
}

permission_ext_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
        chmod 777 $dir
    fi

    echo -e "---------- permission extent test start ----------" >> $LOG
    permission_ext_test1 $dir
    permission_ext_test2 $dir
    permission_ext_test3 $dir
    permission_ext_test4 $dir
    permission_ext_test5 $dir
    permission_ext_test6 $dir
    permission_ext_test7 $dir
    permission_ext_test8 $dir
    permission_ext_test9 $dir
    permission_ext_test10 $dir
    permission_ext_test11 $dir
    permission_ext_test12 $dir
    permission_ext_test13 $dir
    permission_ext_test14 $dir
    permission_ext_test15 $dir
    permission_ext_test16 $dir
    permission_ext_test17 $dir
    permission_ext_test18 $dir
    permission_ext_test19 $dir
    permission_ext_test20 $dir
    permission_ext_test21 $dir
    permission_ext_test22 $dir
    permission_ext_test23 $dir
    permission_ext_test24 $dir

    echo -e "---------- permission extent test finish -----------\n" >> $LOG
}

permission_ext_test
