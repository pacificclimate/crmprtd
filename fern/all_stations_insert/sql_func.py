import sqlalchemy as sa
from sqlalchemy.orm import Session

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