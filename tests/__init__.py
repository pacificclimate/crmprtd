def records_contain_db_connection(test_session, caplog):
    print(type(caplog.records))
    for record in caplog.records:
        if hasattr(record, "database"):
            return getattr(
                record, "database"
            ) == test_session.bind.url.render_as_string(hide_password=True)
    return False
