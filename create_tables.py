# create_tables.py

from backend.store.db import Base, engine
from backend.store import models

Base.metadata.create_all(bind=engine)
print("Tables created successfully.")