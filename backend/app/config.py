import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

load_dotenv()  # variables de entorno desde backend/.env (si existe)


def _lista_env(nombre: str, defecto: list[str]) -> list[str]:
    valor = os.getenv(nombre)
    if not valor:
        return defecto
    return [origen.strip() for origen in valor.split(",") if origen.strip()]


@dataclass(frozen=True)
class Settings:
    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+pymysql://root:@localhost:3306/bditagui",
    )
    jwt_secret: str = os.getenv(
        "JWT_SECRET", "cambia-esta-clave-por-una-segura-en-produccion"
    )
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480")
    )
    create_tables: bool = os.getenv("CREATE_TABLES", "false").lower() == "true"
    admin_email: str = os.getenv("ADMIN_EMAIL", "admin@itagui.com")
    admin_password: str = os.getenv("ADMIN_PASSWORD", "Admin123!")
    admin_nombres: str = os.getenv("ADMIN_NOMBRES", "Administrador")
    admin_apellidos: str = os.getenv("ADMIN_APELLIDOS", "del Sistema")
    cors_origins: list[str] = field(
        default_factory=lambda: _lista_env(
            "CORS_ORIGINS",
            ["http://localhost:5173", "http://127.0.0.1:5173"],
        )
    )


settings = Settings()
