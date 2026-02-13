# We will:
# 	•	Chunk outside (never millions at once)
# 	•	Open a fresh DB session per chunk
# 	•	Commit per chunk
# 	•	Rollback safely on error
# 	•	Log progress so you can resume

# This guarantees:
# ✔ bounded memory
# ✔ no giant transactions
# ✔ recoverability
# ✔ stable connections

import sqlalchemy as sa
from sqlalchemy.orm import Session
import logging
from math import ceil
from crmprtd import setup_logging
from crmprtd.infer import infer
from crmprtd.align import align
from crmprtd.insert import insert
from crmprtd.more_itertools import tap, log_progress
from crmprtd.constants import InsertStrategy


def safe_insert_rows(
    all_rows,
    log_file_path,
    db_url,
    chunk_size=5000,
    insert_strategy=InsertStrategy.BULK,
    bulk_chunk_size=1000,
    sample_size=50,
    network='_test',
    is_diagnostic=False,
):
    """
    Safely insert very large numbers of rows by chunking, committing per chunk,
    and isolating DB sessions.
    """

    total = len(all_rows)
    n_chunks = ceil(total / chunk_size)

    print(f"🚀 Starting insert: {total} rows in {n_chunks} chunks")

    for i in range(n_chunks):
        start = i * chunk_size
        end = min(start + chunk_size, total)
        chunk = all_rows[start:end]

        print(f"➡️  Processing rows {start}–{end-1}")

        engine = sa.create_engine(db_url, echo=False)
        session = Session(engine)

        try:
            # Setup logging per chunk
            setup_logging(None, log_file_path, 'tongli1997@uvic.ca', 'INFO', network)
            log = logging.getLogger(__name__)

            # Infer
            infer(session, chunk, diagnostic=is_diagnostic)

            # Align + filter (generator to avoid memory spike)
            observations = []
            for row in chunk:
                obs = align(session, row, is_diagnostic)
                if obs is not None:
                    observations.append(obs)

            # Insert
            insert(
                session,
                observations,
                strategy=insert_strategy,
                bulk_chunk_size=bulk_chunk_size,
                sample_size=sample_size,
            )

            session.commit()

            log.info(f"✅ Inserted rows {start}–{end-1}")
            print(f"✅ Inserted rows {start}–{end-1}")

        except Exception as e:
            session.rollback()
            print(f"❌ Failed rows {start}–{end-1}: {e}")
            raise

        finally:
            session.close()
            engine.dispose()




def insert_or_update_rows(
    observations,
    db_url,
    log_file_path,
    network_name='_test',
    chunk_size=5000,
    bulk_chunk_size=1000,
    sample_size=50,
    is_diagnostic=False
):
    """
    Insert new rows or update existing ones if values differ.

    Parameters
    ----------
    observations : list of Row
        List of CRMP Row objects to process.
    db_url : str
        SQLAlchemy database URL.
    log_file_path : str
        Path to the log file.
    network_name : str
        Network name for logging.
    chunk_size : int
        Number of rows to process per chunk.
    bulk_chunk_size : int
        Bulk insert chunk size inside safe_insert_rows.
    sample_size : int
        Sample size for insert strategy.
    is_diagnostic : bool
        If True, logs details instead of inserting.
    """

    # Create engine and session
    engine = sa.create_engine(db_url, echo=False)
    session = Session(engine)

    # Setup logging
    setup_logging(None, log_file_path, 'tongli1997@uvic.ca', 'INFO', network_name)
    log = logging.getLogger(__name__)

    rows_to_insert = []

    try:
        for obs in observations:
            existing = session.query(ObsRaw).filter_by(
                station_id=obs.station_id,
                variable_name=obs.variable_name,
                obs_time=obs.time   # match the actual column name
            ).first()

            if existing:
                if pd.isna(existing.val) or existing.val != obs.val:
                    existing.val = obs.val  # update existing
                    log.info(f"Updated: {obs.station_id}, {obs.variable_name}, {obs.time}")
                else:
                    log.info(f"Skipped (same value): {obs.station_id}, {obs.variable_name}, {obs.time}")
            else:
                rows_to_insert.append(obs)

        # Bulk insert new rows
        if rows_to_insert:
            safe_insert_rows(
                all_rows=rows_to_insert,
                log_file_path=log_file_path,
                db_url=db_url,
                chunk_size=chunk_size,
                insert_strategy=InsertStrategy.BULK,
                bulk_chunk_size=bulk_chunk_size,
                sample_size=sample_size,
                network=network_name,
                is_diagnostic=is_diagnostic
            )

        session.commit()
        log.info("✅ All observations processed successfully")

    except Exception as e:
        session.rollback()
        print(f"❌ Error processing observations: {e}")
        raise

    finally:
        session.close()
        engine.dispose()