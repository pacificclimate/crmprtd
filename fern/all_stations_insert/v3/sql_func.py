import sqlalchemy as sa
from sqlalchemy.orm import Session
import pandas as pd


def find_matching_station_in_db(engine, station_name, manual_corrections):
    """Try manual correction, then original name, then 'Wx'-stripped name."""
    # 1. Manual correction (exact match)
    if station_name in manual_corrections:
        corrected = manual_corrections[station_name]
        query = sa.text("""
            SELECT DISTINCT m.station_name
            FROM meta_history AS m
            JOIN meta_station AS s ON m.station_id = s.station_id
            WHERE m.station_name = :station_pattern and s.network_id = 11
            LIMIT 1;
        """)
        with engine.connect() as conn:
            res = conn.execute(query, {"station_pattern": corrected}).fetchone()
        if res:
            return res[0], True

    # 2. Try original name (ILIKE)
    query = sa.text("""
        SELECT DISTINCT m.station_name
        FROM meta_history AS m
        JOIN meta_station AS s ON m.station_id = s.station_id
        WHERE m.station_name ILIKE :station_pattern and s.network_id = 11
        LIMIT 1;
    """)
    with engine.connect() as conn:
        res = conn.execute(query, {"station_pattern": f"%{station_name}%"}).fetchone()
    if res:
        return res[0], False

    # 3. Try removing 'Wx' suffix (ILIKE)
    if station_name.endswith('Wx'):
        revised = station_name[:-2].strip()
        with engine.connect() as conn:
            res = conn.execute(query, {"station_pattern": f"%{revised}%"}).fetchone()
        if res:
            return res[0], False

    return None, None


def get_station_vars_time_from_db(engine, station_name, manual_corrections):
    """Return variables and units from database, applying name corrections."""
    matched_name, is_exact = find_matching_station_in_db(engine, station_name, manual_corrections)
    if matched_name is None:
        print(f"❌ No DB match for '{station_name}'")
        return None

    if is_exact:
        where_clause = "m.station_name = :station_pattern"
        pattern_param = matched_name
    else:
        where_clause = "m.station_name ILIKE :station_pattern"
        pattern_param = f"%{matched_name}%"

    query = sa.text(f"""
        SELECT 
            m.station_name,
            m.lat,
            m.lon,
            v.net_var_name, 
            v.unit,
            MIN(o.obs_time) AS earliest_time,
            MAX(o.obs_time) AS latest_time
        FROM obs_raw AS o
        JOIN meta_history AS m ON o.history_id = m.history_id
        JOIN meta_vars AS v ON o.vars_id = v.vars_id
        WHERE {where_clause}
        GROUP BY v.net_var_name, v.unit, m.station_name, m.lat, m.lon
        ORDER BY v.net_var_name;
    """)
    with engine.connect() as conn:
        df = pd.read_sql(query, conn, params={"station_pattern": pattern_param})

    df['matched_name'] = matched_name
    df['station_name'] = station_name


    print(f"✅ '{station_name}' matched DB as '{matched_name}' ({'exact' if is_exact else 'LIKE'}) "
          f"→ {len(df)} vars found.")

    df = df[['station_name', 'matched_name', 'lat', 'lon', 'net_var_name','unit', 'earliest_time', 'latest_time']]

    return df


def check_postgres_connection(user: str, hosts: str, dbname: str, echo: bool = False):
    """
    Connects to PostgreSQL (with optional failover hosts) and checks if the node is primary (read-write) or standby (read-only).

    Example:
        check_postgres_connection(
            user="tongli1997",
            hosts="pg01.pcic.uvic.ca,pg02.pcic.uvic.ca",
            dbname="crmp"
        )
    """
    conn_str = f"postgresql://{user}@{hosts}:5432/{dbname}?target_session_attrs=read-write"
    engine = sa.create_engine(conn_str, echo=echo)

    with Session(engine) as session:
        # Query host and port
        host, port = session.execute(sa.text("SELECT inet_server_addr(), inet_server_port();")).fetchone()

        # Check if server is in recovery mode
        is_in_recovery = session.execute(sa.text("SELECT pg_is_in_recovery();")).scalar()

        # Print summary
        print(f"Connected to host: {host}, port: {port}")
        if is_in_recovery:
            print("⚠️ Connected to a standby (read-only) node")
        else:
            print("✅ Connected to the primary (read-write) node")

        return {
            "host": host,
            "port": port,
            "is_primary": not is_in_recovery,
            "engine": engine
        }