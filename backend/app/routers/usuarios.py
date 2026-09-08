from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from ..database import get_db
from ..deps import role_required
from ..models import Persona, Rol, Usuario
from ..schemas import (
    UsuarioCreate,
    UsuarioRead,
    UsuarioUpdate,
)
from ..security import hash_password

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"],
    dependencies=[Depends(role_required("ADMIN"))],
)


def _usuario_query():
    return select(Usuario).options(
        joinedload(Usuario.persona),
        joinedload(Usuario.rol),
    )


def _get_usuario_or_404(db: Session, usuario_id: int) -> Usuario:
    usuario = db.scalar(_usuario_query().where(Usuario.id == usuario_id))
    if usuario is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario


@router.get("", response_model=list[UsuarioRead])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.scalars(_usuario_query().order_by(Usuario.id)).all()


@router.get("/{usuario_id}", response_model=UsuarioRead)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    return _get_usuario_or_404(db, usuario_id)


@router.post("", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: UsuarioCreate, db: Session = Depends(get_db)):
    if db.get(Persona, datos.persona_id) is None:
        raise HTTPException(status_code=400, detail="Persona no existe")
    if db.get(Rol, datos.rol_id) is None:
        raise HTTPException(status_code=400, detail="Rol no existe")
    if db.scalar(select(Usuario).where(Usuario.email == datos.email)):
        raise HTTPException(status_code=409, detail="El correo ya está en uso")

    usuario = Usuario(
        persona_id=datos.persona_id,
        email=datos.email,
        password_hash=hash_password(datos.password),
        rol_id=datos.rol_id,
        activo=datos.activo,
    )
    db.add(usuario)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear el usuario (persona o correo duplicado)",
        ) from exc
    return _get_usuario_or_404(db, usuario.id)


@router.put("/{usuario_id}", response_model=UsuarioRead)
def actualizar_usuario(
    usuario_id: int, datos: UsuarioUpdate, db: Session = Depends(get_db)
):
    usuario = _get_usuario_or_404(db, usuario_id)
    cambios = datos.model_dump(exclude_unset=True)

    if "email" in cambios:
        duplicado = db.scalar(
            select(Usuario).where(
                Usuario.email == cambios["email"], Usuario.id != usuario_id
            )
        )
        if duplicado:
            raise HTTPException(status_code=409, detail="El correo ya está en uso")

    password = cambios.pop("password", None)
    if password:
        usuario.password_hash = hash_password(password)

    if "rol_id" in cambios and db.get(Rol, cambios["rol_id"]) is None:
        raise HTTPException(status_code=400, detail="Rol no existe")

    for campo, valor in cambios.items():
        setattr(usuario, campo, valor)
    db.commit()
    return _get_usuario_or_404(db, usuario_id)


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    usuario = _get_usuario_or_404(db, usuario_id)
    db.delete(usuario)
    db.commit()
    return None
