#!/bin/bash
if [ $# -eq 1 ]; then
  logPath=$1
else
  logPath=`pwd`
fi

while true
do
ps aux | head -1 | tee -a $logPath/cpu.log
ps aux | grep FullPipe | grep -v grep | nl | tee -a $logPath/cpu.log
ps aux | grep hddl | grep -v grep | nl | tee -a $logPath/cpu.log

top -b -n 2 -d 10 |head -n 40 |tee -a $logPath/cpu.log
sleep 10
done









