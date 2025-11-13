import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .config import settings

#crear carpeta contenedora si no existe
def _ensure_sqlite_dir(db_url: str):
    if db_url.startswith("sqlite:///"):
        # ruta relativa
        path = db_url.replace("sqlite:///", "", 1)
    elif db_url.startswith("sqlite:////"):
        path = db_url.replace("sqlite:////", "/", 1)
    else:
        return
    dirpath = os.path.dirname(path)
    if dirpath and not os.path.exists(dirpath):
        os.makedirs(dirpath, exist_ok=True)

_ensure_sqlite_dir(settings.DB_URL)

connect_args = {"check_same_thread": False} if settings.DB_URL.startswith("sqlite") else {}
engine = create_engine(settings.DB_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
