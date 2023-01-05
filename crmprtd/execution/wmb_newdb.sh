#!/bin/bash

# Distinguishes cache and log file names.
tag="$1"

export net=wmb
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

# TODO: Is `mof` right??? Why not `${net}`?
export log_file=~/${net}/logs/{tag}_mof_json.log
export cache_file=~/${net}/download/${tag}_{net}_${NOW}.txt

echo "download_${net} --auth_fname ~/.rtd_auth.yaml --auth_key=${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} |\
 crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
