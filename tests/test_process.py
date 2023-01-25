import re
import pytz
import pytest
import logging
from datetime import datetime
from pkg_resources import resource_filename

from pycds import Network, Variable, Obs
from crmprtd.download_utils import verify_date

# from crmprtd.process import process, main
import crmprtd.process


def get_num_obs_to_insert(records):
    r = re.compile(r".*Count of observations to insert:\s*(\d+)")
    for record in records:
        m = r.match(str(record))
        if m:
            return int(m.group(1))
    return None


def get_num_obs_inserted(records):
    r = re.compile(r".*Successfully inserted observations:\s*(\d+)")

    def get_per_rec(record):
        m = r.match(str(record))
        return int(m.group(1)) if m else 0

    return sum(get_per_rec(record) for record in records)


def num_observations_in_db(session):
    return session.query(Obs).count()


@pytest.mark.parametrize(
    # There are 2510 observations in the test data file, all dated 2022-06-17.
    # Of these, 2360 are unique. Those should be inserted; the 150 duplicates should
    # be skipped.
    ("start_date", "end_date", "expected_num_inserts"),
    [
        ("2022/06/1", "2022/06/18", 2360),
        ("June 18", None, 0),
        (None, "June 17 2022 10am", 0),
        (None, None, 2360),
    ],
)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_process_by_date(
    start_date, end_date, expected_num_inserts, monkeypatch, caplog, crmp_session
):
    # Restrict the logging to just what is important to this test.
    caplog.set_level(logging.WARNING, "sqlalchemy.engine")
    caplog.set_level(logging.DEBUG, "crmprtd")

    utc = pytz.utc

    start_date = utc.localize(verify_date(start_date, datetime.min, "start date"))
    end_date = utc.localize(verify_date(end_date, datetime.max, "end date"))

    # Insert the network required in the test data
    network = Network(name="FLNRO-WMB")
    crmp_session.add(network)

    # Insert the variables required in the test data.
    # Note: Infer mode does not insert variables, so we have to do it manually here,
    # parallelling what we do in real usage.
    crmp_session.add_all(
        [
            Variable(
                network=network,
                name=name,
                unit=unit,
                standard_name="dummy",
                cell_method="dummy",
                display_name="dummy",
            )
            for name, unit in (
                ("dwpt_temp", "°C"),
                ("pcpn_amt_pst1hr", "mm"),
                ("rnfl_amt_pst6hrs", "mm"),
                ("air_temp", "°C"),
                ("snw_dpth", "cm"),
                ("rnfl_amt_pst24hrs", "mm"),
                ("rnfl_amt_pst3hrs", "mm"),
                ("rnfl_amt_pst1hr", "mm"),
                ("avg_wnd_spd_10m_pst10mts", "km/h"),
                ("avg_wnd_dir_10m_pst10mts", "°"),
                ("rel_hum", "%"),
                ("cum_pcpn_gag_wt", "kg/m²"),
            )
        ]
    )
    crmp_session.commit()

    num_obs_in_db_before = num_observations_in_db(crmp_session)

    # Set up input from test data file.
    forestry_data = open(resource_filename("crmprtd", "data/forestry_data.xml"))
    monkeypatch.setattr("sys.stdin", forestry_data)

    crmprtd.process.process(
        connection_string=crmp_session.get_bind().url,
        sample_size=50,
        network="bc_forestry",
        start_date=start_date,
        end_date=end_date,
        is_diagnostic=False,
        do_infer=True,
    )

    num_obs_in_db_after = num_observations_in_db(crmp_session)
    num_obs_inserted_in_db = num_obs_in_db_after - num_obs_in_db_before
    log_num_obs_inserted = get_num_obs_inserted(caplog.records)

    assert num_obs_inserted_in_db == expected_num_inserts
    assert log_num_obs_inserted == expected_num_inserts


@pytest.mark.parametrize(
    "connection_string, sample_size, network, start_date, end_date, infer, diagnostic",
    [
        ("DSN", 99, "crd", "2000-01-01", "2000-02-01", False, False),
    ],
)
def test_main(
    connection_string,
    sample_size,
    network,
    start_date,
    end_date,
    infer,
    diagnostic,
    mocker,
):
    args = []
    if connection_string is not None:
        args += f" -c {connection_string}".split()
    if sample_size is not None:
        args += f"--sample_size {sample_size}".split()
    if network is not None:
        args += f"-N {network}".split()
    if start_date is not None:
        args += f"-S {start_date}".split()
    if end_date is not None:
        args += f"-E {end_date}".split()
    if infer:
        args += f"-I".split()
    if diagnostic:
        args += f"-D".split()

    pp = mocker.patch("crmprtd.process.process")

    crmprtd.process.main(args)

    assert pp.called_with(
        connection_string=connection_string,
        sample_size=sample_size,
        network=network,
        start_date=pytz.utc.localize(verify_date(start_date, datetime.min)),
        end_date=pytz.utc.localize(verify_date(end_date, datetime.max)),
        is_diagnostic=diagnostic,
        do_infer=infer,
    )
