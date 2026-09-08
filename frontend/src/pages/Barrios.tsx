import { useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import type { Barrio, Comuna } from "../api/types";
import { useList } from "../hooks/useList";
import { api } from "../api/client";
import { Alerta, Cargando, Modal, Vacio } from "../components/ui";

interface Formulario {
  comuna_id: string;
  nombre: string;
}

export default function Barrios() {
  const { rol } = useAuth();
  const puedeEditar = rol === "ADMIN" || rol === "OPERADOR";
  const puedeEliminar = rol === "ADMIN";

  const barrios = useList<Barrio>("/barrios");
  const comunas = useList<Comuna>("/comunas");

  const [filtroComuna, setFiltroComuna] = useState("");
  const [abierto, setAbierto] = useState(false);
  const [editando, setEditando] = useState<Barrio | null>(null);
  const [form, setForm] = useState<Formulario>({ comuna_id: "", nombre: "" });
  const [enviando, setEnviando] = useState(false);
  const [msgError, setMsgError] = useState<string | null>(null);

  const visibles = (barrios.data ?? []).filter(
    (b) => !filtroComuna || String(b.comuna_id) === filtroComuna,
  );

  const abrirCrear = () => {
    setEditando(null);
    setForm({ comuna_id: filtroComuna || "", nombre: "" });
    setMsgError(null);
    setAbierto(true);
  };

  const abrirEditar = (b: Barrio) => {
    setEditando(b);
    setForm({ comuna_id: String(b.comuna_id), nombre: b.nombre });
    setMsgError(null);
    setAbierto(true);
  };

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setMsgError(null);
    const payload = { comuna_id: Number(form.comuna_id), nombre: form.nombre };
    try {
      if (editando) {
        await api.put(`/barrios/${editando.id}`, payload);
      } else {
        await api.post("/barrios", payload);
      }
      setAbierto(false);
      barrios.recargar();
    } catch (err) {
      setMsgError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEnviando(false);
    }
  };

  const eliminar = async (b: Barrio) => {
    if (!confirm(`¿Eliminar el barrio "${b.nombre}"?`)) return;
    try {
      await api.del(`/barrios/${b.id}`);
      barrios.recargar();
    } catch (err) {
      alert(err instanceof Error ? err.message : "No se pudo eliminar");
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Barrios</h2>
        {puedeEditar && (
          <button className="btn btn-primary" onClick={abrirCrear}>
            Nuevo barrio
          </button>
        )}
      </div>

      {(barrios.error ?? comunas.error) && (
        <Alerta tipo="error">{barrios.error ?? comunas.error}</Alerta>
      )}

      <div className="toolbar">
        <select
          value={filtroComuna}
          onChange={(e) => setFiltroComuna(e.target.value)}
        >
          <option value="">Todas las comunas</option>
          {(comunas.data ?? []).map((c) => (
            <option key={c.id} value={c.id}>
              {c.nombre}
            </option>
          ))}
        </select>
      </div>

      {barrios.cargando && <Cargando />}
      {!barrios.cargando && !visibles.length && (
        <Vacio mensaje="No hay barrios para mostrar." />
      )}

      {visibles.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Comuna</th>
                <th style={{ textAlign: "right" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {visibles.map((b) => (
                <tr key={b.id}>
                  <td>
                    <strong>{b.nombre}</strong>
                  </td>
                  <td>{b.comuna?.nombre ?? "—"}</td>
                  <td>
                    <div className="acciones">
                      {puedeEditar && (
                        <button className="btn btn-sm" onClick={() => abrirEditar(b)}>
                          Editar
                        </button>
                      )}
                      {puedeEliminar && (
                        <button
                          className="btn btn-danger-ghost btn-sm"
                          onClick={() => eliminar(b)}
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
          titulo={editando ? `Editar ${editando.nombre}` : "Nuevo barrio"}
          onClose={() => setAbierto(false)}
        >
          <form onSubmit={guardar}>
            {msgError && <Alerta tipo="error">{msgError}</Alerta>}
            <div className="form-row">
              <label>Comuna</label>
              <select
                required
                value={form.comuna_id}
                onChange={(e) => setForm({ ...form, comuna_id: e.target.value })}
              >
                <option value="">Seleccione…</option>
                {(comunas.data ?? []).map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.nombre}
                  </option>
                ))}
              </select>
            </div>
            <div className="form-row">
              <label>Nombre</label>
              <input
                required
                value={form.nombre}
                onChange={(e) => setForm({ ...form, nombre: e.target.value })}
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
