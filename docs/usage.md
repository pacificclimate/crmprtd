## Usage

The most common usage pattern for package `crmprtd` is to configure cron to run a number of scripts on an hourly or daily basis.

Some data sources require authentication. For most scripts, credentials can be provided as command line arguments, or, preferably, entries in a yaml config file. A sample version of this file can be seen [here](https://github.com/pacificclimate/crmprtd/blob/master/auth.yaml). The location of the config is passed with the `--auth` argument and the key with the `--auth_key` argument.

### Performing the download-cache-process sequence

Although the three steps of downloading data, caching it, and processing it can
be invoked as separate operations, the most common and convenient way to perform
this sequence is the console script `crmprtd_pipeline`.

The script takes a network argument and a handful of other arguments, formulates
appropriate command lines for each step, and causes them to be executed.

Here is the help from `crmprtd_pipeline`:

```text
(crmprtd) rglover@pcic-3002:~/code/crmprtd$ crmprtd_pipeline -h
usage: crmprtd_pipeline [-h] [--version]
                        [-D {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}]
                        [--dry_run] -N
                        {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}
                        [-T TAG] [--log_filename LOG_FILENAME]
                        [--cache_filename CACHE_FILENAME]
                        [-c CONNECTION_STRING]

The download-cache-process pipeline. Starts a pipeline of subprocesses
running, in sequence, (1) script crmprtd_download, (2) an optional cache
step (tee), and (3) the script crmprtd_process. The third subprocess is
optional, depending on arguments provided to this command. Arguments to
each script in the pipeline are provided as appropriate, depending on the
network(s) and other arguments to this command.

optional arguments:
  -h, --help            show this help message and exit
  --version             Show version number and exit
  -D {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}, --describe {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}
                        Describe a network name or alias
  --dry_run             Do a dry run. This prints to stdout all commands
                        and their arguments (sanitized) that would be run.
                        The commands are not actually run.
  -N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}, --network {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,bch,hourly_swobml2,ytnt}
                        Network identifier (a network name or network
                        alias) from which to download observations. A
                        network alias can stand for one or more individual
                        networks (e.g., 'ytnt' stands for many networks).
  -T TAG, --tag TAG     Tag for forming default names for log and cache
                        files
  --log_filename LOG_FILENAME
                        Filename for log file. (If omitted, use default
                        filename generated from network name, tag, and
                        other parameters.)
  --cache_filename CACHE_FILENAME
                        Filename for cache file. (If omitted, use default
                        filename generated from network name, tag, and
                        other parameters.)
  -c CONNECTION_STRING, --connection_string CONNECTION_STRING
                        Connection string for target database. If absent,
                        processing step is not performed.

Hints: (1) Use the -D/--describe <name> option to see the network(s)
designated by <name>, which can be either a single network name or an
alias, which designates one or more networks (e.g., ytnt). (2) Arguments
generated for each step of the pipeline depend in a complicated way on the
network and other arguments provided to this command. Use the --dry_run
option to print to stdout the command pipeline(s) that would be run using
the arguments you provide to this command. It is informative, and each line 
can if you wish be be pasted into a Linux command line and will have the same 
effect as running this script, except that database passwords are sanitized 
from the output.
```

The `--dry_run` option is useful to see what arguments are fed to the scripts
in the pipeline. Example:

```text
(crmprtd) rglover@pcic-3002:~/code/crmprtd$ crmprtd_pipeline --dry_run -N ec -F daily -T tag -c DSN
crmprtd_download -N ec -p bc -F daily -L ~/logging.yaml --log_filename ~/ec/logs/tag_bc_daily_json.log | tee ~/ec/cache/tag_daily_bc_2023-01-19T16:54:04.xml | crmprtd_process -N ec -c DSN -L ~/logging.yaml --log_filename ~/ec/logs/tag_bc_daily_json.log
crmprtd_download -N ec -p yt -F daily -L ~/logging.yaml --log_filename ~/ec/logs/tag_yt_daily_json.log | tee ~/ec/cache/tag_daily_yt_2023-01-19T16:54:04.xml | crmprtd_process -N ec -c DSN -L ~/logging.yaml --log_filename ~/ec/logs/tag_yt_daily_json.log
```

A typical use of this script is:

```text
$ crmprtd_pipeline -N ytnt -T metnorth -c postgresql://user:password@db.uvic.ca/metnorth
```

### Downloading data

Script `crmprtd_download -N [network_name]` downloads data for the named network.  
The standard output stream of this script can be redirected into a file or piped
into `crmprtd_process`.  Script `crmprtd_process` read data from the standard input
stream runs it through a series of formatting changes and checks before inserting
the data into the database.

A list of all available network modules can be found in the online help for `crmprtd_process`:

```bash
(env) james@basalt:~/code/git/crmprtd$ crmprtd_process -h
usage: crmprtd_process [-h] -c CONNECTION_STRING [-D]
                       [--sample_size SAMPLE_SIZE]
                       [-N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}]
                       [-L LOG_CONF] [-l LOG_FILENAME]
                       [-o {DEBUG,INFO,WARNING,ERROR,CRITICAL}]
                       [-m ERROR_EMAIL]

optional arguments:
...
  -N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}, --network {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,ec,moti,wamr,wmb}
                        The network from which the data is coming from. The
                        name will be used for a dynamic import of the module's
                        normalization function.
```

### Input/Output Streams

Connecting the I/O of the download scripts to cache files and the processing scripts is as easy as using unix pipes and I/O redirects. For example, fetching the SWOB-ML for the BC Forestry data and processing it, looks like this:

```bash
crmprtd_download -N bc_forestry > cache_filename
crmprtd_process -N bc_forestry < cache_filename
# Or
crmprtd_download -N bc_forestry | crmprtd_process -N bc_forestry
# Or
crmprtd_download -N bc_forestry | tee cache_filename | crmprtd_process -N bc_forestry
```

More generally:

```bash
crmprtd_download -N [network_name] > cache_filename
crmprtd_process -N [network_name] < cache_filename
# Or
crmprtd_download -N [network_name] | crmprtd_process -N [network_name]
# Or
crmprtd_download -N [network_name] | tee cache_filename | crmprtd_process -N [network_name]
```

### Cron usage

Typical usage is to set up a cron job that invokes an execution script at the
appropriate times. Below is an example _partial_ crontab using the above
scripts. Notes:

- This crontab portion is taken from actual usage at the time of writing.
- This is only _part_ of the complete crontab. It omits some legacy job lines
  that will be replaced in future updates.
- It demonstrates its use targeting some test/transitional databases.
- The pattern below -- using variables defined in the crontab, to factor out
  repeated elements -- is recommended.
- Different database targets use different tags to
  distinguish the cache and log files produced for each target.

```text
CRMP2_PATH=~/env_4.2.0/bin:~/bin:/usr/local/bin:/usr/bin:/bin
CRMP2_DB=postgresql://crmprtd@dbtest01.pcic.uvic.ca:5433/crmp2
CRMP2_TAG=crmp2

METNORTH2_PATH=~/env_4.2.0/bin:~/bin:/usr/local/bin:/usr/bin:/bin
METNORTH2_DB=postgresql://crmprtd@metnorth.pcic.uvic.ca:5433/metnorth2
METNORTH2_TAG=metnorth2

# CRMP2

@hourly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N hourly_swobml2 -c $CRMP2_DB" | batch
@weekly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N wamr -c $CRMP2_DB" | batch
40 4 * * *                      echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N wmb -c $CRMP2_DB" | batch
@hourly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N ec -F hourly -c $CRMP2_DB" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N ec -F daily -c $CRMP2_DB" | batch
30 * * * *                      echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N moti -c $CRMP2_DB" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N crd -c $CRMP2_DB" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N bch -c $CRMP2_DB" | batch
0 7 1,15,28,29,30,31 * *        echo "bash /home/crmprtd/code/crmp_fanslow/read_NRT_ASP_snow_pillow_data_by_variable.sh" | batch
30 2 27-31,1-4 * *              echo "bash /home/crmprtd/code/crmp_fanslow/ec_csv_runner.sh" | batch 
@daily                          echo "psql -h db.pcic.uvic.ca -U crmprtd -d crmp2 -p 5433 -f ~/bin/update_matviews_lazy.sql" | batch
@monthly                        echo "PATH=$CRMP2_PATH manage-views.py -d $CRMP2_DB refresh all" | batch

# Metnorth2

@hourly                         echo "PATH=$METNORTH2_PATH crmprtd_pipeline -T $METNORTH2_TAG -N ytnt -c $METNORTH2_DB" | batch
# I think we need at least the following also. Can we omit the other 2 fanslow scripts as I have done?
@daily                          echo "psql -h dbnorth.pcic.uvic.ca -U crmprtd -d metnorth2 -p 5433 -f ~/bin/update_matviews_lazy.sql" | batch
@monthly                        echo "PATH=$METNORTH2_PATH manage-views.py -d $METNORTH2_DB refresh all" | batch
```

### Logging

One thing to be aware of when using pipes and stdout is that you need to ensure that no logging or debugging output from the download script goes to standard out. The default console logger sends logging output to the standard error stream. However, this is configurable, so the user must take care to *not* configure the logging output to go to standard out, lest it get mixed up with the data output stream.

