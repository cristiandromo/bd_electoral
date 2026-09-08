import { useState, type FormEvent } from "react";
import type { Persona, Rol, Usuario } from "../api/types";
import { useList } from "../hooks/useList";
import { api } from "../api/client";
import { Alerta, Cargando, Modal, Vacio } from "../components/ui";

interface Formulario {
  persona_id: string;
  email: string;
  rol_id: string;
  activo: boolean;
  password: string;
}

const VACIO: Formulario = {
  persona_id: "",
  email: "",
  rol_id: "",
  activo: true,
  password: "",
};

export default function Usuarios() {
  const usuarios = useList<Usuario>("/usuarios");
  const personas = useList<Persona>("/personas");
  const roles = useList<Rol>("/roles");

  const [abierto, setAbierto] = useState(false);
  const [editando, setEditando] = useState<Usuario | null>(null);
  const [form, setForm] = useState<Formulario>(VACIO);
  const [enviando, setEnviando] = useState(false);
  const [msgError, setMsgError] = useState<string | null>(null);

  const abrirCrear = () => {
    setEditando(null);
    setForm(VACIO);
    setMsgError(null);
    setAbierto(true);
  };

  const abrirEditar = (u: Usuario) => {
    setEditando(u);
    setForm({
      persona_id: String(u.persona_id),
      email: u.email,
      rol_id: String(u.rol_id),
      activo: u.activo,
      password: "",
    });
    setMsgError(null);
    setAbierto(true);
  };

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setMsgError(null);
    try {
      if (editando) {
        const payload: Record<string, unknown> = {
          email: form.email,
          rol_id: Number(form.rol_id),
          activo: form.activo,
        };
        if (form.password) payload.password = form.password;
        await api.put(`/usuarios/${editando.id}`, payload);
      } else {
        await api.post("/usuarios", {
          persona_id: Number(form.persona_id),
          email: form.email,
          password: form.password,
          rol_id: Number(form.rol_id),
          activo: form.activo,
        });
      }
      setAbierto(false);
      usuarios.recargar();
    } catch (err) {
      setMsgError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEnviando(false);
    }
  };

  const eliminar = async (u: Usuario) => {
    if (!confirm(`¿Eliminar el acceso de ${u.email}?`)) return;
    try {
      await api.del(`/usuarios/${u.id}`);
      usuarios.recargar();
    } catch (err) {
      alert(err instanceof Error ? err.message : "No se pudo eliminar");
    }
  };

  const personasSinUsuario = (personas.data ?? []).filter(
    (p) => !(usuarios.data ?? []).some((u) => u.persona_id === p.id),
  );

  return (
    <div>
      <div className="page-head">
        <h2>Usuarios</h2>
        <button className="btn btn-primary" onClick={abrirCrear}>
          Nuevo usuario
        </button>
      </div>

      {usuarios.error && <Alerta tipo="error">{usuarios.error}</Alerta>}
      {usuarios.cargando && <Cargando />}
      {!usuarios.cargando && !usuarios.data?.length && (
        <Vacio mensaje="No hay usuarios registrados." />
      )}

      {usuarios.data && usuarios.data.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Persona</th>
                <th>Correo</th>
                <th>Rol</th>
                <th>Estado</th>
                <th>Último acceso</th>
                <th style={{ textAlign: "right" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.data.map((u) => (
                <tr key={u.id}>
                  <td>
                    {u.persona
                      ? `${u.persona.apellidos}, ${u.persona.nombres}`
                      : "—"}
                  </td>
                  <td>{u.email}</td>
                  <td>
                    <span className="badge badge-rol">{u.rol?.nombre}</span>
                  </td>
                  <td>
                    {u.activo ? (
                      <span className="badge badge-activo">Activo</span>
                    ) : (
                      <span className="badge badge-inactivo">Inactivo</span>
                    )}
                  </td>
                  <td>
                    {u.ultimo_login
                      ? new Date(u.ultimo_login).toLocaleString("es-CO")
                      : "Nunca"}
                  </td>
                  <td>
                    <div className="acciones">
                      <button className="btn btn-sm" onClick={() => abrirEditar(u)}>
                        Editar
                      </button>
                      <button
                        className="btn btn-danger-ghost btn-sm"
                        onClick={() => eliminar(u)}
                      >
                        Eliminar
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {abierto && (
        <Modal
          titulo={editando ? "Editar usuario" : "Nuevo usuario"}
          onClose={() => setAbierto(false)}
        >
          <form onSubmit={guardar}>
            {msgError && <Alerta tipo="error">{msgError}</Alerta>}
            <div className="form-row">
              <label>Persona</label>
              {editando ? (
                <input
                  disabled
                  value={
                    editando.persona
                      ? `${editando.persona.nombres} ${editando.persona.apellidos} (${editando.persona.documento})`
                      : editando.persona_id
                  }
                />
              ) : (
                <select
                  required
                  value={form.persona_id}
                  onChange={(e) =>
                    setForm({ ...form, persona_id: e.target.value })
                  }
                >
                  <option value="">Seleccione una persona…</option>
                  {personasSinUsuario.map((p) => (
                    <option key={p.id} value={p.id}>
                      {p.apellidos}, {p.nombres} ({p.documento})
                    </option>
                  ))}
                </select>
              )}
            </div>
            <div className="form-grid">
              <div className="form-row">
                <label>Correo</label>
                <input
                  type="email"
                  required
                  value={form.email}
                  onChange={(e) => setForm({ ...form, email: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Rol</label>
                <select
                  required
                  value={form.rol_id}
                  onChange={(e) => setForm({ ...form, rol_id: e.target.value })}
                >
                  <option value="">Seleccione…</option>
                  {(roles.data ?? []).map((r) => (
                    <option key={r.id} value={r.id}>
                      {r.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-row">
              <label>
                {editando ? "Nueva contraseña (dejar vacío para no cambiarla)" : "Contraseña"}
              </label>
              <input
                type="password"
                minLength={editando ? undefined : 8}
                required={!editando}
                value={form.password}
                onChange={(e) => setForm({ ...form, password: e.target.value })}
              />
            </div>
            <div className="form-row">
              <label style={{ display: "inline-flex", alignItems: "center", gap: 8, fontWeight: 400 }}>
                <input
                  type="checkbox"
                  checked={form.activo}
                  style={{ width: "auto" }}
                  onChange={(e) => setForm({ ...form, activo: e.target.checked })}
                />
                Usuario activo
              </label>
            </div>
            <div className="modal-actions">
              <button type="button" className="btn" onClick={() => setAbierto(false)}>
                Cancelar
              </button>
              <button className="btn btn-primary" disabled={enviando} type="submit">
                {enviando ? "Guardando…" : "Guardar"}
              </button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
