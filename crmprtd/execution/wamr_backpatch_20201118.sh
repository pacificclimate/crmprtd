#!/bin/bash

year=$1
export net=wamr
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${net}_json.log
export cache_file=~/${net}/cache/${net}_${NOW}.txt
export PATH=$PATH:~/env_3.1.5/bin:~/bin:/usr/local/bin:/usr/bin:/bin

#echo "download_${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} | crmprtd_process -c postgres://crmprtd@monsoon/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch
#export LOGGING_ARGS="-L ~/logging.yaml"

echo "download_${net} -f ftp.env.gov.bc.ca -F /pub/outgoing/AIR/AnnualSummary/${year} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} | crmprtd_process -N ${net} -c postgresql://monsoon.pcic/crmp -L ~/logging.yaml --log_filename ${log_file}" | batch
