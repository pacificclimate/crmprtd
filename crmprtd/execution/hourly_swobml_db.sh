#!/bin/bash

export TIME=$(date -u "+%Y/%m/%d %H:00:00" -d "last hour");
#export networks="bc_env_snow bc_forestry bc_tran nt_forestry nt_water yt_gov yt_water"
export networks="bc_env_snow bc_forestry bc_tran"
#export networks="nt_forestry nt_water yt_gov yt_water"

for net in ${networks}; do
    export log_file=~/db_cluster_validation/${net}_json.log
    export cache_file=~/db_cluster_validation/${net}_$(date +'%Y-%m-%dT%H:%M:%S').xml
    download_${net} -L ~/logging.yaml --log_filename ${log_file} -d "${TIME}" | tee ${cache_file} | crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L ~/logging.yaml --log_filename ${log_file}
done
