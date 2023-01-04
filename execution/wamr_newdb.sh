#!/bin/bash

export net=wamr
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${net}_json.log
export cache_file=~/${net}/cache/${net}_${NOW}.txt

echo "download_${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} |\
  crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
