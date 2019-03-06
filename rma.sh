#!/bin/bash
# Reset to factory settings

echo "Starting RMA procedure"

if [ ! $UID -eq 0 ] ; then
  echo "This command needs to be run with sudo"
  exit 1
fi

read -p "Running this process will delete all data on the disk. Continue ? (yes/no)" ans
if [  $ans != "yes" ]; then
       echo "Exiting Decluster procedure"
       exit 1
fi

echo "Decluster initiated"

#RES=$(docker restart datacollect)
#if [ $RES !=  "datacollect" ]; then
#	echo "Datacollect did not restart"
#	exit 1
#fi
sleep 2s

#Flushing Redis keys
echo flushall  nc -q 1 169.254.16.3 6379

#Flushing Replicated Keys
echo flushall  nc -q 1 169.254.16.3 9379

#redis-cli -h 169.254.16.3 -p 9379 flushall
#sleep 5s

#redis-cli -h 169.254.16.3 -p 6379 flushall
#sleep 5s

echo "Stopping Analytics. Removing all containers"
/opt/bigswitch/stop-analytics.sh
sleep 5s

echo "Deleting data on SSD"
rm -rf /var/lib/analytics/data/nodes
#sleep 15s
echo "Data on Disk deleted"

read -p "Resetting back to firstboot. Continue ? (yes/no)" ans
if [  $ans != "yes" ]; then
       echo "Exiting Decluster procedure"
       exit 1
fi

#echo "RMA DONE"
floodlight-boot-factory-default

echo "RMA DONE"
#return 0
