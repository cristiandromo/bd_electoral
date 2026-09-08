import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .database import Base, engine
from .routers import auth, barrios, comunas, personas, reportes, roles, usuarios

logger = logging.getLogger("bditagui")

if settings.create_tables:
    Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API bditagui",
    description="Backend para la base de datos bditagui (comunas, barrios, roles, personas, usuarios).",
    version="1.0.0",
)


@app.exception_handler(Exception)
async def errores_no_controlados(request: Request, exc: Exception):
    logger.exception("Error no controlado en %s", request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Error interno del servidor"},
    )

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(roles.router)
app.include_router(comunas.router)
app.include_router(barrios.router)
app.include_router(personas.router)
app.include_router(usuarios.router)
app.include_router(reportes.router)


@app.get("/health", tags=["Salud"])
def health():
    return {"estado": "ok"}
