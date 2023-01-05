#!/bin/bash

for network in 'EC_raw' 'FLNRO-WMB' 'MoTIe' 'ENV-AQN' 'FLNRO-FERN' 'BCH'; do
    echo "Insertions into ${network} yesterday:";
    psql -h monsoon -U crmprtd -d crmp -c "select count(*) from obs_raw natural join meta_history natural join meta_station natural join meta_network where network_name = '${network}' and obs_time between DATE 'yesterday' and DATE 'today';";
done;
