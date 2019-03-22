#!/bin/bash

#设置源码目录
export SRC_CODE_DIR=/home/StorTest/src_code/P300
#定义配置文件
deploy_config=$1
node_num=`grep -c "<node>" $deploy_config`
#删除旧包
mkdir /home/deploy
echo "Step 1. Rm the old packages."
cd /home/deploy
rm -rf /home/deploy/parastor-3.0*
#拷贝新包，包括客户端安装包
echo "Step 2. Cp new packages."
cp $SRC_CODE_DIR/code/bin/parastor-3.0.0*.xz .
#清理环境
echo "Step 3. Clean old parastor system ......."
package_name=`ls -F -l | grep "^-" | grep parastor-3.0.0-centos7.5 | awk -F ' ' '{print $9}' | awk -F '.tar' '{print $1}'`
tar -xvf /home/deploy/$package_name".tar.xz" -C /home/deploy >& /dev/null
deploy_tool_path=/home/deploy/$package_name/
$deploy_tool_path/clean --deploy_config=$deploy_config
echo "Step 4. Deploy new package."
package_full_name=/home/deploy/$package_name".tar.xz"
#修改配置文件
echo "====change deploy.xml"
sed -i "s#path>.*<#path>$package_full_name<#g" $deploy_config

echo "====install sys"
/home/deploy/$package_name/deploy --deploy_config=$deploy_config
sleep 120
echo "==== create_node_pool"
if [ $node_num -eq 3 ]
then
    pscli --command=create_node_pool --node_ids=1,2,3 --replica_num="1" --stripe_width="4" --disk_parity_num="2" --node_parity_num="1" --name=firstpool
    if [ $? -ne 0 ]
    then
        echo create_node_pool failed.
        exit 1
    fi
elif [ $node_num -eq 1 ]
then
    pscli --command=create_node_pool --node_ids=1 --replica_num="1" --stripe_width="1" --disk_parity_num="0" --node_parity_num="0" --name=firstpool
    if [ $? -ne 0 ]
    then
        echo create_node_pool failed.
        exit 1
    fi
fi
sleep 60


echo "==== sys start"
time pscli --command=startup
if [ $? -ne 0 ]
then
    echo startup failed.
    exit 1
fi
sleep 60

echo "==== create_storage_pool"
time pscli --command=create_storage_pool --name=stor1 --type=FILE --node_pool_ids=1
if [ $? -ne 0 ]
then
    echo create_storage_pool failed.
    exit 1
fi
sleep 120

echo "==== create_volume"
if [ $node_num -eq 3 ]
then
    pscli --command=create_volume --name=parastor --storage_pool_id=2 --is_simple_conf=true --min_throughput=0 --max_throughput=100 --min_iops=0 --max_iops=100 --replica_num="1" --stripe_width="4" --disk_parity_num="2" --node_parity_num="1"  --dir_slice_num=1 --chunk_size=4096 --obj_size=67108864
	if [ $? -ne 0 ]
	then
	    echo create_volume failed.
	    exit 1
	fi
elif [ $node_num -eq 1 ]
then
    pscli --command=create_volume --name=parastor --storage_pool_id=2 --is_simple_conf=true --min_throughput=0 --max_throughput=100 --min_iops=0 --max_iops=100 --replica_num="1" --stripe_width="1" --disk_parity_num="0" --node_parity_num="0"  --dir_slice_num=1 --chunk_size=4096 --obj_size=67108864
	if [ $? -ne 0 ]
	then
	    echo create_volume failed.
	    exit 1
	fi
fi
#echo "==== create_client_auth"
#pscli --command=create_client_auth --auth_info='{"ip":"20.20.0.30","volume_ids":[16]}'
#sleep 1
#time pscli --command=create_client_auth --auth_info='{"ip":"10.2.40.20","volume_ids":[16]}'
#time pscli --command=create_client_auth --auth_info='{"ip":"10.2.41.161","volume_ids":[16]}'

#echo "==== cp client"
#tar xvf /home/deploy/ParaStor3.0.0_*/parastor-3.0.0-client-centos6.5-*.tar.xz -C /home/deploy/
#scp -rp /home/deploy/client 10.20.0.30:/home/deploy/
#scp -rp /home/deploy/client 10.20.0.31:/home/deploy/

#echo "==== install client"
#ssh 10.20.0.30 /home/deploy/client/install.py --ips=10.20.0.34
#ssh 10.20.0.31 /home/deploy/client/install.py --ips=10.20.0.34
#ssh 10.20.0.30 mount -t parastor nodev /mnt/parastor/ -o sysname=p300 -o fsname=parastor
#ssh 10.20.0.31 mount -t parastor nodev /mnt/parastor/ -o sysname=p300 -o fsname=parastor
