from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import get_current_user
from ..models import Persona, Rol, Usuario
from ..schemas import LoginRequest, RegistroRequest, Token, UsuarioRead
from ..security import create_access_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["Autenticación"])


def _usuario_read(usuario: Usuario) -> UsuarioRead:
    return UsuarioRead.model_validate(usuario)


def _usuario_query():
    return select(Usuario).options(
        joinedload(Usuario.persona),
        joinedload(Usuario.rol),
    )


@router.post("/registro", response_model=Token, status_code=status.HTTP_201_CREATED)
def registrar(datos: RegistroRequest, db: Session = Depends(get_db)):
    """Crea una persona y su usuario (rol CONSULTA por defecto)."""
    rol_consulta = db.scalar(select(Rol).where(Rol.nombre == "CONSULTA"))
    if rol_consulta is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="No existe el rol CONSULTA. Ejecute el seed_admin.",
        )

    if db.scalar(select(Usuario).where(Usuario.email == datos.email)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    persona = Persona(
        tipo_documento=datos.tipo_documento,
        documento=datos.documento,
        nombres=datos.nombres,
        apellidos=datos.apellidos,
        telefono=datos.telefono,
        direccion=datos.direccion,
        barrio_id=datos.barrio_id,
    )
    usuario = Usuario(
        email=datos.email,
        password_hash=hash_password(datos.password),
        rol_id=rol_consulta.id,
        persona=persona,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear el registro: documento o correo ya en uso",
        ) from exc
    db.refresh(usuario)
    return Token(
        access_token=create_access_token(usuario.id, rol_consulta.nombre),
        usuario=_usuario_read(usuario),
    )


@router.post("/login", response_model=Token)
def login(datos: LoginRequest, db: Session = Depends(get_db)):
    usuario = db.scalar(
        _usuario_query().where(Usuario.email == datos.email)
    )
    if usuario is None or not verify_password(datos.password, usuario.password_hash):
        if usuario is not None:
            usuario.intentos_fallidos = (usuario.intentos_fallidos or 0) + 1
            if usuario.intentos_fallidos >= 5:
                usuario.activo = False
            db.commit()
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
        )

    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo. Contacte al administrador.",
        )

    usuario.intentos_fallidos = 0
    usuario.ultimo_login = datetime.utcnow()
    db.commit()
    db.refresh(usuario)

    return Token(
        access_token=create_access_token(usuario.id, usuario.rol.nombre),
        usuario=_usuario_read(usuario),
    )


@router.get("/me", response_model=UsuarioRead)
def me(usuario: Usuario = Depends(get_current_user)):
    return _usuario_read(usuario)
