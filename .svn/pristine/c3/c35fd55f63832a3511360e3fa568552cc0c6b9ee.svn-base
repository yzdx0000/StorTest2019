#!/bin/bash

source ./acl_common.sh
# dir=$mnt/xattr_test
dir=$2/xattr_test  # changed by zhanghan 20181126

# opara=$1
cli_ip=$1

user="user."
tru="trusted."
sec="security."
# sys="system.advacl"  # changed by zhanghan 20181126
sys="system.posix_acl_access"
value="abc1234567890xyz"
data="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


# 1-dir, 2-obj, 3-name
check_xattr()
{
    cd $1

    x=`getfattr -d -m "" $2 | grep $3 | sed s/\"//g`
    if [ $x != "$3=$value" ]
    then
        echo "$1/$2: get[$x], set[$3=$value], xattr error!!!" >> $ELOG
    fi

    cd - &> /dev/null
}

# 1-dir, 2-obj
check_advacl()
{
    cd $1

    x=`getfattr -d -m "" $2 | grep system | cut -d = -f1 | sed -n 1p`
    if [[ $x != $sys ]]
    then
        echo "$1/$2: get[$x], set[$sys], xattr error!!!" >> $ELOG
    fi

    cd - $> /dev/null
}

# 1-dir, 2-obj, 3-name
_check_xattr()
{
    cd $1
    x=`getfattr -d -m "" $2 | grep $3`
    cd - &> /dev/null

    y=`ssh root@$cli_ip "cd $1; getfattr -d -m '' $2 | grep $3"`
    if [ $x != $y ]
    then
        echo "$1/$2 xatter error, local[$x], $cli_ip[$y]" >> $ELOG
    fi
}

