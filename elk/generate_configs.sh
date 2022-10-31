#!/bin/bash
set -a
source .env

envsubst '
${AUTH0_DOMAIN}
${AUTH0_CLIENT_ID}
${AUTH0_CLIENT_SECRET}
${KIBANA_BASIC_GUEST}
${KIBANA_BASIC_ADMIN}
' < nginx/templates/elastic.conf > nginx/conf.d/elastic.conf

envsubst '
${AUTH0_DOMAIN}
${AUTH0_CLIENT_ID}
${AUTH0_CLIENT_SECRET}
' < vouch/config.yml.template > vouch/config.yml

envsubst '
${KIBANA_ES_SERVICE_ACCOUNT_TOKEN}
' < kibana/kibana.yml.template > kibana/kibana.yml

envsubst '
${HEARTBEAT_API_ID}
${HEARTBEAT_API_KEY}
' < heartbeat/heartbeat.yml.template > heartbeat/heartbeat.yml
