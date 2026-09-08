from __future__ import annotations

from enum import Enum

from sqlalchemy import (
    TIMESTAMP,
    Boolean,
    DateTime,
    Enum as SAEnum,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.mysql import INTEGER, MEDIUMINT, SMALLINT, TINYINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class TipoDocumento(str, Enum):
    CC = "CC"
    TI = "TI"
    CE = "CE"
    PAS = "PAS"


class Comuna(Base):
    __tablename__ = "comunas"

    id: Mapped[int] = mapped_column(SMALLINT(unsigned=True), primary_key=True)
    numero: Mapped[int] = mapped_column(TINYINT(unsigned=True), nullable=False, unique=True)
    nombre: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(255), nullable=True)

    barrios: Mapped[list[Barrio]] = relationship(
        back_populates="comuna", cascade="all, delete-orphan", lazy="selectin"
    )


class Barrio(Base):
    __tablename__ = "barrios"

    id: Mapped[int] = mapped_column(MEDIUMINT(unsigned=True), primary_key=True)
    comuna_id: Mapped[int] = mapped_column(
        SMALLINT(unsigned=True), ForeignKey("comunas.id"), nullable=False
    )
    nombre: Mapped[str] = mapped_column(String(100), nullable=False)

    __table_args__ = (
        UniqueConstraint("nombre", "comuna_id", name="uq_barrio_por_comuna"),
    )

    comuna: Mapped[Comuna] = relationship(back_populates="barrios")


class Rol(Base):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(TINYINT(unsigned=True), primary_key=True)
    nombre: Mapped[str] = mapped_column(String(30), nullable=False, unique=True)
    descripcion: Mapped[str | None] = mapped_column(String(150), nullable=True)

    usuarios: Mapped[list[Usuario]] = relationship(back_populates="rol")


class Persona(Base):
    __tablename__ = "personas"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    tipo_documento: Mapped[TipoDocumento] = mapped_column(
        SAEnum(
            TipoDocumento,
            values_callable=lambda e: [m.value for m in e],
            length=3,
            name="tipo_documento",
        ),
        nullable=False,
        default=TipoDocumento.CC,
    )
    documento: Mapped[str] = mapped_column(String(20), nullable=False)
    nombres: Mapped[str] = mapped_column(String(80), nullable=False)
    apellidos: Mapped[str] = mapped_column(String(80), nullable=False)
    telefono: Mapped[str | None] = mapped_column(String(20), nullable=True)
    direccion: Mapped[str | None] = mapped_column(String(150), nullable=True)
    barrio_id: Mapped[int | None] = mapped_column(
        MEDIUMINT(unsigned=True), ForeignKey("barrios.id"), nullable=True
    )
    creado_en: Mapped[object] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    actualizado_en: Mapped[object] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint(
            "tipo_documento", "documento", name="uq_personas_documento"
        ),
    )

    barrio: Mapped[Barrio | None] = relationship(lazy="selectin")
    usuario: Mapped[Usuario | None] = relationship(
        back_populates="persona",
        uselist=False,
        cascade="all, delete-orphan",
    )


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(INTEGER(unsigned=True), primary_key=True)
    persona_id: Mapped[int] = mapped_column(
        INTEGER(unsigned=True),
        ForeignKey("personas.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    email: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    rol_id: Mapped[int] = mapped_column(
        TINYINT(unsigned=True), ForeignKey("roles.id"), nullable=False
    )
    activo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    intentos_fallidos: Mapped[int] = mapped_column(
        TINYINT(unsigned=True), nullable=False, default=0
    )
    ultimo_login: Mapped[object | None] = mapped_column(DateTime, nullable=True)
    creado_en: Mapped[object] = mapped_column(
        TIMESTAMP, server_default=func.current_timestamp(), nullable=False
    )
    actualizado_en: Mapped[object] = mapped_column(
        TIMESTAMP,
        server_default=func.current_timestamp(),
        onupdate=func.current_timestamp(),
        nullable=False,
    )

    persona: Mapped[Persona] = relationship(back_populates="usuario")
    rol: Mapped[Rol] = relationship(back_populates="usuarios")
