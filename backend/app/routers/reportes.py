import csv
import io

from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import role_required
from ..models import Barrio, Comuna, Persona, Usuario
from ..schemas import ReportePorComuna, ResumenReporte

router = APIRouter(
    prefix="/reportes",
    tags=["Reportes"],
    dependencies=[Depends(role_required("ADMIN"))],
)

# Delimitador ";" y BOM UTF-8 para que el CSV se abra bien en Excel (es-CO).
DELIMITADOR = ";"


def _contar(db: Session, modelo) -> int:
    return db.scalar(select(func.count()).select_from(modelo)) or 0


def _filas_por_comuna(db: Session) -> list[dict]:
    """Una fila por comuna con la cantidad de barrios y personas asociadas."""
    filas = db.execute(
        select(
            Comuna.id.label("comuna_id"),
            Comuna.numero.label("numero"),
            Comuna.nombre.label("comuna"),
            func.count(func.distinct(Barrio.id)).label("barrios"),
            func.count(func.distinct(Persona.id)).label("personas"),
        )
        .outerjoin(Barrio, Barrio.comuna_id == Comuna.id)
        .outerjoin(Persona, Persona.barrio_id == Barrio.id)
        .group_by(Comuna.id, Comuna.numero, Comuna.nombre)
        .order_by(Comuna.numero)
    ).all()
    return [dict(fila._mapping) for fila in filas]


def _celda(valor) -> str:
    return "" if valor is None else str(valor)


def _respuesta_csv(nombre: str, encabezados: list[str], filas) -> Response:
    buffer = io.StringIO()
    escritor = csv.writer(buffer, delimiter=DELIMITADOR, lineterminator="\n")
    escritor.writerow(encabezados)
    for fila in filas:
        escritor.writerow(fila)
    cuerpo = buffer.getvalue().encode("utf-8")
    return Response(
        content=b"\xef\xbb\xbf" + cuerpo,
        media_type="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f'attachment; filename="{nombre}"',
            "Cache-Control": "no-cache",
        },
    )


@router.get("/resumen", response_model=ResumenReporte)
def resumen(db: Session = Depends(get_db)):
    return ResumenReporte(
        comunas=_contar(db, Comuna),
        barrios=_contar(db, Barrio),
        personas=_contar(db, Persona),
        usuarios=_contar(db, Usuario),
        por_comuna=[ReportePorComuna(**fila) for fila in _filas_por_comuna(db)],
    )


@router.get("/exportar/barrios")
def exportar_barrios(db: Session = Depends(get_db)):
    filas = db.execute(
        select(Barrio.nombre, Comuna.numero, Comuna.nombre)
        .join(Comuna, Barrio.comuna_id == Comuna.id)
        .order_by(Comuna.numero, Barrio.nombre)
    ).all()
    return _respuesta_csv(
        "barrios-itagui.csv",
        ["comuna_numero", "comuna", "barrio"],
        ([fila[2], fila[1], fila[0]] for fila in filas),
    )


@router.get("/exportar/personas")
def exportar_personas(comuna_id: int | None = None, db: Session = Depends(get_db)):
    query = (
        select(Persona, Barrio.nombre.label("barrio"), Comuna.nombre.label("comuna"))
        .outerjoin(Barrio, Barrio.id == Persona.barrio_id)
        .outerjoin(Comuna, Comuna.id == Barrio.comuna_id)
        .order_by(Persona.apellidos, Persona.nombres)
    )
    if comuna_id is not None:
        if db.get(Comuna, comuna_id) is None:
            raise HTTPException(status_code=404, detail="Comuna no encontrada")
        query = query.where(Comuna.id == comuna_id)

    filas = db.execute(query).all()

    encabezados = [
        "tipo_documento",
        "documento",
        "nombres",
        "apellidos",
        "telefono",
        "direccion",
        "comuna",
        "barrio",
    ]
    return _respuesta_csv(
        "personas-itagui.csv",
        encabezados,
        (
            [
                _celda(persona.tipo_documento.value),
                _celda(persona.documento),
                _celda(persona.nombres),
                _celda(persona.apellidos),
                _celda(persona.telefono),
                _celda(persona.direccion),
                _celda(comuna),
                _celda(barrio),
            ]
            for persona, barrio, comuna in filas
        ),
    )


@router.get("/exportar/resumen")
def exportar_resumen(db: Session = Depends(get_db)):
    return _respuesta_csv(
        "resumen-comunas.csv",
        ["numero", "comuna", "barrios", "personas"],
        (
            [
                fila["numero"],
                fila["comuna"],
                fila["barrios"],
                fila["personas"],
            ]
            for fila in _filas_por_comuna(db)
        ),
    )
