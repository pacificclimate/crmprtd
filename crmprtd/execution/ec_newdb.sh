#!/bin/bash

frequency="$1"

if [[ $frequency = "hourly" ]] || [[ $frequency = "daily" ]]; then
    echo $frequency
else
    echo "This must be called with first argument 'hourly' or 'daily' (e.g. ./hourly_ec.sh daily)"
    exit 1
fi

export net=ec
export TIME=$(date -u "+%Y/%m/%d %H:00:00" -d "last hour");
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')
export provinces="BC YT"

for prov in ${provinces}; do
    export lower_prov=$(echo ${prov} | tr '[:upper:]' '[:lower:]')
    export log_file=~/${net}/logs/${lower_prov}_${frequency}_json.log
    export cache_file=~/${net}/download/${frequency}_${lower_prov}_${NOW}.xml
    echo "download_${net} -p ${lower_prov} -F ${frequency} -L ~/logging.yaml --log_filename ${log_file} -t \"${TIME}\" | tee ${cache_file} |\
       crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
done
