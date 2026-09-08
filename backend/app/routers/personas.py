from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import role_required
from ..models import Barrio, Persona, Usuario
from ..schemas import (
    PersonaCreate,
    PersonaRead,
    PersonaUpdate,
)

router = APIRouter(prefix="/personas", tags=["Personas"])


def _get_persona_or_404(db: Session, persona_id: int) -> Persona:
    persona = db.get(Persona, persona_id)
    if persona is None:
        raise HTTPException(status_code=404, detail="Persona no encontrada")
    return persona


@router.get("", response_model=list[PersonaRead])
def listar_personas(
    q: str | None = Query(default=None, description="Busca por documento, nombres o apellidos"),
    db: Session = Depends(get_db),
):
    query = select(Persona).order_by(Persona.apellidos, Persona.nombres)
    if q:
        patron = f"%{q}%"
        query = query.where(
            or_(
                Persona.documento.like(patron),
                Persona.nombres.like(patron),
                Persona.apellidos.like(patron),
            )
        )
    return db.scalars(query).all()


@router.get("/{persona_id}", response_model=PersonaRead)
def obtener_persona(persona_id: int, db: Session = Depends(get_db)):
    return _get_persona_or_404(db, persona_id)


@router.post(
    "",
    response_model=PersonaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def crear_persona(datos: PersonaCreate, db: Session = Depends(get_db)):
    if datos.barrio_id and db.get(Barrio, datos.barrio_id) is None:
        raise HTTPException(status_code=400, detail="Barrio no válido")
    persona = Persona(**datos.model_dump())
    db.add(persona)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una persona con ese tipo y número de documento",
        ) from exc
    db.refresh(persona)
    return persona


@router.put(
    "/{persona_id}",
    response_model=PersonaRead,
    dependencies=[Depends(role_required("ADMIN", "OPERADOR"))],
)
def actualizar_persona(
    persona_id: int, datos: PersonaUpdate, db: Session = Depends(get_db)
):
    persona = _get_persona_or_404(db, persona_id)
    cambios = datos.model_dump(exclude_unset=True)
    if cambios.get("barrio_id") and db.get(Barrio, cambios["barrio_id"]) is None:
        raise HTTPException(status_code=400, detail="Barrio no válido")
    for campo, valor in cambios.items():
        setattr(persona, campo, valor)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Ya existe una persona con ese tipo y número de documento",
        ) from exc
    db.refresh(persona)
    return persona


@router.delete(
    "/{persona_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(role_required("ADMIN"))],
)
def eliminar_persona(persona_id: int, db: Session = Depends(get_db)):
    persona = _get_persona_or_404(db, persona_id)
    db.delete(persona)  # El usuario asociado se elimina en cascada
    db.commit()
    return None
