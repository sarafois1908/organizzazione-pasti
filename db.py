from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker

engine = create_engine("sqlite:///piatti.db", future=True)
metadata = MetaData()
metadata.reflect(bind=engine)

Session = sessionmaker(bind=engine, future=True)
session = Session()

ingredienti = metadata.tables["ingredienti"]
calendario = metadata.tables["calendario"]