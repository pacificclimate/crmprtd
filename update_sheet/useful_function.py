from sqlalchemy import text

def delete_station(session, station_id, preview=True):
    """
    Delete a station and all related data from:
        - obs_raw
        - meta_history
        - meta_station

    Parameters
    ----------
    session : SQLAlchemy session
    station_id : int
        Station ID to delete.
    preview : bool (default=True)
        If True: runs inside a SAVEPOINT and rolls back (no changes committed)
        If False: commits actual deletion.
    """

    delete_obs = text("""
        DELETE FROM obs_raw
        WHERE history_id IN (
            SELECT history_id FROM meta_history WHERE station_id = :sid
        );
    """)

    delete_history = text("""
        DELETE FROM meta_history
        WHERE station_id = :sid;
    """)

    delete_station = text("""
        DELETE FROM meta_station
        WHERE station_id = :sid;
    """)

    if preview:
        print(f"\n=== PREVIEW DELETE for station_id={station_id} ===")
        with session.begin_nested():   # SAVEPOINT
            session.execute(delete_obs, {"sid": station_id})
            session.execute(delete_history, {"sid": station_id})
            session.execute(delete_station, {"sid": station_id})

            # Show remaining row (should be none if deletion ran)
            remaining = session.execute(
                text("SELECT * FROM meta_station WHERE station_id = :sid"),
                {"sid": station_id}
            ).fetchall()

            print("Remaining meta_station rows after deletion (preview):")
            print(remaining)

            print("\nPreview complete — NO CHANGES saved.\n")
            # rollback happens automatically when exiting begin_nested()
        return

    else:
        print(f"\n=== REAL DELETE for station_id={station_id} ===")
        with session.begin():   # real transaction
            session.execute(delete_obs, {"sid": station_id})
            session.execute(delete_history, {"sid": station_id})
            session.execute(delete_station, {"sid": station_id})

        print("✔ Deletion committed.\n")

        # Double-check
        remaining = session.execute(
            text("SELECT * FROM meta_station WHERE station_id = :sid"),
            {"sid": station_id}
        ).fetchall()

        print("Remaining rows (should be empty):", remaining)

### case
delete_station(session, 12063, preview=True)   # dry run
delete_station(session, 12063, preview=False)  # real delete