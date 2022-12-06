import re
import pytz
import pytest
import logging
from datetime import datetime
from pkg_resources import resource_filename

from pycds import Network, Variable
from crmprtd.download import verify_date
from crmprtd.process import process


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


@pytest.mark.parametrize(
    ("start_date", "end_date", "num_inserts"),
    [
        ("2022/06/1", "2022/06/18", 2510),
        ("June 18", None, 0),
        (None, "June 17 2022 10am", 0),
        (None, None, 2510),
    ],
)
@pytest.mark.filterwarnings("ignore::UserWarning")
def test_process_by_date(
    start_date, end_date, num_inserts, monkeypatch, caplog, crmp_session
):
    caplog.set_level(logging.INFO)

    utc = pytz.utc

    start_date = utc.localize(verify_date(start_date, datetime.min, "start date"))
    end_date = utc.localize(verify_date(end_date, datetime.max, "end date"))

    forestry_data = open(resource_filename("crmprtd", "data/forestry_data.xml"))
    monkeypatch.setattr("sys.stdin", forestry_data)

    # Insert the network in the test data
    network = Network(name="FLNRO-WMB")
    crmp_session.add(network)

    # Insert the variables required in the test data.
    # Note: Infer mode cannot insert variables, so we have to do it manually.
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

    process(
        connection_string=crmp_session.get_bind().url,
        sample_size=50,
        network="bc_forestry",
        start_date=start_date,
        end_date=end_date,
        is_diagnostic=False,
        do_infer=True,
    )

    num_obs_to_insert = get_num_obs_to_insert(caplog.records)
    num_obs_inserted = get_num_obs_inserted(caplog.records)
    print(
        f"num_obs_to_insert = {num_obs_to_insert}; "
        f"num_obs_inserted = {num_obs_inserted}"
    )
    assert num_obs_to_insert == num_inserts
    assert num_obs_inserted == num_obs_to_insert
