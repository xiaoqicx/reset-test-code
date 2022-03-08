#!/bin/bash

#set -x
timeNum=2
deviceNum=24

cd /opt/intel/vpu_accelerator_samples/hddlunite
ROOTDIR=$PWD

device_sw_id=(100b500 100b600 100b700 100b800 100b900 100ba00 100bd00 100be00 100bf00 100c000 100c100 100c200 100c500 100c600 100c700 100c800 100c900 100ca00 100cd00 100ce00 100cf00 100d000 100d100 100d200);


dirLogName=$(date +%F)-$(date +%T)


if [ $# -eq 1 ]; then
  logPath=$1
else
  logPath=$ROOTDIR/pmslog/$dirLogName
  mkdir -p $logPath
fi

. ./env_host.sh

./bin/GroupTool -q > $logPath/group.txt
grouplog=`grep $logPath/group.txt -nre "Total group"`

groupNum=`echo $grouplog|cut -d '(' -f2|cut -d ')' -f1`
echo "Total group Number: $groupNum" | tee -a $logPath/pmsReset.log

declare -A -g GroupMap;
declare -A -g groupIDDeviceHandleMap;
declare -A -g groupIDDeviceIDMap;
declare -A -g groupIDPid;
declare -A -g groupIDCPU;

getGroupIDMap()
{
    #key(groupid)-[devicehandle, deviceID]
    groupLineNum=`grep $logPath/group.txt -nre "2022"|wc -l`
    
    if (($groupLineNum != 24));then
       echo "Total group number is incorrect." | tee -a $logPath/pmsReset.log
       exit 0
    fi
    
    while read groupLine
    do
        if [[ $groupLine =~ "2022" ]];then
           #echo $groupLine |awk 'BEGIN {FS = "|"} {print $3}'
           groupID=`echo $groupLine |awk 'BEGIN {FS = "|"} {print $3}'`
           #echo $groupLine |awk 'BEGIN {FS = "|"} {print $5}'
           deviceHandle=`echo $groupLine |awk 'BEGIN {FS = "|"} {print $5}'`
           #echo $groupLine |awk 'BEGIN {FS = "|"} {print $6}'
           deviceID=`echo $groupLine |awk 'BEGIN {FS = "|"} {print $6}'`
           #GroupMap[eval($groupID)]=[eval($deviceHandle),eval($deviceID)]
           GroupMap[`eval echo $groupID`]=[`eval echo $deviceHandle`,`eval echo $deviceID`]
           groupIDDeviceHandleMap[`eval echo $groupID`]=`eval echo $deviceHandle`
           groupIDDeviceIDMap[`eval echo $groupID`]=`eval echo $deviceID`
    #       echo "groupID: $groupID, deviceHandle: $deviceHandle,deviceID: $deviceID"
        fi
    done <<< "$(cat $logPath/group.txt)"
    
    if (( ${#GroupMap[@]} != 24 ));then
       echo "Total group map number is incorrect" | tee -a $logPath/pmsReset.log
       exit 0
    fi
}

GetPIDAndCPU()
{
  local i=0
  for((;i<24;i++))
  do
    pidValue=`ps -ef|grep hvaCfg_$i.json|head -n 1|cut -c 9-16`
    cpuValue=`ps -aux|grep hvaCfg_$i.json|head -n 1|awk '{print $3}'`
    groupIDCPU[$i]=`eval echo $cpuValue`
    groupIDPid[$i]=`eval echo $pidValue`
  done
}

CheckPIDAndCPU()
{
  local i=0
  for((;i<24;i++))
  do
    #if((groupIDCPU[$i] > 150))||((groupIDCPU[$i] < 50));then
    if [[ `echo "${groupIDCPU[$i]} > 150.0" |bc` -eq 1 ]];then
    #if ((groupIDCPU[$i] > 150));then
      echo "you need to reset group id: $((i+1)), device id:${groupIDDeviceIDMap[$((i+1))]}, cpu:${groupIDCPU[$i]}, or kill groupid fullpipe" | tee -a $logPath/pmsReset.log
      ./bin/DeviceResetTest ${groupIDDeviceIDMap[$((i+1))]} | tee -a $logPath/pmsReset.log
      sleep 300
      pidValue=`ps -ef|grep hvaCfg_$i.json|head -n 1|cut -c 9-16`
      cpuValue=`ps -aux|grep hvaCfg_$i.json|head -n 1|awk '{print $3}'`
      groupIDCPU[$i]=`eval echo $cpuValue`
      groupIDPid[$i]=`eval echo $pidValue`
    elif [[ `echo "${groupIDCPU[$i]} < 10.0" |bc` -eq 1 ]];then
    #elif ((groupIDCPU[$i] < 10 ));then
      sleep 300
      cpuValue=`ps -aux|grep hvaCfg_$i.json|head -n 1|awk '{print $3}'`
      pidValue=`ps -ef|grep hvaCfg_$i.json|head -n 1|cut -c 9-16`
      groupIDCPU[$i]=`eval echo $cpuValue`
      groupIDPid[$i]=`eval echo $pidValue`
      if [[ `echo "${groupIDCPU[$i]} < 10.0" |bc` -eq 1 ]];then
      #if ((groupIDCPU[$i] < 10));then
          echo "you need to reset group id: $((i+1)), device id:${groupIDDeviceIDMap[$((i+1))]}, cpu:${groupIDCPU[$i]}, or kill groupid fullpipe" | tee -a $logPath/pmsReset.log
          ./bin/DeviceResetTest ${groupIDDeviceIDMap[$((i+1))]} | tee -a $logPath/pmsReset.log
          sleep 300
          pidValue=`ps -ef|grep hvaCfg_$i.json|head -n 1|cut -c 9-16`
          cpuValue=`ps -aux|grep hvaCfg_$i.json|head -n 1|awk '{print $3}'`
          groupIDCPU[$i]=`eval echo $cpuValue`
          groupIDPid[$i]=`eval echo $pidValue`
      fi
    else
      echo "groupID: $((i+1)), device id:${groupIDDeviceIDMap[$((i+1))]}, cpu:${groupIDCPU[$i]} is normal." | tee -a $logPath/pmsReset.log
    fi
  done
    echo "Full pipeline number: ${#groupIDCPU[@]};" | tee -a $logPath/pmsReset.log
}

resetDevice()
{
    for ((j = 0;j < timeNum; ++j))
    do
    
    for ((i = 0;i < deviceNum; ++i))
    do
        echo "Start Reset the ${i}th kmb device for the ${j}th round." | tee -a $logPath/pmsReset.log
        echo "######[`date`] process info######." | tee -a $logPath/pmsReset.log
        ps aux | head -1 | tee -a $logPath/pmsReset.log
        ps aux | grep FullPipe | grep -v grep | nl | tee -a $logPath/pmsReset.log
        ./bin/DeviceResetTest $((16#${device_sw_id[$i]})) | tee -a $logPath/pmsReset.log
        sleep 100 | tee -a $logPath/pmsReset.log
        GetPIDAndCPU
        echo "sleep 100 check status" | tee -a $logPath/pmsReset.log
        echo "Full pipeline number: ${#groupIDCPU[@]};" | tee -a $logPath/pmsReset.log
        echo "CPU list: (${groupIDCPU[@]})" | tee -a $logPath/pmsReset.log
        sleep 200 | tee -a $logPath/pmsReset.log | tee -a $logPath/pmsReset.log
        GetPIDAndCPU
        echo "sleep 200 check status" | tee -a $logPath/pmsReset.log
        echo "Full pipeline number: ${#groupIDCPU[@]};" | tee -a $logPath/pmsReset.log
        echo "CPU list: (${groupIDCPU[@]})" | tee -a $logPath/pmsReset.log
        CheckPIDAndCPU
        echo "Stop Reset the ${i}th kmb device for the ${j}th round. " | tee -a $logPath/pmsReset.log
    done
    done
}

getGroupIDMap
resetDevice
