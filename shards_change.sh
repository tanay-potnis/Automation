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
else
	shards=3
fi


#exit 0
#exit_status=$?

echo "Changing template_data to 2 shards"

curl -s -H "Content-Type: application/json" -XPUT $(eshash elastic_curl) 169.254.16.2:9201/_template/template_data -d '
{
  "index_patterns": ["flow-*", "dns-*", "dhcp-*", "trackedhost-*", "bigtap-*", "bro_*", "metricbeat-*", "congestion-ip-*", "congestion-pauseframe-*", "network_topology-*"],
  "settings" : {
    "index.refresh_interval" : "5s",
    "number_of_shards": "'$shards'",
    "auto_expand_replicas": "0-1"
  },
  "mappings" : {
    "doc": {
      "properties": {
        "user": {"type": "keyword"},
        "sIp": {"type": "keyword"},
        "dIp": {"type": "keyword"},
        "dP": {"type": "keyword"},
        "sDesc": {"type": "keyword"},
        "dDesc": {"type": "keyword"},
        "devicePort": {"type": "keyword"},
        "switchPort": {"type": "keyword"},
        "firstSwitched": {"type": "date"},
        "lastSwitched": {"type": "date"},
        "sGeo": {
          "properties": {
            "location": {"type": "geo_point"}
          }
        },
        "dGeo": {
          "properties": {
            "location": {"type": "geo_point"}
          }
        },
        "rGeo": {
          "properties": {
            "location": {"type": "geo_point"}
          }
        },
        "firstSeen": {"type": "date"},
        "lastSeen": {"type": "date"},
        "yiaddr": {"type": "keyword"},
        "yname": {"type": "keyword"},
        "ipAddr": {"type": "keyword"},
        "hostName": {"type": "keyword"},
        "qnamelist": {"type": "keyword"}
      }
    }
  }
}'
#exit 1
echo "Template change done"
	

INDICES=($(curl -s $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices | awk '{print $3}' ))
#echo ${INDICES[0]}
#echo ${INDICES[1]}
#echo ${INDICES[2]}
#echo ${INDICES[3]}

for i in "${INDICES[@]}"
    do
        #echo $i
	
	wildcard="-*"
	dest=$i$wildcard
	if [[ "$i" != ".config" ]] &&  [[ "$i" != ".kibana" ]] && [[ "$i" != ".watch"* ]] && [[ "$i" != ".security-6" ]] && [[ "$i" != ".monitoring"* ]] && [[ "$i" != ".triggered_watches" ]] ; then
		echo "$i"
		
		curl  -XPOST -H "Content-Type:application/json"  $(eshash elastic_curl) 169.254.16.2:9201/_reindex -d '
				{
					"source": {
						"index":"'$i'"
					},

					"dest": {
						"index":"test"
					},

					"script": {
						"lang": "painless",
						"source": "ctx._index=ctx._index + \"-temp\""
					}

				}'
	fi
		
		new_index=$i"-temp"
		result=($(curl -s -H "Content-Type:application/json" -XGET $(eshash elastic_curl) 169.254.16.2:9201/_cat/indices | grep  $new_index))

		if [ -z "$result" ] ; then
			:
		else
			curl -s -XDELETE admin:bsn@169.254.16.2:9201/"$i"	
		fi
	
    done

    echo "Reindexing Complete"

exit 0
