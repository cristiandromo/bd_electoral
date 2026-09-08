import { useState, type FormEvent } from "react";
import type { Rol } from "../api/types";
import { useList } from "../hooks/useList";
import { api } from "../api/client";
import { Alerta, Cargando, Modal, Vacio } from "../components/ui";

export default function Roles() {
  const roles = useList<Rol>("/roles");
  const [abierto, setAbierto] = useState(false);
  const [nombre, setNombre] = useState("");
  const [descripcion, setDescripcion] = useState("");
  const [msgError, setMsgError] = useState<string | null>(null);
  const [enviando, setEnviando] = useState(false);

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setMsgError(null);
    try {
      await api.post("/roles", { nombre, descripcion: descripcion || null });
      setAbierto(false);
      setNombre("");
      setDescripcion("");
      roles.recargar();
    } catch (err) {
      setMsgError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEnviando(false);
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Roles</h2>
        <button className="btn btn-primary" onClick={() => setAbierto(true)}>
          Nuevo rol
        </button>
      </div>

      {roles.error && <Alerta tipo="error">{roles.error}</Alerta>}
      {roles.cargando && <Cargando />}
      {!roles.cargando && !roles.data?.length && (
        <Vacio mensaje="No hay roles registrados." />
      )}

      {roles.data && roles.data.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Nombre</th>
                <th>Descripción</th>
              </tr>
            </thead>
            <tbody>
              {roles.data.map((r) => (
                <tr key={r.id}>
                  <td>
                    <span className="badge badge-rol">{r.nombre}</span>
                  </td>
                  <td>{r.descripcion ?? "—"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {abierto && (
        <Modal titulo="Nuevo rol" onClose={() => setAbierto(false)}>
          <form onSubmit={guardar}>
            {msgError && <Alerta tipo="error">{msgError}</Alerta>}
            <div className="form-row">
              <label>Nombre (ej. AUDITOR)</label>
              <input
                required
                value={nombre}
                onChange={(e) => setNombre(e.target.value)}
              />
            </div>
            <div className="form-row">
              <label>Descripción</label>
              <textarea
                rows={3}
                value={descripcion}
                onChange={(e) => setDescripcion(e.target.value)}
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
