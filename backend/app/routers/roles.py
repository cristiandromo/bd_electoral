from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import role_required
from ..models import Rol
from ..schemas import RolCreate, RolRead

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.get("", response_model=list[RolRead])
def listar_roles(db: Session = Depends(get_db)):
    return db.scalars(select(Rol).order_by(Rol.id)).all()


@router.get("/{rol_id}", response_model=RolRead)
def obtener_rol(rol_id: int, db: Session = Depends(get_db)):
    rol = db.get(Rol, rol_id)
    if rol is None:
        raise HTTPException(status_code=404, detail="Rol no encontrado")
    return rol


@router.post(
    "",
    response_model=RolRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required("ADMIN"))],
)
def crear_rol(datos: RolCreate, db: Session = Depends(get_db)):
    if db.scalar(select(Rol).where(Rol.nombre == datos.nombre.upper())):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El rol ya existe",
        )
    rol = Rol(nombre=datos.nombre.upper(), descripcion=datos.descripcion)
    db.add(rol)
    db.commit()
    db.refresh(rol)
    return rol
