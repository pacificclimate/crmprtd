#!/bin/bash

export net=bc_hydro
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${net}_json.log
export cache_file=~/${net}/cache/${net}_${NOW}.txt

echo "download_${net} -f sftp2.bchydro.com -F pcic -S ~/.ssh/id_rsa -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file}" | batch
