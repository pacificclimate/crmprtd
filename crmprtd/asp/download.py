import logging

from crmprtd.download import main_download_by_station

log = logging.getLogger(__name__)

main = main_download_by_station(
    'http://bcrfc.env.gov.bc.ca/data/asp/realtime/data/{}.csv',
    'crmprtd.asp',
    'ENV-ASP',
    log
)

if __name__ == "__main__":
    main()
