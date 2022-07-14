from io import BytesIO

from crmprtd.bc_hydro.normalize import normalize

import pytest

simple_data = b"""STN	DATE		MAX T 	MIN T	PREC	
AKI	2020/09/01	15.1	7.0	0.1	
AKI	2020/09/02	15.2	5.8	0.0	
AKI	2020/09/03	15.1	3.4	0.0	
AKI	2020/09/04	16.5	7.0	0.2	
AKI	2020/09/05	18.1	7.0	0.3	
AKI	2020/09/06	17.2	2.7	0.0	
AKI	2020/09/07	16.6	-1.6	0.0	
AKI	2020/09/08	18.7	4.8	0.0	
AKI	2020/09/09	23.5	4.5	0.0	

"""  # noqa

extended_data = b"""Colpitti Ck
STN	Date/Time       	PREC_HR_TTL_VAL	PREC_HR_TTL_VAL_QC	PREC_HR_TTL_VAL_Note	PREC_BEST_HR_TTL	PREC_BEST_HR_TTL_QC	PREC_BEST_HR_TTL_Note	TEMP_INST_VAL	TEMP_INST_VAL_QC	TEMP_INST_VAL_Note	SWE_INST_VAL	SWE_INST_VAL_QC	SWE_INST_VAL_Note	
CPI	2020/09/19 14:00	+	+	+	+	+	+	8.3	190	+	-1.0	190	+	
CPI	2020/09/19 14:15	+	+	+	+	+	+	8.0	190	+	-1.0	190	+	
CPI	2020/09/19 14:30	+	+	+	+	+	+	8.1	190	+	-1.0	190	+	
CPI	2020/09/19 14:45	+	+	+	+	+	+	7.4	190	+	-1.0	190	+	
CPI	2020/09/19 15:00	0.2	50	+	0.2	50	+	7.4	190	+	0.0	190	+	
CPI	2020/09/19 15:15	+	+	+	+	+	+	7.7	190	+	-1.0	190	+	
CPI	2020/09/19 15:30	+	+	+	+	+	+	7.4	190	+	0.0	190	+	
CPI	2020/09/19 15:45	+	+	+	+	+	+	6.7	190	+	0.0	190	+	

"""  # noqa

good_data = (
    simple_data,
    extended_data,
    simple_data + extended_data,
    simple_data + simple_data + extended_data,
)


@pytest.mark.parametrize(("lines"), good_data)
def test_normalize_good_data(lines):
    rows = [row for row in normalize(BytesIO(lines))]

    assert len(rows) > 0
    for row in rows:
        assert row.val is not None


def test_normalize_no_data():
    """+s should be skipped so this example should generate no rows"""
    rows = normalize(
        BytesIO(
            b"""Colpitti Ck
STN	Date/Time       	PREC_HR_TTL_VAL	PREC_HR_TTL_VAL_QC
CPI	2020/09/19 14:00	+	+
CPI	2020/09/19 14:00	+	+

"""
        )
    )
    with pytest.raises(StopIteration):
        next(rows)


def test_normalize_bad_data():
    rows = normalize(BytesIO(b"""bad data %^#&@*$%%"""))
    with pytest.raises(StopIteration):
        next(rows)


def test_normalize_backwards_data():
    """The first line is ignored since there are no variable names
    available, but we should get 4 values from the second line
    """
    rows = normalize(
        BytesIO(
            b"""Colpitti Ck
CPI	2020/09/19 14:00	+	+	+	+	+	+	8.3	190	+	-1.0	190	+	
STN	Date/Time       	PREC_HR_TTL_VAL	PREC_HR_TTL_VAL_QC	PREC_HR_TTL_VAL_Note	PREC_BEST_HR_TTL	PREC_BEST_HR_TTL_QC	PREC_BEST_HR_TTL_Note	TEMP_INST_VAL	TEMP_INST_VAL_QC	TEMP_INST_VAL_Note	SWE_INST_VAL	SWE_INST_VAL_QC	SWE_INST_VAL_Note	
CPI	2020/09/19 14:30	+	+	+	+	+	+	8.1	190	+	-1.0	190	+	
 """
        )
    )
    n = sum([1 for _ in rows])
    assert n == 4
