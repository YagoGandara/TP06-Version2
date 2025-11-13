from sqlalchemy.orm import Session
from .models import Todo

DEFAULT_TODOS = [
    {"title": "Seed General", "description": "TP05 ADO", "done": False},
    {"title": "Config QA", "description": "App Settings QA", "done": True},
    {"title": "Config PROD", "description": "App Settings PROD", "done": False},
]

def seed_if_empty(db: Session) -> dict:
    count = db.query(Todo).count()
    if count > 0:
        return {"inserted": 0, "skipped": True, "existing": count}

    for item in DEFAULT_TODOS:
        db.add(Todo(**item))
    db.commit()
    return {"inserted": len(DEFAULT_TODOS), "skipped": False, "existing": 0}
