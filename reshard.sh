#!/bin/bash

health_status=$(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/health | awk '{print $4}')
#echo $health_status
if [ $health_status != "green" ]; then
	echo "Cluster health not green. Exiting..."
	exit 1
fi

number_of_nodes=$(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cluster/health | jq '.number_of_data_nodes')
if [ $number_of_nodes == "1" ] ; then
	shards=1
	max_shards=5000
else
	shards=3
	max_shards=15000
fi


#exit 0
#exit_status=$?

echo "Changing template_data "

#curl -s -H "Content-Type: application/json" -XPUT $(eshash elastic_curl) 169.254.16.2:9201/_template/template_data -d '
#{
#  "index_patterns": ["flow-*", "dns-*", "dhcp-*", "trackedhost-*", "bigtap-*", "bro_*", "metricbeat-*", "congestion-ip-*", "congestion-pauseframe-*", "network_topology-*"],
#  "settings" : {
#    "index.refresh_interval" : "5s",
#    "number_of_shards": "'$shards'",
#    "auto_expand_replicas": "0-1"
#  },
#  "mappings" : {
#    "doc": {
#      "properties": {
#        "user": {"type": "keyword"},
#        "sIp": {"type": "keyword"},
#        "dIp": {"type": "keyword"},
#        "dP": {"type": "keyword"},
#        "sDesc": {"type": "keyword"},
#        "dDesc": {"type": "keyword"},
#        "devicePort": {"type": "keyword"},
#        "switchPort": {"type": "keyword"},
#        "firstSwitched": {"type": "date"},
#        "lastSwitched": {"type": "date"},
#        "sGeo": {
#          "properties": {
#            "location": {"type": "geo_point"}
#          }
#        },
#        "dGeo": {
#          "properties": {
#            "location": {"type": "geo_point"}
#          }
#        },
#        "rGeo": {
#          "properties": {
#            "location": {"type": "geo_point"}
#          }
#        },
#        "firstSeen": {"type": "date"},
#        "lastSeen": {"type": "date"},
#        "yiaddr": {"type": "keyword"},
#        "yname": {"type": "keyword"},
#        "ipAddr": {"type": "keyword"},
#        "hostName": {"type": "keyword"},
#        "qnamelist": {"type": "keyword"}
#      }
#    }
#  }
#}'
#exit 1
#echo "Template change done"

current_date=$(date -u "+%Y.%m.%d")
last_date=$(date -u "+%Y.%m.%d" -d '-1 days')

INDICES=($(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices | grep open | awk '{ if($1 == "close") print $2; else print $3 }' | sort -t '2' -k2 -r  ))
#echo ${INDICES[0]}
#echo ${INDICES[1]}
#echo ${INDICES[2]}
#echo ${INDICES[3]}

for i in "${INDICES[@]}"
    do
        #echo $i
	
	#wildcard="-*"
	#dest=$i$wildcar
	current_shard_count=$(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cluster/health | jq '.active_primary_shards')
	if [ $current_shard_count -le $max_shards ] ; then
		echo "Sharding to limit complete"
		exit 0
	fi

	shards_left=`expr $current_shard_count - $max_shards`
	echo "$shards_left of $max_shards left"

	status_of_index=$(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices/"$i" | awk '{print $1}')
	if [ $status_of_index == "close" ] ; then
		curl -XPOST $(eshash elastic_curl) 169.254.16.2:9201/"$i"/_open
	fi

	#Check if any index is reading events
	#docs_1=($(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices/"$i" | awk '{print $7}' ))
	#sleep 10s
	#docs_2=($(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices/"$i" | awk '{print $7}' ))

	#if [ `expr $docs_2 - $docs_1` -gt 0 ] ; then
	#	continue
	#fi
	

        
	if [[ "$i" != ".config" ]] &&  [[ "$i" != ".kibana" ]] && [[ "$i" != ".watch"* ]] && [[ "$i" != ".security-6" ]] && [[ "$i" != ".monitoring"* ]] && [[ "$i" != ".triggered_watches" ]]  && [[ "$i" != ".ml"* ]] && [[ "$i" != *"reindexed"* ]] && [[ "$i" != *"$current_date" ]] && [[ "$i" != *"$last_date" ]] ; then
		date -u "+[%F:%T]"
		echo "$i"
		
		#Getting prefix of index for painless code
		if [[ "$i" == "bro"*  ]] || [[ "$i" == "trackedhost"* ]] || [[ "$i" == "metricbeat"* ]] || [[ "$i" == "dns"* ]]	|| [[ "$i" == "dhcp"* ]] ; then
			prefix=$(echo "$i" | cut -d'-' -f 1)
			date=$(echo "$i" | cut -d'-' -f 2)
		else
			prefix=$(echo "$i" | cut -d'-' -f 1-2)
			date=$(echo "$i" | cut -d'-' -f 3)
		fi
		prefix=$prefix"-"
		
		#Ignoring indices over 10Gb
		index_size_in_bytes=($(curl -s $(eshash elastic_curl) 169.254.16.2:9201/"$i"/_stats | jq '._all.primaries.store.size_in_bytes'))

		if [ $index_size_in_bytes -ge 10737418240 ]; then
			echo "Index bigger than 10GB"
			continue
		fi

		curl  -XPOST -H "Content-Type:application/json"  $(eshash elastic_curl) 169.254.16.2:9201/_reindex -d '
				{
					"source": {
						"index":"'$i'"
					},

					"dest": {
						"index":""
					},

					"script": {
						"lang": "painless",
						"source": "ctx._index=\"'$prefix'\" + \"reindexed-\" + (ctx._index.substring(\"'$prefix'\".length(), ctx._index.length()))" 

					}

				}'
	
		
		new_index=$prefix"reindexed-"$date
		echo $new_index
		result=($(curl -s -H "Content-Type:application/json" -XGET $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices | grep  $new_index))

		if [ -z "$result" ] ; then
			:
		else
			curl -s -XDELETE $(eshash elastic_curl) 169.254.16.2:9201/"$i"
			echo "Deleted $i"	
		fi
	fi

    done

    echo "Reindexing Complete"

exit 0



