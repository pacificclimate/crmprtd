import logging
import os
import sqlalchemy as sa
from sqlalchemy.orm import Session
from crmprtd import setup_logging
from crmprtd.infer import infer
from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd.more_itertools import tap, log_progress
from crmprtd.constants import InsertStrategy

def insert_rows(
    rows_insert,
    log_file_path,
    db_url,
    network='_test',
    insert_strategy=InsertStrategy.BULK,
    bulk_chunk_size=1000,
    sample_size=50,
    is_diagnostic=False
):
    """
    Insert rows into the CRMP database, including logging, infer, align, and insert steps.

    Parameters
    ----------
    rows_insert : list
        List of Row objects to insert.
    log_file_path : str
        Path to the log file.
    db_url : str
        SQLAlchemy database URL.
    network : str
        Network name for logging and insert metadata.
    insert_strategy : InsertStrategy
        Strategy for inserting (default: BULK).
    bulk_chunk_size : int
        Chunk size for BULK inserts.
    sample_size : int
        Sample size for insert checks.
    is_diagnostic : bool
        If True, logs full observation objects instead of inserting.
    """
    # Setup logging
    setup_logging(None, log_file_path, 'tongli1997@uvic.ca', 'DEBUG', network)
    log = logging.getLogger(__name__)
    log.info("Logging system initialized")
    
    # Connect to DB
    engine = sa.create_engine(db_url, echo=False)
    session = Session(engine)

    # Infer
    infer(session, rows_insert, diagnostic=is_diagnostic)

    # Align + filter
    log.info("Align + filter: start")
    observations = list(
        filter(
            None,
            tap(
                log_progress(
                    (1, 2, 5, 10, 20, 50, 100, 200, 500, 1000, 5000),
                    "align progress: {count}",
                    log.info,
                ),
                (align(session, row, is_diagnostic) for row in rows_insert),
            ),
        )
    )
    log.info("Align + filter: done")
    log.info(f"Count of observations to process: {len(observations)}")

    if is_diagnostic:
        for obs in observations:
            log.info(obs)
        return None

    # Insert
    log.info("Insert: start")
    results = insert(
        session,
        observations,
        strategy=insert_strategy,
        bulk_chunk_size=bulk_chunk_size,
        sample_size=sample_size,
    )
    log.info("Insert: done")
    log.info("Data insertion results", extra={"results": results, "network": network})
    return results


