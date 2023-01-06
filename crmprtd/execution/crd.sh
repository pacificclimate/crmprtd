#!/bin/bash

# Distinguishes cache and log file names.
tag="$1"

# Target database DSN, e.g., postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp
db="$2"

export net=crd
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${tag}_{net}_json.log
export cache_file=~/${net}/cache/${tag}_{net}_${NOW}.txt

echo "download_${net} --auth_fname ~/.rtd_auth.yaml --auth_key=${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} |\
 crmprtd_process -c ${db} -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