# 1-dir, 2-obj
_check_advacl()
{
    cd $1
    x=`getfattr -d -m "" $2 | grep system`
    cd - $> /dev/null

    y=`ssh root@$cli_ip "cd $1; getfattr -d -m '' $2 | grep system"`
    if [ $x != $y ]
    then
        echo "$1/$2: xatter error, local[$1], $cli_ip[$y]" >> $ELOG
    fi
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-001
# 测试项目  : 测试获取Adv ACLs名称的扩展属性
# 用例标题  : 支持获取扩展属性01
# 用例简介  : 使用工具读写文件的Adv ACLs名称的扩展属性
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfacl设置文件f0的acl
#             3、使用getfattr查看文件f0的Adv ACLs名称的扩展属性
# 预期结果  : 返回的system.advacl名称的扩展属性
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test1()
{
    f=f1
    touch $1/$f
    sync

    setfacl -m user:u1:rw- $1/$f
    clean_cache

    check_advacl $1 $f
    echo "xattr_test1 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-002
# 测试项目  : 测试获取user.名称的扩展属性
# 用例标题  : 支持获取扩展属性02
# 用例简介  : 使用工具读写文件user.名称的扩展属性
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfattr设置文件f0的user.名称的扩展属性
#             3、使用getfattr查看文件f0的user.名称的扩展属性
# 预期结果  : 返回user.名称的扩展属性与设置的相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test2()
{
    f=f2
    touch $1/$f
    sync

    n=${user}abc

    setfattr -n $n -v $value $1/$f
    clean_cache

    check_xattr $1 $f $n
    echo "xattr_test2 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-003
# 测试项目  : 测试获取security.名称的扩展属性
# 用例标题  : 支持获取扩展属性03
# 用例简介  : 使用工具读写文件security.名称的扩展属性
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfattr设置文件f0的security.名称的扩展属性
#             3、使用getfattr查看文件f0的security.名称的扩展属性
# 预期结果  : 返回security.名称的扩展属性与设置的相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test3()
{
    f=f3
    touch $1/$f
    sync

    n=${sec}ghi

    setfattr -n $n -v $value $1/$f
    clean_cache

    check_xattr $1 $f $n
    echo "xattr_test3 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-004
# 测试项目  : 测试获取trusted.名称的扩展属性
# 用例标题  : 支持获取扩展属性04
# 用例简介  : 使用工具读写文件trusted.名称的扩展属性
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfattr设置文件f0的trusted.名称的扩展属性
#             3、使用getfattr查看文件f0的trusted.名称的扩展属性
# 预期结果  : 返回trusted.名称的扩展属性与设置的相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test4()
{
    f=f4
    touch $1/$f
    sync

    n=${tru}def

    setfattr -n $n -v $value $1/$f
    clean_cache

    check_xattr $1 $f $n
    echo "xattr_test4 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-005
# 测试项目  : 测试获取user. security. trusted. system.名称的扩展属性
# 用例标题  : 支持获取扩展属性05
# 用例简介  : 使用工具读写目录user. security. trusted. system.名称的扩展属性
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端创建文件f0
#             2、使用setfattr设置文件f0的user.名称的扩展属性
#             3、使用setfattr设置文件f0的security.名称的扩展属性
#             4、使用setfattr设置文件f0的trusted.名称的扩展属性
#             5、使用setfacl设置文件f0的acl
#             6、使用getfattr查看文件f0的扩展属性
# 预期结果  : 1、返回的user. security. trusted. 名称的扩展属性
#             与设置的扩展属性相同
#             2、返回system.advacl名称的扩展属性
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test5()
{
    d=d5
    mkdir $1/$d
    sync

    setfattr -n ${user}123 -v $value $1/$d
    setfattr -n ${tru}456 -v $value $1/$d
    setfattr -n ${sec}789 -v $value $1/$d
    setfacl -m user:u1:rw- $1/$d
    clean_cache

    check_xattr $1 $d ${user}123
    check_xattr $1 $d ${tru}456
    check_xattr $1 $d ${sec}789

    check_advacl $1 $d

    echo "xattr_test5 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-006
# 测试项目  : 测试设置文件权限mode
# 用例标题  : 支持扩展属性读写缓存01
# 用例简介  : 多客户端之间设置、获取文件的权限mode
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用chmod修改文件f0的权限mode
#             3、在客户端c2使用stat查看文件f0权限mode
# 预期结果  : 客户端c2返回的文件权限mode与c1设置的权限mode相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test6()
{
    f=$1/f6
    touch $f
    sync

    chmod 777 $f
    clean_cache

    mode=`ssh $cli_ip "stat $f | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0777 ]
    then
        echo "xattr_test6 test failed: " >> $ELOG
        echo "$f get[$mode], set[777], mode error!!!" >> $ELOG
    fi
    echo "xattr_test6 test finish!" >> $LOG
}


#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-007
# 测试项目  : 测试设置文件的所有者和所有组
# 用例标题  : 支持扩展属性读写缓存02
# 用例简介  : 多客户端之间设置、获取文件的所有者和所有组
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
#             3、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用chown修改文件f0的所有者和所有组
#             3、在客户端c2使用stat查看文件f0的所有者和所有组
# 预期结果  : 客户端c2返回的文件所有者和所有组与c1设置的所有者和所有组相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test7()
{
    f=$1/f7
    touch $f
    sync

    chown u1:g2 $f
    clean_cache

    u=`ssh $cli_ip "stat $f | grep Uid | cut -d ' ' -f11 | sed s/\)//g"`
    if [ $u != "u1" ]
    then
        echo "xattr_test7 test failed: " >> $ELOG
        echo "$f get[$u], set[u1], uid error!!!" >> $ELOG
    fi

    g=`ssh $cli_ip "stat $f | grep Uid | cut -d ' ' -f21 | sed s/\)//g"`
    if [ $g != "g2" ]
    then
        echo "xattr_test7 test failed: " >> $ELOG
        echo "$f get[$g], set[g2], gid error!!!" >> $ELOG
    fi
    echo "xattr_test7 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-008
# 测试项目  : 测试设置Adv ACLs名称的扩展属性
# 用例标题  : 支持设置Adv ACLs名称的扩展属性
# 用例简介  : 设置目录的Adv ACLs名称的扩展属性，并确认成功
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfacl设置目录d0的acl
#             3、使用getfattr查看目录d0的扩展属性
# 预期结果  : 1、设置目录d0的acl成功，返回0
#             2、返回目录d0的system.advacl名称的扩展属性
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月24日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test8()
{
    d=d8
    mkdir $1/$d
    sync

    setfacl -d -m user:u1:rw- $1/$d
    if [ $? -ne 0 ]
    then
        echo "xattr_test8 test failed: " >> $ELOG
        echo "$1/$d set xattr error!!!" >> $ELOG
    fi
    clean_cache

    check_advacl $1 $d
    echo "xattr_test8 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-009
# 测试项目  : 测试设置user.名称的扩展属性
# 用例标题  : 支持设置普通名称的扩展属性01
# 用例简介  : 设置目录的user.名称的扩展属性，并确认成功
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfattr设置目录d0的user.扩展属性
#             3、使用getfattr查看目录d0的扩展属性
# 预期结果  : 1、设置目录d0的user.扩展属性成功，返回0
#             2、返回的目录d0扩展属性与设置的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test9()
{
    d=d9
    mkdir $1/$d
    sync

    n=${user}abc

    setfattr -n $n -v $value $1/$d
    if [ $? -ne 0 ]
    then
        echo "xattr_test9 test failed: " >> $ELOG
        echo "$1/$d set xattr error!!!" >> $ELOG
    fi
    clean_cache

    check_xattr $1 $d $n
    echo "xattr_test9 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-010
# 测试项目  : 测试设置security.名称的扩展属性
# 用例标题  : 支持设置普通名称的扩展属性02
# 用例简介  : 设置目录的security.名称的扩展属性，并确认成功
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfattr设置目录d0的security.扩展属性
#             3、使用getfattr查看目录d0的扩展属性
# 预期结果  : 1、设置目录d0的security.扩展属性成功，返回0
#             2、返回的目录d0扩展属性与设置的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test10()
{
    d=d10
    mkdir $1/$d
    sync

    n=${sec}ghi

    setfattr -n $n -v $value $1/$d
    if [ $? -ne 0 ]
    then
        echo "xattr_test10 test failed: " >> $ELOG
        echo "$1/$d set xattr error!!!" >> $ELOG
    fi
    clean_cache

    check_xattr $1 $d $n
    echo "xattr_test10 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-011
# 测试项目  : 测试设置trusted.名称的扩展属性
# 用例标题  : 支持设置普通名称的扩展属性03
# 用例简介  : 设置目录的trusted.名称的扩展属性，并确认成功
# 预置条件  : 挂载的parastor文件系统支持扩展属性功能
# 输    入  :
# 执行步骤  : 1、在客户端创建目录d0
#             2、使用setfattr设置目录d0的trusted.扩展属性
#             3、使用getfattr查看目录d0的扩展属性
# 预期结果  : 1、设置目录d0的trusted.扩展属性成功，返回0
#             2、返回的目录d0扩展属性与设置的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月23日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test11()
{
    d=d11
    mkdir $1/$d
    sync

    n=${tru}def

    setfattr -n $n -v $value $1/$d
    if [ $? -ne 0 ]
    then
        echo "xattr_test11 test failed: " >> $ELOG
        echo "$1/$d set xattr error!!!" >> $ELOG
    fi
    clean_cache

    check_xattr $1 $d $n
    echo "xattr_test11 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-012
# 测试项目  : user.名称的扩展属性最大支持64KB
# 用例标题  : 单名称的扩展属性最大支持64KB01
# 用例简介  : 创建user.名称的扩展属性超过64KB，64KB内可以创建成功，
#             超过64KB后创建失败
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、系统存在多个用户
# 输    入  :
# 执行步骤  : (ps:64KB=head + (entry_head + name_len    +     value_len)
#                      (32)       (12)      (strlen(name)+1)  strlen(value)
#                 1、使用相同长度的name和相同长度的value
#                 2、计算64KB缓存可以存放N个user.名称的扩展属性
#             )
#             1、在客户端创建文件f0
#             2、使用setfattr为文件f0设置N+1个user.名称的扩展属性
#             3、验证设置每个user.名称的扩展属性返回值
#             4、记录返回no space错误时设置的entry数
# 预期结果  : 1、设置<=N个user.名称的扩展属性不返回错误
#             2、返回no space错误时设置的user.名称扩展属性个数为N+1
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test12()
{
    f=f12
    touch $1/$f
    sync

    for ((i = 0; i < 64; i++))
    do
        n=${user}abc_$i
        setfattr -n $n -v $data $1/$f
        if [ $? -ne 0 ]
        then
            echo "xattr_test12 test failed: " >> $ELOG
            echo "$1/$d set xattr error!!!" >> $ELOG
        fi
    done

    n=${user}abc_$i
    setfattr -n $n -v $data $1/$f &> /dev/null
    if [ $? -eq 0 ]
    then
        echo "xattr_test12 test failed: " >> $ELOG
        echo "$1/$f set xattr error!!!" >> $ELOG
    fi
    echo "xattr_test12 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-013
# 测试项目  : security.名称的扩展属性最大支持64KB
# 用例标题  : 单名称的扩展属性最大支持64KB02
# 用例简介  : 创建security.名称的扩展属性超过64KB，64KB内可以创建成功，
#             超过64KB后创建失败
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、系统存在多个用户
# 输    入  :
# 执行步骤  : (ps:64KB=head + (entry_head + name_len    +     value_len)
#                      (32)       (12)      (strlen(name)+1)  strlen(value)
#                 1、使用相同长度的name和相同长度的value
#                 2、计算64KB缓存可以存放N个security.名称的扩展属性
#             )
#             1、在客户端创建文件f0
#             2、使用setfattr为文件f0设置N+1个security.名称的扩展属性
#             3、验证设置每个security.名称的扩展属性返回值
#             4、记录返回no space错误时设置的entry数
# 预期结果  : 1、设置<=N个security.名称的扩展属性不返回错误
#             2、返回no space错误时设置的security.名称扩展属性个数为N+1
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test13()
{
    f=f13
    touch $1/$f
    sync

    for ((i = 0; i < 64; i++))
    do
        n=${tru}abc_$i
        setfattr -n $n -v $data $1/$f
        if [ $? -ne 0 ]
        then
            echo "xattr_test13 test failed: " >> $ELOG
            echo "$1/$d set xattr error!!!" >> $ELOG
        fi
    done

    n=${tru}abc_$i
    setfattr -n $n -v $data $1/$f &> /dev/null
    if [ $? -eq 0 ]
    then
        echo "xattr_test13 test failed: " >> $ELOG
        echo "$1/$f set xattr error!!!" >> $ELOG
    fi
    echo "xattr_test13 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-014
# 测试项目  : trusted.名称的扩展属性最大支持64KB
# 用例标题  : 单名称的扩展属性最大支持64KB03
# 用例简介  : 创建trusted.名称的扩展属性超过64KB，64KB内可以创建成功，
#             超过64KB后创建失败
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、系统存在多个用户
# 输    入  :
# 执行步骤  : (ps:64KB=head + (entry_head + name_len    +     value_len)
#                      (32)       (12)      (strlen(name)+1)  strlen(value)
#                 1、使用相同长度的name和相同长度的value
#                 2、计算64KB缓存可以存放N个trusted.名称的扩展属性
#             )
#             1、在客户端创建文件f0
#             2、使用setfattr为文件f0设置N+1个trusted.名称的扩展属性
#             3、验证设置每个trueste.名称的扩展属性返回值
#             4、记录返回no space错误时设置的entry数
# 预期结果  : 1、设置<=N个trusted.名称的扩展属性不返回错误
#             2、返回no space错误时设置的trusted.名称扩展属性个数为N+1
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test14()
{
    f=f14
    touch $1/$f
    sync

    for ((i = 0; i < 64; i++))
    do
        n=${sec}abc_$i
        setfattr -n $n -v $data $1/$f
        if [ $? -ne 0 ]
        then
        echo "xattr_test14 test failed: " >> $ELOG
            echo "$1/$d set xattr error!!!" >> $ELOG
        fi
    done

    n=${sec}abc_$i
    setfattr -n $n -v $data $1/$f &> /dev/null
    if [ $? -eq 0 ]
    then
        echo "xattr_test14 test failed: " >> $ELOG
        echo "$1/$f set xattr error!!!" >> $ELOG
    fi
    echo "xattr_test14 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-015
# 测试项目  : 测试user.名称的扩展属性在多客户端一致
# 用例标题  : 能够维护多客户端一致性01
# 用例简介  : 在不同客户端创建和获取user.名称的扩展属性，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用setfattr设置文件f0的user.名称的扩展属性
#             3、在客户端c1和c2使用getfattr查看文件f0的
#             user.名称的扩展属性
# 预期结果  : 客户端c1和c2返回文件f0的user.名称的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test15()
{
    f=f15
    touch $1/$f
    sync

    n=${user}abc

    setfattr -n $n -v $value $1/$f
    clean_cache

    _check_xattr $1 $f $n
    echo "xattr_test15 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-016
# 测试项目  : 测试security.名称的扩展属性在多客户端一致
# 用例标题  : 能够维护多客户端一致性02
# 用例简介  : 在不同客户端创建和获取security.名称的扩展属性，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用setfattr设置文件f0的security.名称的扩展属性
#             3、在客户端c1和c2使用getfattr查看文件f0的
#             security.名称的扩展属性
# 预期结果  : 客户端c1和c2返回文件f0的system.名称的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test16()
{
    f=f16
    touch $1/$f
    sync

    n=${sec}ghi

    setfattr -n $n -v $value $1/$f
    clean_cache

    _check_xattr $1 $f $n
    echo "xattr_test16 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-017
# 测试项目  : 测试trusted.名称的扩展属性在多客户端一致
# 用例标题  : 能够维护多客户端一致性03
# 用例简介  : 在不同客户端创建和获取trusted.名称的扩展属性，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用setfattr设置文件f0的trusted.名称的扩展属性
#             3、在客户端c1和c2使用getfattr查看文件f0的
#             trusted.名称的扩展属性
# 预期结果  : 客户端c1和c2返回文件f0的trusted.名称的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test17()
{
    f=f17
    touch $1/$f
    sync

    n=${tru}def

    setfattr -n $n -v $value $1/$f
    clean_cache

    _check_xattr $1 $f $n
    echo "xattr_test17 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-018
# 测试项目  : 测试system.名称的扩展属性在多客户端一致
# 用例标题  : 能够维护多客户端一致性04
# 用例简介  : 在不同客户端创建和获取system.名称的扩展属性，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用setfattr设置文件f0的system.u1名称的扩展属性
#             3、在客户端c1和c2使用getfattr查看文件f0的
#             system.名称的扩展属性
# 预期结果  : 客户端c1和c2返回文件f0的system.名称的扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test18()
{
    f=f18
    touch $1/$f
    sync

    setfacl -m user:u1:rw- $1/$f
    clean_cache

    _check_advacl $1 $f
    echo "xattr_test18 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-019
# 测试项目  : 测试多个名称的扩展属性在多客户端一致
# 用例标题  : 能够维护多客户端一致性05
# 用例简介  : 在不同客户端创建和获取user. security. trusted. system. Adv ACLs
#             名称的扩展属性，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用setfattr设置文件f0的user. security. trusted. sytem.
#             名称的扩展属性
#             3、使用setfacl设置文件f0的Adv ACLs名称的扩展属性
#             4、在客户端c1和c2使用getfattr查看文件f0的user.
#             security. trusted. system. 名称的扩展属性
#             5、在客户端c1和c2使用getfacl查看文件f0的
#             Adv ACLs名称的扩展属性
# 预期结果  : 客户端c1和c2返回文件f0的user. security. trusted. system.
#             Adv ACLs扩展属性相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月28日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test19()
{
    f=f19
    touch $1/$f
    sync

    setfattr -n ${user}123 -v $value $1/$f
    setfattr -n ${tru}456 -v $value $1/$f
    setfattr -n ${sec}789 -v $value $1/$f
    setfacl -m user:u1:rw- $1/$f
    clean_cache

    _check_xattr $1 $f ${user}123
    _check_xattr $1 $f ${tru}456
    _check_xattr $1 $f ${sec}789

    _check_advacl $1 $f
    echo "xattr_test19 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-020
# 测试项目  : 测试文件所有者和所有组在多客户端一致
# 用例标题  : 能够维护多客户端一致性06
# 用例简介  : 在不同客户端设置和获取文件的所有者和所有组，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
#             3、系统存在多个用户和组
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用chown改变文件f0的所有者
#             3、使用chown改变文件f0的所有组
#             4、在客户端c2使用stat获取文件f0的所有者和所有组
# 预期结果  : 客户端c1和c2返回文件的所有者和所有组相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月31日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test20()
{
    d=$1/d20
    mkdir $d
    sync

    chmod 000 $d
    clean_cache

    mode=`ssh $cli_ip "stat $d | grep Uid | cut -d ' ' -f2 | cut -b 2-5"`
    if [ $mode -ne 0000 ]
    then
        echo "xattr_test20 test failed: " >> $ELOG
        echo "$d get[$mode], set[000], mode error!!!" >> $ELOG
    fi

    echo "xattr_test20 test finish!" >> $LOG
}

#/*****************************************************************************
# 用例编号  : DAC-STUC-CLIENT-021
# 测试项目  : 测试文件的权限mode在多客户端一致
# 用例标题  : 能够维护多客户端一致性07
# 用例简介  : 在不同客户端设置和获取文件的权限mode，验证结果
# 预置条件  : 1、挂载的parastor文件系统支持扩展属性功能
#             2、parastor文件系统挂载多个客户端
# 输    入  :
# 执行步骤  : 1、在客户端c1创建文件f0
#             2、使用chmod改变文件f0的权限mode
#             4、在客户端c2使用stat获取文件f0的权限mode
# 预期结果  : 客户端c1和c2返回文件的权限mode相同
# 后置条件  :
#
# 修改历史  :
#  1.日    期   : 2016年3月31日
#    作    者   : wangsen
#    修改内容   : 设计用例
#
#*****************************************************************************/
xattr_test21()
{
    d=$1/d21
    mkdir $d
    sync

    chown u1:g2 $d
    clean_cache

    u=`ssh $cli_ip "stat $d | grep Uid | cut -d ' ' -f11 | sed s/\)//g"`
    if [ $u != "u1" ]
    then
        echo "xattr_test21 test failed: " >> $ELOG
        echo "$d get[$u], set[u1], uid error!!!" >> $ELOG
    fi

    g=`ssh $cli_ip "stat $d | grep Uid | cut -d ' ' -f21 | sed s/\)//g"`
    if [ $g != "g2" ]
    then
        echo "xattr_test21 test failed: " >> $ELOG
        echo "$d get[$g], set[g2], gid error!!!" >> $ELOG
    fi
    echo "xattr_test21 test finish!" >> $LOG
}

xattr_test22_27()
{
    for ((i = 22; i < 28; i++))
    do
        f=$1/f$i
        touch $f
    done
    sync

    ./xattr_st_22_27 >> $LOG
    echo "xattr_test22_27 test finish!" >> $LOG
}

xattr_test()
{
    if [ -d $dir ]
    then
        rm -rf $dir/*
        sync
    else
        mkdir -p $dir
    fi

#    gcc -o xattr_st_22_27 ./xattr_ops.c
#     chmod 777 xattr_st_22_27                         # comment by zhanghan 20181126

    echo -e "---------- xattr test start ----------" >> $LOG

    xattr_test1 $dir
    xattr_test2 $dir
    xattr_test3 $dir
    xattr_test4 $dir
    xattr_test5 $dir
    xattr_test6 $dir
    xattr_test7 $dir
    xattr_test8 $dir
    xattr_test9 $dir
    xattr_test10 $dir
    xattr_test11 $dir
    xattr_test12 $dir
    xattr_test13 $dir
    xattr_test14 $dir
    xattr_test15 $dir
    xattr_test16 $dir
    xattr_test17 $dir
    xattr_test18 $dir
    xattr_test19 $dir
    xattr_test20 $dir
    xattr_test21 $dir
#     xattr_test22_27 $dir  # comment by zhanghan 20181126

    echo -e "---------- xattr test finish ----------\n" >> $LOG
}

xattr_test
