import os

os.environ["DATABASE_URL"] = "mysql+pymysql://root:@127.0.0.1:3307/bditagui_test"
os.environ.setdefault("JWT_SECRET", "clave-de-prueba-no-segura")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.database import SessionLocal, engine
from app.models import Persona, Rol, Usuario
from app.security import hash_password

TEST_PASSWORD = "Test1234!"

ROLES_BASE = [
    ("ADMIN", "Acceso total al sistema"),
    ("OPERADOR", "Puede crear y editar registros operativos"),
    ("CONSULTA", "Acceso de solo lectura"),
]

USUARIOS_BASE = [
    ("admin@itagui.com", "ADMIN", "CC", "9999000001"),
    ("operador@itagui.com", "OPERADOR", "CC", "9999000002"),
    ("consulta@itagui.com", "CONSULTA", "CC", "9999000003"),
]


def seed_base():
    """Limpia la BD y deja roles + un usuario por rol listos."""
    with engine.begin() as conn:
        conn.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        for tabla in ("usuarios", "personas", "barrios", "comunas", "roles"):
            conn.execute(text(f"TRUNCATE TABLE {tabla}"))
        conn.execute(text("SET FOREIGN_KEY_CHECKS=1"))

    with SessionLocal() as db:
        roles = {}
        for nombre, descripcion in ROLES_BASE:
            rol = Rol(nombre=nombre, descripcion=descripcion)
            db.add(rol)
            roles[nombre] = rol
        db.flush()

        for email, rol_nombre, tipo_doc, documento in USUARIOS_BASE:
            persona = Persona(
                tipo_documento=tipo_doc,
                documento=documento,
                nombres=f"Usuario",
                apellidos=rol_nombre,
            )
            db.add(persona)
            db.flush()
            db.add(
                Usuario(
                    email=email,
                    password_hash=hash_password(TEST_PASSWORD),
                    rol=roles[rol_nombre],
                    persona=persona,
                )
            )
        db.commit()


@pytest.fixture(scope="session", autouse=True)
def _ensure_tablas():
    # Comprueba que el esquema existe (debe crearse ejecutando bd.sql)
    with engine.connect() as conn:
        conn.execute(text("SELECT 1 FROM roles LIMIT 1"))
    yield


@pytest.fixture(autouse=True)
def _bd_limpia():
    seed_base()
    yield


@pytest.fixture()
def client():
    from app.main import app

    with TestClient(app) as c:
        yield c


def login(client, email: str) -> dict[str, str]:
    resp = client.post(
        "/auth/login", json={"email": email, "password": TEST_PASSWORD}
    )
    assert resp.status_code == 200, resp.text
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


@pytest.fixture()
def admin_headers(client):
    return login(client, "admin@itagui.com")


@pytest.fixture()
def operador_headers(client):
    return login(client, "operador@itagui.com")


@pytest.fixture()
def consulta_headers(client):
    return login(client, "consulta@itagui.com")
