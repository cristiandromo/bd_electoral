from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import role_required
from ..models import Barrio, Comuna
from ..schemas import (
    ComunaCreate,
    ComunaRead,
    ComunaReadWithBarrios,
    ComunaUpdate,
)

router = APIRouter(prefix="/comunas", tags=["Comunas"])


@router.get("", response_model=list[ComunaRead])
def listar_comunas(db: Session = Depends(get_db)):
    return db.scalars(select(Comuna).order_by(Comuna.numero)).all()


@router.get("/{comuna_id}", response_model=ComunaReadWithBarrios)
def obtener_comuna(comuna_id: int, db: Session = Depends(get_db)):
    comuna = db.get(Comuna, comuna_id)
    if comuna is None:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    return comuna


@router.post(
    "",
    response_model=ComunaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def crear_comuna(datos: ComunaCreate, db: Session = Depends(get_db)):
    comuna = Comuna(**datos.model_dump())
    db.add(comuna)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Número o nombre de comuna ya existe",
        ) from exc
    db.refresh(comuna)
    return comuna


@router.put(
    "/{comuna_id}",
    response_model=ComunaRead,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def actualizar_comuna(
    comuna_id: int, datos: ComunaUpdate, db: Session = Depends(get_db)
):
    comuna = db.get(Comuna, comuna_id)
    if comuna is None:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    for campo, valor in datos.model_dump(exclude_unset=True).items():
        setattr(comuna, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Número o nombre de comuna ya existe",
        ) from exc
    db.refresh(comuna)
    return comuna


@router.delete(
    "/{comuna_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required("ADMIN"))],
)
def eliminar_comuna(comuna_id: int, db: Session = Depends(get_db)):
    comuna = db.get(Comuna, comuna_id)
    if comuna is None:
        raise HTTPException(status_code=404, detail="Comuna no encontrada")
    if db.scalar(select(Barrio.id).where(Barrio.comuna_id == comuna_id).limit(1)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: la comuna tiene barrios asociados",
        )
    db.delete(comuna)
    db.commit()
    return None
