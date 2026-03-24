from fastapi import FastAPI

from app.api.routes.auth import router as auth_router
from app.api.routes.files import router as files_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.app_name)

app.include_router(auth_router)
app.include_router(files_router)


@app.get("/health")
def healthcheck():
    return {"status": "ok"}