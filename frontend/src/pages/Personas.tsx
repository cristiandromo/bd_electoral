import { useMemo, useState, type FormEvent } from "react";
import { useAuth } from "../auth/AuthContext";
import type { Barrio, Persona, TipoDocumento } from "../api/types";
import { useList } from "../hooks/useList";
import { api } from "../api/client";
import { Alerta, Cargando, Modal, Vacio } from "../components/ui";

interface Formulario {
  tipo_documento: TipoDocumento;
  documento: string;
  nombres: string;
  apellidos: string;
  telefono: string;
  direccion: string;
  barrio_id: string;
}

const TIPOS: { valor: TipoDocumento; etiqueta: string }[] = [
  { valor: "CC", etiqueta: "Cédula de ciudadanía" },
  { valor: "TI", etiqueta: "Tarjeta de identidad" },
  { valor: "CE", etiqueta: "Cédula de extranjería" },
  { valor: "PAS", etiqueta: "Pasaporte" },
];

const VACIO: Formulario = {
  tipo_documento: "CC",
  documento: "",
  nombres: "",
  apellidos: "",
  telefono: "",
  direccion: "",
  barrio_id: "",
};

export default function Personas() {
  const { rol } = useAuth();
  const puedeEditar = rol === "ADMIN" || rol === "OPERADOR";
  const puedeEliminar = rol === "ADMIN";

  const personas = useList<Persona>("/personas");
  const barrios = useList<Barrio>("/barrios");

  const [busqueda, setBusqueda] = useState("");
  const [abierto, setAbierto] = useState(false);
  const [editando, setEditando] = useState<Persona | null>(null);
  const [form, setForm] = useState<Formulario>(VACIO);
  const [enviando, setEnviando] = useState(false);
  const [msgError, setMsgError] = useState<string | null>(null);

  const visibles = useMemo(() => {
    const q = busqueda.trim().toLowerCase();
    if (!q) return personas.data ?? [];
    return (personas.data ?? []).filter((p) =>
      [p.documento, p.nombres, p.apellidos].some((v) =>
        v.toLowerCase().includes(q),
      ),
    );
  }, [personas.data, busqueda]);

  const abrirCrear = () => {
    setEditando(null);
    setForm(VACIO);
    setMsgError(null);
    setAbierto(true);
  };

  const abrirEditar = (p: Persona) => {
    setEditando(p);
    setForm({
      tipo_documento: p.tipo_documento,
      documento: p.documento,
      nombres: p.nombres,
      apellidos: p.apellidos,
      telefono: p.telefono ?? "",
      direccion: p.direccion ?? "",
      barrio_id: p.barrio_id ? String(p.barrio_id) : "",
    });
    setMsgError(null);
    setAbierto(true);
  };

  const guardar = async (e: FormEvent) => {
    e.preventDefault();
    setEnviando(true);
    setMsgError(null);
    const payload = {
      tipo_documento: form.tipo_documento,
      documento: form.documento,
      nombres: form.nombres,
      apellidos: form.apellidos,
      telefono: form.telefono || null,
      direccion: form.direccion || null,
      barrio_id: form.barrio_id ? Number(form.barrio_id) : null,
    };
    try {
      if (editando) {
        await api.put(`/personas/${editando.id}`, payload);
      } else {
        await api.post("/personas", payload);
      }
      setAbierto(false);
      personas.recargar();
    } catch (err) {
      setMsgError(err instanceof Error ? err.message : "Error al guardar");
    } finally {
      setEnviando(false);
    }
  };

  const eliminar = async (p: Persona) => {
    if (
      !confirm(
        `¿Eliminar a ${p.nombres} ${p.apellidos}? Se borrará también su usuario de acceso.`,
      )
    )
      return;
    try {
      await api.del(`/personas/${p.id}`);
      personas.recargar();
    } catch (err) {
      alert(err instanceof Error ? err.message : "No se pudo eliminar");
    }
  };

  return (
    <div>
      <div className="page-head">
        <h2>Personas</h2>
        {puedeEditar && (
          <button className="btn btn-primary" onClick={abrirCrear}>
            Nueva persona
          </button>
        )}
      </div>

      {personas.error && <Alerta tipo="error">{personas.error}</Alerta>}

      <div className="toolbar">
        <input
          placeholder="Buscar por documento, nombres o apellidos…"
          value={busqueda}
          onChange={(e) => setBusqueda(e.target.value)}
        />
      </div>

      {personas.cargando && <Cargando />}
      {!personas.cargando && !visibles.length && (
        <Vacio mensaje="No hay personas para mostrar." />
      )}

      {visibles.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Documento</th>
                <th>Nombre completo</th>
                <th>Teléfono</th>
                <th>Barrio</th>
                <th style={{ textAlign: "right" }}>Acciones</th>
              </tr>
            </thead>
            <tbody>
              {visibles.map((p) => (
                <tr key={p.id}>
                  <td>
                    {p.tipo_documento} {p.documento}
                  </td>
                  <td>
                    <strong>
                      {p.apellidos}, {p.nombres}
                    </strong>
                  </td>
                  <td>{p.telefono ?? "—"}</td>
                  <td>{p.barrio?.nombre ?? "—"}</td>
                  <td>
                    <div className="acciones">
                      {puedeEditar && (
                        <button className="btn btn-sm" onClick={() => abrirEditar(p)}>
                          Editar
                        </button>
                      )}
                      {puedeEliminar && (
                        <button
                          className="btn btn-danger-ghost btn-sm"
                          onClick={() => eliminar(p)}
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
          titulo={editando ? "Editar persona" : "Nueva persona"}
          onClose={() => setAbierto(false)}
        >
          <form onSubmit={guardar}>
            {msgError && <Alerta tipo="error">{msgError}</Alerta>}
            <div className="form-grid">
              <div className="form-row">
                <label>Tipo de documento</label>
                <select
                  value={form.tipo_documento}
                  onChange={(e) =>
                    setForm({
                      ...form,
                      tipo_documento: e.target.value as TipoDocumento,
                    })
                  }
                >
                  {TIPOS.map((t) => (
                    <option key={t.valor} value={t.valor}>
                      {t.etiqueta}
                    </option>
                  ))}
                </select>
              </div>
              <div className="form-row">
                <label>N.° documento</label>
                <input
                  required
                  value={form.documento}
                  onChange={(e) => setForm({ ...form, documento: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Nombres</label>
                <input
                  required
                  value={form.nombres}
                  onChange={(e) => setForm({ ...form, nombres: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Apellidos</label>
                <input
                  required
                  value={form.apellidos}
                  onChange={(e) => setForm({ ...form, apellidos: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Teléfono</label>
                <input
                  placeholder="+57 300 000 0000"
                  value={form.telefono}
                  onChange={(e) => setForm({ ...form, telefono: e.target.value })}
                />
              </div>
              <div className="form-row">
                <label>Barrio</label>
                <select
                  value={form.barrio_id}
                  onChange={(e) => setForm({ ...form, barrio_id: e.target.value })}
                >
                  <option value="">Sin barrio</option>
                  {(barrios.data ?? []).map((b) => (
                    <option key={b.id} value={b.id}>
                      {b.comuna ? `${b.comuna.nombre} · ` : ""}
                      {b.nombre}
                    </option>
                  ))}
                </select>
              </div>
            </div>
            <div className="form-row">
              <label>Dirección</label>
              <input
                value={form.direccion}
                onChange={(e) => setForm({ ...form, direccion: e.target.value })}
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
