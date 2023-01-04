#!/bin/bash

export net=crd
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${net}_json.log
export cache_file=~/${net}/cache/${net}_${NOW}.txt

echo "download_${net} --auth_fname ~/.rtd_auth.yaml --auth_key=${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} | crmprtd_process -c postgresql://crmprtd@monsoon/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
