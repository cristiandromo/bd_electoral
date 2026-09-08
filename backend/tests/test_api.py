import pytest


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"estado": "ok"}


# ------------------------------------------------------------------
# Autenticación
# ------------------------------------------------------------------
def test_login_ok(client):
    resp = client.post(
        "/auth/login",
        json={"email": "admin@itagui.com", "password": "Test1234!"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["usuario"]["email"] == "admin@itagui.com"
    assert body["usuario"]["rol"]["nombre"] == "ADMIN"


def test_login_password_incorrecta(client):
    resp = client.post(
        "/auth/login",
        json={"email": "admin@itagui.com", "password": "incorrecta"},
    )
    assert resp.status_code == 401


def test_me_requiere_token(client):
    assert client.get("/auth/me").status_code == 401


def test_me_con_token_valido(client, admin_headers):
    resp = client.get("/auth/me", headers=admin_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@itagui.com"


def test_registro_crea_usuario_consulta(client):
    resp = client.post(
        "/auth/registro",
        json={
            "tipo_documento": "CC",
            "documento": "123456789",
            "nombres": "Ana",
            "apellidos": "Pérez",
            "email": "ana@itagui.com",
            "password": "ClaveSegura1!",
        },
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    assert body["usuario"]["rol"]["nombre"] == "CONSULTA"
    assert body["usuario"]["email"] == "ana@itagui.com"


def test_registro_email_duplicado(client):
    client.post(
        "/auth/registro",
        json={
            "tipo_documento": "CC",
            "documento": "123456789",
            "nombres": "Ana",
            "apellidos": "Pérez",
            "email": "ana@itagui.com",
            "password": "ClaveSegura1!",
        },
    )
    resp = client.post(
        "/auth/registro",
        json={
            "tipo_documento": "CC",
            "documento": "987654321",
            "nombres": "Luis",
            "apellidos": "Gómez",
            "email": "ana@itagui.com",
            "password": "ClaveSegura1!",
        },
    )
    assert resp.status_code == 409


def test_login_inactiva_usuario_tras_fallos(client):
    for _ in range(5):
        client.post(
            "/auth/login",
            json={"email": "consulta@itagui.com", "password": "mala"},
        )
    resp = client.post(
        "/auth/login",
        json={"email": "consulta@itagui.com", "password": "Test1234!"},
    )
    assert resp.status_code == 403


# ------------------------------------------------------------------
# Permisos por rol
# ------------------------------------------------------------------
def test_consulta_no_puede_crear_persona(client, consulta_headers):
    resp = client.post(
        "/personas",
        headers=consulta_headers,
        json={
            "tipo_documento": "CC",
            "documento": "123456789",
            "nombres": "Ana",
            "apellidos": "Pérez",
        },
    )
    assert resp.status_code == 403


def test_operador_no_accede_a_usuarios(client, operador_headers):
    assert client.get("/usuarios", headers=operador_headers).status_code == 403


def test_admin_accede_a_usuarios(client, admin_headers):
    resp = client.get("/usuarios", headers=admin_headers)
    assert resp.status_code == 200
    assert len(resp.json()) == 3


# ------------------------------------------------------------------
# CRUD comunas
# ------------------------------------------------------------------
def test_crud_comuna(client, operador_headers, admin_headers):
    datos = {"numero": 1, "nombre": "Comuna 1", "descripcion": "Centro"}
    resp = client.post("/comunas", headers=operador_headers, json=datos)
    assert resp.status_code == 201, resp.text
    comuna_id = resp.json()["id"]

    assert client.get("/comunas").status_code == 200

    detalle = client.get(f"/comunas/{comuna_id}")
    assert detalle.status_code == 200
    assert detalle.json()["nombre"] == "Comuna 1"

    # duplicado -> 409
    assert (
        client.post("/comunas", headers=operador_headers, json=datos).status_code
        == 409
    )

    actualizada = client.put(
        f"/comunas/{comuna_id}",
        headers=operador_headers,
        json={"nombre": "Comuna Uno"},
    )
    assert actualizada.status_code == 200
    assert actualizada.json()["nombre"] == "Comuna Uno"

    # OPERADOR no puede eliminar
    assert (
        client.delete(f"/comunas/{comuna_id}", headers=operador_headers).status_code
        == 403
    )
    assert client.delete(f"/comunas/{comuna_id}", headers=admin_headers).status_code == 204


def test_404_comuna_inexistente(client, admin_headers):
    assert client.get("/comunas/9999").status_code == 404
    assert client.put("/comunas/9999", headers=admin_headers, json={}).status_code == 404


# ------------------------------------------------------------------
# CRUD barrios
# ------------------------------------------------------------------
def _crear_comuna(client, headers, numero=2):
    resp = client.post(
        "/comunas", headers=headers, json={"numero": numero, "nombre": f"Comuna {numero}"}
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


def test_crud_barrio(client, operador_headers):
    comuna_id = _crear_comuna(client, operador_headers)

    resp = client.post(
        "/barrios", headers=operador_headers, json={"comuna_id": comuna_id, "nombre": "Centro"}
    )
    assert resp.status_code == 201, resp.text
    barrio_id = resp.json()["id"]

    # lista filtrada por comuna
    lista = client.get("/barrios", params={"comuna_id": comuna_id})
    assert lista.status_code == 200
    assert len(lista.json()) == 1
    assert lista.json()[0]["comuna"]["nombre"] == "Comuna 2"

    # nombre duplicado en la misma comuna -> 409
    dup = client.post(
        "/barrios",
        headers=operador_headers,
        json={"comuna_id": comuna_id, "nombre": "Centro"},
    )
    assert dup.status_code == 409

    # comuna inexistente -> 400
    invalido = client.post(
        "/barrios",
        headers=operador_headers,
        json={"comuna_id": 999, "nombre": "Nuevo"},
    )
    assert invalido.status_code == 400

    assert (
        client.get(f"/barrios/{barrio_id}").status_code == 200
    )
    assert client.get("/barrios/9999").status_code == 404


# ------------------------------------------------------------------
# CRUD personas
# ------------------------------------------------------------------
def test_crud_persona(client, operador_headers):
    resp = client.post(
        "/personas",
        headers=operador_headers,
        json={
            "tipo_documento": "CC",
            "documento": "123456789",
            "nombres": "Ana",
            "apellidos": "Pérez",
            "telefono": "+57 300 123 4567",
        },
    )
    assert resp.status_code == 201, resp.text
    persona_id = resp.json()["id"]

    # búsqueda
    encontradas = client.get("/personas", params={"q": "Pérez"})
    assert encontradas.status_code == 200
    assert any(p["id"] == persona_id for p in encontradas.json())

    # documento duplicado mismo tipo -> 409
    dup = client.post(
        "/personas",
        headers=operador_headers,
        json={
            "tipo_documento": "CC",
            "documento": "123456789",
            "nombres": "Otra",
            "apellidos": "Persona",
        },
    )
    assert dup.status_code == 409

    # teléfono inválido -> 422
    invalido = client.post(
        "/personas",
        headers=operador_headers,
        json={
            "tipo_documento": "CC",
            "documento": "555555555",
            "nombres": "X",
            "apellidos": "Y",
            "telefono": "abc",
        },
    )
    assert invalido.status_code == 422

    actualizada = client.put(
        f"/personas/{persona_id}",
        headers=operador_headers,
        json={"nombres": "Ana María"},
    )
    assert actualizada.status_code == 200
    assert actualizada.json()["nombres"] == "Ana María"

    assert client.delete(f"/personas/{persona_id}", headers=operador_headers).status_code == 403


# ------------------------------------------------------------------
# CRUD usuarios (solo admin)
# ------------------------------------------------------------------
def test_admin_crea_y_elimina_usuario(client, admin_headers):
    # persona nueva sin usuario
    persona = client.post(
        "/personas",
        headers=admin_headers,
        json={
            "tipo_documento": "CC",
            "documento": "987654321",
            "nombres": "Nuevo",
            "apellidos": "Empleado",
        },
    )
    assert persona.status_code == 201, persona.text
    persona_id = persona.json()["id"]

    roles = client.get("/roles")
    rol_operador = next(r["id"] for r in roles.json() if r["nombre"] == "OPERADOR")

    resp = client.post(
        "/usuarios",
        headers=admin_headers,
        json={
            "persona_id": persona_id,
            "email": "nuevo@itagui.com",
            "password": "ClaveSegura1!",
            "rol_id": rol_operador,
        },
    )
    assert resp.status_code == 201, resp.text
    usuario_id = resp.json()["id"]
    assert resp.json()["email"] == "nuevo@itagui.com"

    # el nuevo usuario puede hacer login
    login = client.post(
        "/auth/login",
        json={"email": "nuevo@itagui.com", "password": "ClaveSegura1!"},
    )
    assert login.status_code == 200

    assert (
        client.delete(f"/usuarios/{usuario_id}", headers=admin_headers).status_code
        == 204
    )
    assert client.get(f"/usuarios/{usuario_id}", headers=admin_headers).status_code == 404


# ------------------------------------------------------------------
# Integridad referencial
# ------------------------------------------------------------------
def test_no_borra_comuna_con_barrios(client, operador_headers, admin_headers):
    comuna_id = _crear_comuna(client, operador_headers)
    client.post(
        "/barrios", headers=operador_headers, json={"comuna_id": comuna_id, "nombre": "Centro"}
    )
    resp = client.delete(f"/comunas/{comuna_id}", headers=admin_headers)
    assert resp.status_code == 409


def test_eliminar_persona_cascada_usuario(client, admin_headers):
    # eliminamos al OPERADOR (no al admin, para poder seguir autenticados)
    personas = client.get("/personas", params={"q": "9999000002"})
    persona_id = personas.json()[0]["id"]
    usuarios = client.get("/usuarios", headers=admin_headers)
    usuario_id = next(
        u["id"] for u in usuarios.json() if u["persona_id"] == persona_id
    )

    resp = client.delete(f"/personas/{persona_id}", headers=admin_headers)
    assert resp.status_code == 204
    assert client.get(f"/usuarios/{usuario_id}", headers=admin_headers).status_code == 404
