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
(env_4.3.1) [crmprtd@crmprtd ~]$ crmprtd_pipeline -h
usage: crmprtd_pipeline [-h] [--version]
                        [-D {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}]
                        [--dry_run] -N
                        {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}
                        [-T TAG] [--log_filename LOG_FILENAME]
                        [--cache_filename CACHE_FILENAME] [-c CONNECTION_STRING]

The download-cache-process pipeline. Starts a pipeline of subprocesses running, in sequence,
(1) script crmprtd_download, (2) an optional cache step (tee), and (3) the script
crmprtd_process. The third subprocess is optional, depending on arguments provided to this
command. Arguments to each script in the pipeline are provided as appropriate, depending on
the network(s) and other arguments to this command.

optional arguments:
  -h, --help            show this help message and exit
  --version             Show version number and exit
  -D {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}, --describe {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}
                        Describe a network name or alias
  --dry_run             Do a dry run. This prints to stdout all commands and their arguments
                        (sanitized) that would be run. The commands are not actually run.
  -N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}, --network {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test,bch,hourly_swobml2,ytnt}
                        Network identifier (a network name or network alias) from which to
                        download observations. A network alias can stand for one or more
                        individual networks (e.g., 'ytnt' stands for many networks).
  -T TAG, --tag TAG     Tag for forming default names for log and cache files
  --log_filename LOG_FILENAME
                        Filename for log file. (If omitted, use default filename generated
                        from network name, tag, and other parameters.)
  --cache_filename CACHE_FILENAME
                        Filename for cache file. (If omitted, use default filename generated
                        from network name, tag, and other parameters.)
  -c CONNECTION_STRING, --connection_string CONNECTION_STRING
                        Connection string for target database. If absent, processing step is
                        not performed.

Hints: (1) Use the -D/--describe <name> option to see the network(s) designated by <name>,
which can be either a single network name or an alias, which designates one or more networks
(e.g., ytnt). (2) Arguments generated for each step of the pipeline depend in a complicated
way on the network and other arguments provided to this command. Use the --dry_run option to
print to stdout the command pipeline(s) that would be run using the arguments you provide to
this command. It is informative, and each line can if you wish be be pasted into a Linux
command line and will have the same effect as running this script, except that database
passwords are sanitized from the output.
```

The `--dry_run` option is useful to see what arguments are fed to the scripts
in the pipeline. Example:

```text
(env_4.3.1) [crmprtd@crmprtd ~]$ crmprtd_pipeline --dry_run -N ec -F daily -T tag -c DSN
crmprtd_download -N ec -p bc -F daily -L ~/logging.yaml --log_filename ~/ec/logs/tag_bc_daily_json.log | tee ~/ec/cache/tag_daily_bc_2023-04-21T13:26:11.xml | crmprtd_process -N ec -c DSN -L ~/logging.yaml --log_filename ~/ec/logs/tag_bc_daily_json.log
crmprtd_download -N ec -p yt -F daily -L ~/logging.yaml --log_filename ~/ec/logs/tag_yt_daily_json.log | tee ~/ec/cache/tag_daily_yt_2023-04-21T13:26:11.xml | crmprtd_process -N ec -c DSN -L ~/logging.yaml --log_filename ~/ec/logs/tag_yt_daily_json.log
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
(env_4.3.1) [crmprtd@crmprtd ~]$ crmprtd_process -h
usage: crmprtd_process [-h] [--version] [-c CONNECTION_STRING] [-D]
                       [--sample_size SAMPLE_SIZE]
                       [-N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test}]
                       [-S START_DATE] [-E END_DATE] [-I] [-L LOG_CONF] [-l LOG_FILENAME]
                       [-o {DEBUG,INFO,WARNING,ERROR,CRITICAL}] [-m ERROR_EMAIL]

