#!/bin/bash
read -s -p "elastic password:" ES_ELASTIC_PASSWD
docker run \
--cap-add=NET_RAW \
docker.elastic.co/beats/heartbeat:8.4.2 \
setup -E output.elasticsearch.hosts=["https://elk.cloudnativedays.jp:9200"] \
-E output.elasticsearch.username=elastic \
-E output.elasticsearch.password=$ES_ELASTIC_PASSWD
