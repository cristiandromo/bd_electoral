from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import role_required
from ..models import Barrio, Comuna, Persona
from ..schemas import (
    BarrioCreate,
    BarrioDetail,
    BarrioUpdate,
)

router = APIRouter(prefix="/barrios", tags=["Barrios"])


def _get_barrio_or_404(db: Session, barrio_id: int) -> Barrio:
    barrio = db.get(Barrio, barrio_id)
    if barrio is None:
        raise HTTPException(status_code=404, detail="Barrio no encontrado")
    return barrio


def _validar_comuna(db: Session, comuna_id: int) -> None:
    if db.get(Comuna, comuna_id) is None:
        raise HTTPException(status_code=400, detail="Comuna no válida")


@router.get("", response_model=list[BarrioDetail])
def listar_barrios(comuna_id: int | None = None, db: Session = Depends(get_db)):
    query = select(Barrio).order_by(Barrio.nombre)
    if comuna_id is not None:
        query = query.where(Barrio.comuna_id == comuna_id)
    return db.scalars(query).all()


@router.get("/{barrio_id}", response_model=BarrioDetail)
def obtener_barrio(barrio_id: int, db: Session = Depends(get_db)):
    return _get_barrio_or_404(db, barrio_id)


@router.post(
    "",
    response_model=BarrioDetail,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def crear_barrio(datos: BarrioCreate, db: Session = Depends(get_db)):
    _validar_comuna(db, datos.comuna_id)
    barrio = Barrio(**datos.model_dump())
    db.add(barrio)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El barrio ya existe en esa comuna",
        ) from exc
    db.refresh(barrio)
    return barrio


@router.put(
    "/{barrio_id}",
    response_model=BarrioDetail,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def actualizar_barrio(
    barrio_id: int, datos: BarrioUpdate, db: Session = Depends(get_db)
):
    barrio = _get_barrio_or_404(db, barrio_id)
    cambios = datos.model_dump(exclude_unset=True)
    if "comuna_id" in cambios:
        _validar_comuna(db, cambios["comuna_id"])
    for campo, valor in cambios.items():
        setattr(barrio, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El barrio ya existe en esa comuna",
        ) from exc
    db.refresh(barrio)
    return barrio


@router.delete(
    "/{barrio_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required("ADMIN"))],
)
def eliminar_barrio(barrio_id: int, db: Session = Depends(get_db)):
    barrio = _get_barrio_or_404(db, barrio_id)
    if db.scalar(select(Persona.id).where(Persona.barrio_id == barrio_id).limit(1)):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se puede eliminar: el barrio tiene personas asociadas",
        )
    db.delete(barrio)
    db.commit()
    return None
