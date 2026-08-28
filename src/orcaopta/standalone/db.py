from sqlalchemy import create_engine

def configure_sqlite(cfg):
    db_url = cfg["standalone"]["db"]
    engine = create_engine(db_url)
    print(f"SQLite DB ready: {db_url}")
    return engine
