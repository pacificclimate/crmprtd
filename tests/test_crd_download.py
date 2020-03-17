import pytest

from dateutil.parser import parse

from crmprtd.crd.download import verify_dates, make_url


@pytest.mark.parametrize(("sdate", "edate"), [
    ("2020/06/06", "2020/06/06"),
    ("2020/01/01", "2019/12/31"),
    ("2010/01/01", "2010/01/29 01:00:00"),
    ("2011/11/11", None),
    (None, "2011/11/11"),
])
def test_verify_dates(sdate, edate):
    if sdate:
        sdate = parse(sdate)
    if edate:
        edate = parse(edate)
    with pytest.raises(AssertionError):
        verify_dates(sdate, edate)


@pytest.mark.parametrize(("sdate", "edate", "expected"), [
    (None, None, "https://webservices.crd.bc.ca/weatherdata/PCIC/"),
    (parse("2019/06/06"), parse("2019/06/07"),
      "https://webservices.crd.bc.ca/weatherdata/PCIC/201906060000-201906070000")
])
def test_make_url(sdate, edate, expected):
    result = make_url("PCIC", sdate, edate)
    assert result == expected
    #"https://webservices.crd.bc.ca/weatherdata/{client_id}/{time_range}"