optional arguments:
  -h, --help            show this help message and exit
  --version             Show version number and exit
  -c CONNECTION_STRING, --connection_string CONNECTION_STRING
                        PostgreSQL connection string
  -D, --diag            Turn on diagnostic mode (no commits)
  --sample_size SAMPLE_SIZE
                        Number of samples to be taken from observations when searching for
                        duplicates to determine which insertion strategy to use
  -N {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test}, --network {bc_env_aq,bc_env_snow,bc_forestry,bc_tran,nt_forestry,nt_water,yt_gov,yt_water,yt_firewx,yt_avalanche,dfo_ccg_lighthouse,bc_hydro,crd,ec,moti,wamr,wmb,_test}
                        The network from which the data is coming from. The name will be used
                        for a dynamic import of the module's normalization function.
  -S START_DATE, --start_date START_DATE
                        Optional start time to use for processing (interpreted with
                        dateutil.parser.parse).
  -E END_DATE, --end_date END_DATE
                        Optional end time to use for processing (interpreted with
                        dateutil.parser.parse).
  -I, --infer           Run the 'infer' stage of the pipeline, which determines what metadata
                        insertions could be made basedon the observed data available
  -L LOG_CONF, --log_conf LOG_CONF
                        YAML file to use to override the default logging configuration
  -l LOG_FILENAME, --log_filename LOG_FILENAME
                        Override the default log filename
  -o {DEBUG,INFO,WARNING,ERROR,CRITICAL}, --log_level {DEBUG,INFO,WARNING,ERROR,CRITICAL}
                        Set log level: DEBUG, INFO, WARNING, ERROR, CRITICAL. Note that debug
                        output by default goes directly to file
  -m ERROR_EMAIL, --error_email ERROR_EMAIL
                        Override the default e-mail address to which the program should
                        report critical errors
```

### Input/Output Streams

Connecting the I/O of the download scripts to cache files and the processing 
scripts is as easy as using unix pipes and I/O redirects. 

Notes:
1. This is just an outline. Not all necessary arguments are shown.
2. The network name must be the same for both download and process. 
3. Command `crmprtd_pipeline` wraps this pattern and supplies required arguments.

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
CRMP2_PATH=~/env_4.3.1/bin:~/bin:/usr/local/bin:/usr/bin:/bin
CRMP2_DB='postgresql://crmprtd@db.pcic.uvic.ca:5433/crmp?keepalives=1&keepalives_idle=300&keepalives_interval=300&keepalives_count=9'
CRMP2_DB_PRIV='postgresql://crmp@db.pcic.uvic.ca:5433/crmp?keepalives=1&keepalives_idle=300&keepalives_interval=300&keepalives_count=9'
CRMP2_TAG=crmp

@hourly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N hourly_swobml2 -c $CRMP2_DB 2>> ~/error_logs/hourly_swobml2.out" | batch
#35 * * * *                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N hourly_swobml2 -c $CRMP2_DB 2>> ~/error_logs/hourly_swobml2.out" | batch
@weekly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N wamr -c $CRMP2_DB" | batch
40 4 * * *                      echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N wmb -c $CRMP2_DB" | batch
@hourly                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N ec -F hourly -c $CRMP2_DB" | batch
#35 * * * *                         echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N ec -F hourly -c $CRMP2_DB 2>> ~/error_logs/ec_hourly.out" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N ec -F daily -c $CRMP2_DB" | batch
50 * * * *                      echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N moti -c $CRMP2_DB" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N crd -c $CRMP2_DB" | batch
@daily                          echo "PATH=$CRMP2_PATH crmprtd_pipeline -T $CRMP2_TAG -N bc_hydro -c $CRMP2_DB" | batch
@daily                          echo "psql $CRMP2_DB -f ~/bin/update_matviews_lazy_879f0efa125f.sql 2>> ~/error_logs/update_matviews_lazy_879f0efa125f.out" | batch
@monthly                        echo "PATH=$CRMP2_PATH manage-views -d $CRMP2_DB_PRIV refresh all" | batch

# The following scripts need only be run once for all CRMP db instances; they 
# download data but do not process it. 
# They are commented out here because they are invoked elsewhere. If those 
# other invocations are removed, uncomment these.
#0 7 1,15,28,29,30,31 * *        echo "bash /home/crmprtd/code/crmp_fanslow/read_NRT_ASP_snow_pillow_data_by_variable.sh" | batch
#30 2 27-31,1-4 * *              echo "bash /home/crmprtd/code/crmp_fanslow/ec_csv_runner.sh" | batch 

# Metnorth @ rev 879f0efa125f

METNORTH2_PATH=~/env_4.2.1/bin:~/bin:/usr/local/bin:/usr/bin:/bin
METNORTH2_DB=postgresql://crmprtd@dbnorth.pcic.uvic.ca:5432/metnorth2
METNORTH2_TAG=metnorth2

@hourly                         echo "PATH=$METNORTH2_PATH crmprtd_pipeline -T $METNORTH2_TAG -N ytnt -c $METNORTH2_DB" | batch
```

### Logging

WARNING: You must ensure that no logging or debugging output from the download script goes to standard out. The default console logger sends logging output to the standard error stream. However, this is configurable, so the user must take care to *not* configure the logging output to go to standard out, lest it get mixed up with the data output stream.

