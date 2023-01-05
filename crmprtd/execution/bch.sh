#!/bin/bash

# Distinguishes cache and log file names.
tag="$1"

# Target database DSN, e.g., postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp
# (Not currently used.)
db="$2"

export net=bc_hydro
export NOW=$(date +'%Y-%m-%dT%H:%M:%S')

export log_file=~/${net}/logs/${tag}_{net}_json.log
export cache_file=~/${net}/cache/${tag}{net}_${NOW}.txt

echo "download_${net} -f sftp2.bchydro.com -F pcic -S ~/.ssh/id_rsa -L ~/logging.yaml --log_filename ${log_file} | tee ${cache_file}" | batch
