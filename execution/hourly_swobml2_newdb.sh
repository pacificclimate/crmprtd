#!/bin/bash
# set up for access to new DB.PCIC.UVIC.CA

export TIME=$(date -u "+%Y/%m/%d %H:00:00" -d "last hour");
#export networks=bc_env_aq bc_env_snow bc_forestry bc_tran
#export networks=bc_env_snow bc_tran
export networks="bc_env_snow bc_forestry bc_tran dfo_ccg_lighthouse"

for net in ${networks}; do
    export log_file=~/${net}/logs/${net}_json.log
    export cache_file=~/${net}/cache/${net}_$(date +'%Y-%m-%dT%H:%M:%S').xml
    echo "download_${net} -L logging.yaml --log_filename ${log_file} -d \"${TIME}\" | tee ${cache_file} |\
      crmprtd_process -c postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp -N ${net} -L logging.yaml --log_filename ${log_file}" | batch
done


# As of April 14, 2022 The YT/NWT networks don't have their variables
# in the database, so we can't insert the data, but we can at least
# download the cache file and insert them later.

export networks="nt_forestry nt_water yt_gov yt_water yt_avalanche yt_firewx"
for net in ${networks}; do
    export log_file=~/${net}/logs/${net}_json.log
    export cache_file=~/${net}/cache/${net}_$(date +'%Y-%m-%dT%H:%M:%S').xml
    echo "download_${net} -L ~/logging.yaml --log_filename ${log_file} -d \"${TIME}\" | tee ${cache_file} |\
       crmprtd_process -c postgresql://crmprtd@dbnorth/metnorth -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch

done
