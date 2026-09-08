import { useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import type { Comuna } from "../api/types";
import { useList } from "../hooks/useList";
import { api } from "../api/client";
import { Alerta, Cargando, Modal, Vacio } from "../components/ui";

interface Formulario {
  numero: string;
  nombre: string;
  descripcion: string;
}

const VACIO: Formulario = { numero: "", nombre: "", descripcion: "" };

export default function Comunas() {
  const { rol } = useAuth();
  const puedeEditar = rol === "ADMIN" || rol === "OPERADOR";
  const puedeEliminar = rol === "ADMIN";

  const { data, error, cargando, recargar } = useList<Comuna>("/comunas");
  const [abierto, setAbierto] = useState(false);
  const [editando, setEditando] = useState<Comuna | null>(null);
  const [form, setForm] = useState<Formulario>(VACIO);
  const [enviando, setEnviando] = useState(false);
  const [msgError, setMsgError] = useState<string | null>(null);

  const abrirCrear = () => {
    setEditando(null);
    setForm(VACIO);
    setMsgError(null);
    setAbierto(true);
  };

  const abrirEditar = (c: Comuna) => {
    setEditando(c);
    setForm({
      numero: String(c.numero),
      nombre: c.nombre,
      descripcion: c.descripcion ?? "",
    });
    setMsgError(null);
    setAbierto(true);
  };

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setMsgError(null);
    const payload = {
      numero: Number(form.numero),
      nombre: form.nombre,
      descripcion: form.descripcion || null,
    };
    try {
      if (editando) {
        await api.put(`/comunas/${editando.id}`, payload);
      } else {
        await api.post("/comunas", payload);
      }
      setAbierto(false);
      recargar();
    } catch (err) {
      setMsgError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEnviando(false);
    }
  };

  const eliminar = async (c: Comuna) => {
    if (!confirm(`¿Eliminar la comuna "${c.nombre}"?`)) return;
    try {
      await api.del(`/comunas/${c.id}`);
      recargar();
    } catch (err) {
      alert(err instanceof Error ? err.message : "No se pudo eliminar");
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Comunas</h2>
        {puedeEditar && (
          <button className="btn btn-primary" onClick={abrirCrear}>
            Nueva comuna
          </button>
        )}
      </div>

      {error && <Alerta tipo="error">{error}</Alerta>}
      {cargando && <Cargando />}
      {!cargando && !data?.length && <Vacio mensaje="No hay comunas registradas." />}

      {data && data.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>N.°</th>
                <th>Nombre</th>
                <th>Descripción</th>
                <th style={{ textAlign: "right" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {data.map((c) => (
                <tr key={c.id}>
                  <td>{c.numero}</td>
                  <td>
                    <strong>{c.nombre}</strong>
                  </td>
                  <td>{c.descripcion ?? "—"}</td>
                  <td>
                    <div className="acciones">
                      {puedeEditar && (
                        <button className="btn btn-sm" onClick={() => abrirEditar(c)}>
                          Editar
                        </button>
                      )}
                      {puedeEliminar && (
                        <button
                          className="btn btn-danger-ghost btn-sm"
                          onClick={() => eliminar(c)}
                        >
                          Eliminar
                        </button>
                      )}
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
          titulo={editando ? `Editar ${editando.nombre}` : "Nueva comuna"}
          onClose={() => setAbierto(false)}
        >
          <form onSubmit={guardar}>
            {msgError && <Alerta tipo="error">{msgError}</Alerta>}
            <div className="form-row">
              <label>Número (1–20)</label>
              <input
                type="number"
                min={1}
                max={20}
                required
                value={form.numero}
                onChange={(e) => setForm({ ...form, numero: e.target.value })}
              />
            </div>
            <div className="form-row">
              <label>Nombre</label>
              <input
                required
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
              />
            </div>
            <div className="form-row">
              <label>Descripción</label>
              <textarea
                rows={3}
                value={form.descripcion}
                onChange={(e) => setForm({ ...form, descripcion: e.target.value })}
              />
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
