"""Crea los roles base y un usuario administrador inicial.

Uso (desde backend/):
    python -m app.seed_admin
"""
from sqlalchemy import select

from .config import settings
from .database import SessionLocal
from .models import Persona, Rol, Usuario
from .security import hash_password

ROLES_BASE = [
    ("ADMIN", "Acceso total al sistema"),
    ("OPERADOR", "Puede crear y editar registros operativos"),
    ("CONSULTA", "Acceso de solo lectura"),
]


def run() -> None:
    with SessionLocal() as db:
        for nombre, descripcion in ROLES_BASE:
            rol = db.scalar(select(Rol).where(Rol.nombre == nombre))
            if rol is None:
                db.add(Rol(nombre=nombre, descripcion=descripcion))
        db.commit()

        rol_admin = db.scalar(select(Rol).where(Rol.nombre == "ADMIN"))
        assert rol_admin is not None

        admin = db.scalar(
            select(Usuario).where(Usuario.email == settings.admin_email)
        )
        if admin is not None:
            print(f"El administrador {settings.admin_email} ya existe.")
            return

        persona = Persona(
            tipo_documento="CC",
            documento="0000000000",
            nombres=settings.admin_nombres,
            apellidos=settings.admin_apellidos,
        )
        usuario = Usuario(
            email=settings.admin_email,
            password_hash=hash_password(settings.admin_password),
            rol=rol_admin,
            persona=persona,
        )
        db.add(usuario)
        db.commit()
        print(
            f"Administrador creado: {settings.admin_email} "
            f"(contraseña {settings.admin_password})"
        )


if __name__ == "__main__":
    run()
