#!/bin/bash

# Distinguishes cache and log file names.
tag="$1"

# Target database DSN, e.g., postgresql://crmprtd@dbnorth/metnorth
db="$2"

export TIME=$(date -u "+%Y/%m/%d %H:00:00" -d "last hour");

export networks="nt_forestry nt_water yt_gov yt_water yt_avalanche yt_firewx"
for net in ${networks}; do
    export log_file=~/${net}/logs/${tag}_{net}_json.log
    export cache_file=~/${net}/cache/${tag}_{net}_$(date +'%Y-%m-%dT%H:%M:%S').xml
    echo "crmptd_download -N ${net} -L ~/logging.yaml --log_filename ${log_file} -d \"${TIME}\" | tee ${cache_file} |\
       crmprtd_process -c ${db} -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
done
