#!/bin/bash

export net=wamr
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/db_cluster_validation/${net}_json.log
export cache_file=~/db_cluster_validation/cache_${net}_${NOW}.txt

download_${net} -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file} | crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca/crmp:5433 -N ${net} -L ~/logging.yaml --log_filename ${log_file}
