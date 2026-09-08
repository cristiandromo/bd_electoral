from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import TipoDocumento


# ---------------------------------------------------------------
# Comunas
# ---------------------------------------------------------------
class ComunaBase(BaseModel):
    numero: int = Field(ge=1, le=20)
    nombre: str = Field(min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class ComunaCreate(ComunaBase):
    pass


class ComunaUpdate(BaseModel):
    numero: int | None = Field(default=None, ge=1, le=20)
    nombre: str | None = Field(default=None, min_length=2, max_length=80)
    descripcion: str | None = Field(default=None, max_length=255)


class BarrioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str


class ComunaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    numero: int
    nombre: str
    descripcion: str | None


class ComunaReadWithBarrios(ComunaRead):
    barrios: list[BarrioRead] = []


# ---------------------------------------------------------------
# Barrios
# ---------------------------------------------------------------
class BarrioBase(BaseModel):
    comuna_id: int
    nombre: str = Field(min_length=2, max_length=100)


class BarrioCreate(BarrioBase):
    pass


class BarrioUpdate(BaseModel):
    comuna_id: int | None = None
    nombre: str | None = Field(default=None, min_length=2, max_length=100)


class BarrioDetail(BarrioRead):
    comuna_id: int
    comuna: ComunaRead | None = None


# ---------------------------------------------------------------
# Roles
# ---------------------------------------------------------------
class RolRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    nombre: str
    descripcion: str | None


class RolCreate(BaseModel):
    nombre: str = Field(min_length=2, max_length=30)
    descripcion: str | None = Field(default=None, max_length=150)


# ---------------------------------------------------------------
# Personas
# ---------------------------------------------------------------
class PersonaBase(BaseModel):
    tipo_documento: TipoDocumento = TipoDocumento.CC
    documento: str = Field(min_length=3, max_length=20)
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    telefono: str | None = Field(
        default=None,
        max_length=20,
        pattern=r"^[0-9+ ()-]{7,20}$",
    )
    direccion: str | None = Field(default=None, max_length=150)
    barrio_id: int | None = None


class PersonaCreate(PersonaBase):
    pass


class PersonaUpdate(BaseModel):
    tipo_documento: TipoDocumento | None = None
    documento: str | None = Field(default=None, min_length=3, max_length=20)
    nombres: str | None = Field(default=None, min_length=2, max_length=80)
    apellidos: str | None = Field(default=None, min_length=2, max_length=80)
    telefono: str | None = Field(
        default=None,
        max_length=20,
        pattern=r"^[0-9+ ()-]{7,20}$",
    )
    direccion: str | None = Field(default=None, max_length=150)
    barrio_id: int | None = None


class PersonaRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    tipo_documento: TipoDocumento
    documento: str
    nombres: str
    apellidos: str
    telefono: str | None
    direccion: str | None
    barrio_id: int | None
    creado_en: datetime
    actualizado_en: datetime
    barrio: BarrioRead | None = None


# ---------------------------------------------------------------
# Usuarios
# ---------------------------------------------------------------
class UsuarioRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    persona_id: int
    email: EmailStr
    rol_id: int
    activo: bool
    ultimo_login: datetime | None
    creado_en: datetime
    persona: PersonaRead | None = None
    rol: RolRead | None = None


class UsuarioCreate(BaseModel):
    persona_id: int
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    rol_id: int
    activo: bool = True


class UsuarioUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=128)
    rol_id: int | None = None
    activo: bool | None = None


# ---------------------------------------------------------------
# Autenticación
# ---------------------------------------------------------------
class RegistroRequest(BaseModel):
    tipo_documento: TipoDocumento = TipoDocumento.CC
    documento: str = Field(min_length=3, max_length=20)
    nombres: str = Field(min_length=2, max_length=80)
    apellidos: str = Field(min_length=2, max_length=80)
    telefono: str | None = Field(
        default=None,
        max_length=20,
        pattern=r"^[0-9+ ()-]{7,20}$",
    )
    direccion: str | None = Field(default=None, max_length=150)
    barrio_id: int | None = None
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    usuario: UsuarioRead


# ---------------------------------------------------------------
# Reportes (solo ADMIN)
# ---------------------------------------------------------------
class ReportePorComuna(BaseModel):
    comuna_id: int
    numero: int
    comuna: str
    barrios: int
    personas: int


class ResumenReporte(BaseModel):
    comunas: int
    barrios: int
    personas: int
    usuarios: int
    por_comuna: list[ReportePorComuna]
