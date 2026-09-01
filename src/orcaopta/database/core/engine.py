from sqlalchemy import create_engine

DB_PATH = "/home/orcadevstack/orcaopta/orcaopta.db"

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
