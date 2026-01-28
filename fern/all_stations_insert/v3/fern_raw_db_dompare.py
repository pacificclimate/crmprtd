from geopy.distance import geodesic
import numpy as np
import pandas as pd
from rapidfuzz import process
from rapidfuzz import fuzz
import sqlalchemy as sa
from sqlalchemy.orm import Session


###### Compare of the variables


from rapidfuzz import process, fuzz
import pandas as pd

def fuzzy_match_station_vars(raw_one, db_one, threshold=80):
    """
    Fuzzy match variable names between one raw station and its DB counterpart.

    Parameters
    ----------
    raw_one : pd.DataFrame
        Subset of raw_summary for one station (columns must include 'variable').
    db_one : pd.DataFrame
        Subset of db_summary for the same station (must include 'net_var_name').
    threshold : int
        Minimum matching score (0–100) to consider a match.

    Returns
    -------
    pd.DataFrame
        DataFrame with ['station_name', 'variable', 'db_var_match', 'score'].
    """

    if db_one.empty or raw_one.empty:
        return pd.DataFrame(columns=["station_name", "variable", "db_var_match", "score"])

    station_name = raw_one["station_name"].iloc[0]
    db_var_list = db_one["net_var_name"].dropna().tolist()

    results = []
    for file_var in raw_one["variable"]:
        match_result = process.extractOne(file_var, db_var_list, scorer=fuzz.ratio)
        if match_result:
            match, score, _ = match_result
        else:
            match, score = (None, 0)

        # Keep all results; you can filter later by score
        results.append({
            "station_name": station_name,
            "variable": file_var,
            "db_var_match": match if score >= threshold else None,
            "score": score
        })

    return pd.DataFrame(results)