#!/bin/bash
# Arguments:
#   $1: override for location of crmprtd scripts

# If the first argument ($1) is supplied, put it on the front of PATH.
#[ ! -z "$1" ] && export PATH="$1:$PATH"

export PATH="~/env_4.0.0/bin:$PATH"
echo $PATH
crmprtd_process --version

export networks="nt_forestry nt_water yt_gov yt_water yt_avalanche yt_firewx"
for net in ${networks}; do
    export log_file=~/${net}/logs/${net}_json.log
    export cache_file=~/${net}/cache/${net}_$(date +'%Y-%m-%dT%H:%M:%S').xml
    echo "download_${net} -L ~/logging.yaml --log_filename ${log_file} -d \"${TIME}\" | tee ${cache_file} |\
       crmprtd_process -c postgresql://crmprtd@dbnorth/metnorth2 -N ${net} -L ~/logging.yaml --log_filename ${log_file}" | batch

done
