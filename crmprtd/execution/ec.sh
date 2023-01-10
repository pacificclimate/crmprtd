#!/bin/bash

frequency="$1"

if [[ $frequency = "hourly" ]] || [[ $frequency = "daily" ]]; then
    echo $frequency
else
    echo "This must be called with first argument 'hourly' or 'daily' (e.g. ./hourly_ec.sh daily)"
    exit 1
fi

# Distinguishes cache and log file names.
tag="$2"

# Target database DSN, e.g., postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp
db="$3"

export net=ec
export TIME=$(date -u "+%Y/%m/%d %H:00:00" -d "last hour");
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')
export provinces="BC YT"

for prov in ${provinces}; do
    export lower_prov=$(echo ${prov} | tr '[:upper:]' '[:lower:]')
    export log_file=~/${net}/logs/${tag}_{lower_prov}_${frequency}_json.log
    export cache_file=~/${net}/download/${tag}_{frequency}_${lower_prov}_${NOW}.xml
    echo "crmptd_download -N ${net} -p ${lower_prov} -F ${frequency} -L ~/logging.yaml --log_filename ${log_file} -t \"${TIME}\" | tee ${cache_file} |\
       crmprtd_process -c ${db} -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
done
