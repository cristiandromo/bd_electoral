# bditagui

API y panel web para administrar comunas, barrios, personas y usuarios del
municipio de Itagüí (Antioquia, Colombia).

Lo construí como proyecto de práctica de desarrollo full-stack. El frontend es una
SPA en React que consume una API en FastAPI; la base de datos es MySQL y el esquema
se define a mano en SQL. Incluye autenticación con JWT, permisos por rol
(`ADMIN`, `OPERADOR`, `CONSULTA`) y pruebas automatizadas del backend.

## Funcionalidades

- Login con JWT; las contraseñas se guardan con hash (`bcrypt`).
- Tres roles con permisos distintos; las rutas del frontend y los endpoints de la
  API exigen el rol correspondiente.
- CRUD de comunas, barrios, personas y usuarios.
- Búsqueda en vivo sobre el listado de personas (documento, nombres o apellidos).
- Cuenta que se bloquea después de 5 intentos de login fallidos.
- Registro público de usuarios, que quedan con rol `CONSULTA`.
- La API expone documentación Swagger en `/docs`.
- `bd.sql` define el esquema con `CHECK`, `ENUM`, claves foráneas e índices;
  `seed_itagui.sql` carga 7 comunas, los 84 barrios oficiales de Itagüí
  (Acuerdo 17 del 30/dic/2024) y 20 personas de prueba.

## Stack

**Frontend**

- React 18 + TypeScript
- Vite
- React Router (rutas protegidas)
- CSS propio, sin librerías de componentes

**Backend**

- Python 3.9+
- FastAPI + Uvicorn
- SQLAlchemy 2.0 (ORM) + PyMySQL
- Pydantic v2
- PyJWT y bcrypt para autenticación
- Pytest

**Base de datos**

- MySQL / MariaDB, `utf8mb4`.

## Estructura

```
.
├── backend/
│   ├── app/
│   │   ├── main.py            # app FastAPI, CORS y montaje de routers
│   │   ├── config.py          # lectura de variables de entorno
│   │   ├── database.py        # motor SQLAlchemy y sesión
│   │   ├── models.py          # modelos ORM
│   │   ├── schemas.py         # esquemas Pydantic
│   │   ├── security.py        # hash y tokens
│   │   ├── deps.py            # dependencias: usuario actual y roles
│   │   ├── seed_admin.py      # roles base + usuario admin inicial
│   │   └── routers/           # auth, roles, comunas, barrios, personas, usuarios
│   ├── tests/                 # pruebas de API
│   └── requirements.txt
├── frontend/
│   └── src/
│       ├── api/               # cliente HTTP y tipos
│       ├── auth/              # contexto de autenticación
│       ├── components/        # layout y componentes UI
│       ├── hooks/             # useList
│       └── pages/             # Login, Dashboard, Comunas, Barrios, Personas,
│                              # Roles, Usuarios
├── scripts/
│   └── gen_seed.py            # genera seed_itagui.sql
├── bd.sql
├── seed_itagui.sql
└── README.md
```

## Cómo correrlo

Requisitos: Python 3.9+, Node.js 18+ y MySQL/MariaDB.

1. Crear la base y cargar los datos:

```bash
mysql -u root -p < bd.sql
mysql -u root -p < seed_itagui.sql
```

`seed_itagui.sql` se genera con `python scripts/gen_seed.py`; los datos de comunas y
barrios están definidos en `scripts/gen_seed.py`.

2. Backend:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # en Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env             # ajustar DATABASE_URL y JWT_SECRET
python -m app.seed_admin         # crea roles y el usuario admin
uvicorn app.main:app --reload --port 8000
```

La API queda en `http://localhost:8000` y Swagger en `/docs`.

3. Frontend:

```bash
cd frontend
npm install
npm run dev
```

La app queda en `http://localhost:5173`. Vite reenvía `/api/*` al backend
(`vite.config.ts`), de modo que el frontend no necesita saber el puerto de la API.

El usuario inicial que crea `seed_admin` es `admin@itagui.com` / `Admin123!`
(editable en `backend/.env`).

## Endpoints

| Método | Ruta               | Descripción                    | Acceso           |
| ------ | ------------------ | ------------------------------ | ---------------- |
| POST   | `/auth/registro`   | Registro (rol CONSULTA)        | público          |
| POST   | `/auth/login`      | Login, devuelve el JWT         | público          |
| GET    | `/auth/me`         | Usuario autenticado            | token            |
| GET    | `/comunas`         | Lista de comunas               | token            |
| GET    | `/comunas/{id}`    | Comuna con sus barrios         | token            |
| POST   | `/comunas`         | Crear comuna                   | ADMIN/OPERADOR   |
| PUT    | `/comunas/{id}`    | Actualizar comuna              | ADMIN/OPERADOR   |
| DELETE | `/comunas/{id}`    | Eliminar comuna                | ADMIN            |
| GET    | `/barrios`         | Barrios (`?comuna_id=` filtra) | token            |
| POST   | `/barrios`         | Crear barrio                   | ADMIN/OPERADOR   |
| PUT    | `/barrios/{id}`    | Actualizar barrio              | ADMIN/OPERADOR   |
| DELETE | `/barrios/{id}`    | Eliminar barrio                | ADMIN            |
| GET    | `/personas`        | Personas (`?q=` busca)         | token            |
| POST   | `/personas`        | Crear persona                  | ADMIN/OPERADOR   |
| PUT    | `/personas/{id}`   | Actualizar persona             | ADMIN/OPERADOR   |
| DELETE | `/personas/{id}`   | Eliminar persona               | ADMIN            |
| GET    | `/roles`           | Lista de roles                 | token            |
| GET    | `/roles/{id}`      | Detalle de rol                 | token            |
| POST   | `/roles`           | Crear rol                      | ADMIN            |
| PUT    | `/roles/{id}`      | Actualizar rol                 | ADMIN            |
| DELETE | `/roles/{id}`      | Eliminar rol                   | ADMIN            |
| GET    | `/usuarios`        | Lista de usuarios              | ADMIN            |
| POST   | `/usuarios`        | Crear usuario                  | ADMIN            |
| PUT    | `/usuarios/{id}`   | Actualizar usuario             | ADMIN            |
| DELETE | `/usuarios/{id}`   | Eliminar usuario               | ADMIN            |
| GET    | `/health`          | Estado de la API               | público          |

## Tests

El backend usa pytest. Los tests se conectan a una base de datos MySQL aparte
(`bditagui_test`, puerto `3307`), que se define en `backend/tests/conftest.py`.
Hay que crearla antes de correrlos (el esquema se asume creado con `bd.sql`):

```bash
cd backend
source .venv/bin/activate
pytest -v
```

Cubren login (éxito, contraseña incorrecta y bloqueo por intentos), registro,
permisos por rol, CRUD de los recursos e integridad referencial (por ejemplo, no
borrar una comuna que tenga barrios).

## Cosas que quedaron pendientes / por mejorar

- El esquema se crea ejecutando `bd.sql`; no hay migraciones (Alembic) todavía.
- CORS está abierto (`allow_origins=["*"]`) porque es un proyecto de práctica;
  conviene restringirlo si se despliega.
- `JWT_SECRET` debe cambiarse fuera de desarrollo; el ejemplo en `.env.example`
  no es para producción.
- No hay capa de tests para el frontend.

## Autor

Cristian — reemplaza por tu usuario de GitHub y deja el enlace si quieres
(mencionar: repositorio o linkedin).

Los datos de comunas y barrios provienen de la división administrativa pública de
Itagüí (Acuerdo 17 del 30/dic/2024).
# bd_electoral
