#!/bin/bash

export net=wmb
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/mof_json.log
export cache_file=~/${net}/download/${net}_${NOW}.txt

echo "download_${net} --auth_fname ~/.rtd_auth.yaml --auth_key=${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} |\
 crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
