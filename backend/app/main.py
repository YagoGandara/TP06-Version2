import os
from fastapi import FastAPI, Depends, Header, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from .db import engine, SessionLocal
from .models import Base
from .config import settings
from fastapi.middleware.cors import CORSMiddleware
from .deps import get_store, Store
from .schemas import TodoIn, TodoOut
from .seed import seed_if_empty
from dotenv import load_dotenv

load_dotenv(os.getenv("ENV_FILE", None))

app = FastAPI(title=os.getenv("APP_NAME", "tp05-api"))

origins = os.getenv("CORS_ORIGINS", "").split(",") if os.getenv("CORS_ORIGINS") else ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

# Seed opcional en el primer arranque (no debe tumbar el proceso si falla)
if settings.SEED_ON_START.lower() == "true":
    try:
        with SessionLocal() as db:
            seed_if_empty(db)
    except Exception as e:
        # loggear si querés; no romper el start por un seed
        print(f"[WARN] seed_on_start failed: {e}")


@app.post("/admin/seed")
def run_seed(x_seed_token: str = Header(default="")):
    if not settings.SEED_TOKEN or x_seed_token != settings.SEED_TOKEN:
        raise HTTPException(status_code=401, detail="Unauthorized")
    with SessionLocal() as db:
        result = seed_if_empty(db)
    return {"ok": True, "env": settings.ENV, **result}


@app.get("/")
def root():
    return {"status": "ok", "message": "tp05-api running"}


# --- Healthchecks robustos ---
@app.get("/healthz")
def healthz():
    # ping superficial: el proceso responde
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    # readiness: probar DB sin depender de DI
    info = {"app": "ok"}
    code = 200
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        info["db"] = "ok"
    except OperationalError as e:
        info["db"] = "down"
        info["error"] = e.__class__.__name__
        code = 503
    except Exception as e:
        info["db"] = "down"
        info["error"] = e.__class__.__name__
        code = 503
    return JSONResponse(info, status_code=code)


# --- Fin healthchecks ---

# --- DEBUG ROUTES (temporales; quitarlas en PROD) ---
@app.get("/admin/debug")
def debug():
    return {
        "db_url": settings.DB_URL,
        "db_file_exists": os.path.exists("/home/data/app.db"),
    }


@app.get("/admin/touch")
def touch():
    from .models import Todo
    with SessionLocal() as db:
        return {"count": db.query(Todo).count()}


# --- FIN DEBUG ---


@app.get("/api/todos", response_model=list[TodoOut])
def list_todos(store: Store = Depends(get_store)):
    return store.list()


@app.post("/api/todos", response_model=TodoOut, status_code=201)
def create_todo(payload: TodoIn, store: Store = Depends(get_store)):
    # Reglas de negocio:
    # - El título no puede estar vacío (solo espacios).
    # - El título debe ser único (case-insensitive).
    title = payload.title.strip()
    if not title:
        raise HTTPException(status_code=400, detail="title must not be empty")

    # Regla de unicidad: no permitir dos títulos iguales (case-insensitive)
    existing = [t for t in store.list() if t.title.lower() == title.lower()]
    if existing:
        raise HTTPException(status_code=400, detail="title must be unique")

    todo = store.add(title=title, description=payload.description)
    return todo


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("API_PORT", 8080)))
