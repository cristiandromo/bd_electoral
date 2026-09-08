import { useEffect, useState } from "react";
import { descargarCSV, api } from "../api/client";
import type { Comuna, ResumenReporte } from "../api/types";
import { useList } from "../hooks/useList";
import { Alerta, Cargando, Vacio } from "../components/ui";

export default function Reportes() {
  const comunas = useList<Comuna>("/comunas");
  const [resumen, setResumen] = useState<ResumenReporte | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [comunaId, setComunaId] = useState("");
  const [descargando, setDescargando] = useState(false);

  useEffect(() => {
    setError(null);
    api
      .get<ResumenReporte>("/reportes/resumen")
      .then(setResumen)
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "No se pudo cargar el resumen"),
      );
  }, []);

  const exportar = async (path: string, nombre: string) => {
    setDescargando(true);
    setError(null);
    try {
      await descargarCSV(path, nombre);
    } catch (e) {
      setError(e instanceof Error ? e.message : "No se pudo exportar");
    } finally {
      setDescargando(false);
    }
  };

  const rutaPersonas = () => {
    const q = comunaId ? `?comuna_id=${comunaId}` : "";
    return `/reportes/exportar/personas${q}`;
  };

  const filtroComuna = comunas.data?.find((c) => String(c.id) === comunaId);
  const totalBarrios = (resumen?.por_comuna ?? []).reduce(
    (acc, fila) => acc + fila.barrios,
    0,
  );
  const totalPersonas = (resumen?.por_comuna ?? []).reduce(
    (acc, fila) => acc + fila.personas,
    0,
  );

  const estadisticas = resumen
    ? [
        { valor: resumen.comunas, etiqueta: "Comunas" },
        { valor: resumen.barrios, etiqueta: "Barrios" },
        { valor: resumen.personas, etiqueta: "Personas" },
        { valor: resumen.usuarios, etiqueta: "Usuarios" },
      ]
    : [];

  return (
    <div>
      <div className="page-head">
        <h2>Reportes y exportación</h2>
      </div>

      {error && <Alerta tipo="error">{error}</Alerta>}
      {!resumen && !error && <Cargando />}

      {resumen && (
        <div className="grid-stats">
          {estadisticas.map((s) => (
            <div className="stat" key={s.etiqueta}>
              <div className="valor">{s.valor}</div>
              <div className="etiqueta">{s.etiqueta}</div>
            </div>
          ))}
        </div>
      )}

      {resumen && resumen.por_comuna.length > 0 && (
        <div className="card table-wrap">
          <table>
            <thead>
              <tr>
                <th>Comuna</th>
                <th style={{ textAlign: "right" }}>Barrios</th>
                <th style={{ textAlign: "right" }}>Personas</th>
              </tr>
            </thead>
            <tbody>
              {resumen.por_comuna.map((f) => (
                <tr key={f.comuna_id}>
                  <td>
                    <strong>{f.comuna}</strong> <span className="muted">(n.° {f.numero})</span>
                  </td>
                  <td style={{ textAlign: "right" }}>{f.barrios}</td>
                  <td style={{ textAlign: "right" }}>{f.personas}</td>
                </tr>
              ))}
              <tr>
                <td>
                  <strong>Total</strong>
                </td>
                <td style={{ textAlign: "right" }}>{totalBarrios}</td>
                <td style={{ textAlign: "right" }}>{totalPersonas}</td>
              </tr>
            </tbody>
          </table>
        </div>
      )}

      {resumen && resumen.por_comuna.length === 0 && (
        <Vacio mensaje="No hay comunas registradas para reportar." />
      )}

      <div className="card">
        <h3 className="grupo-titulo" style={{ marginBottom: 14 }}>
          Exportar a CSV
        </h3>
        <div className="toolbar">
          <select
            value={comunaId}
            onChange={(e) => setComunaId(e.target.value)}
            aria-label="Filtrar personas por comuna"
          >
            <option value="">Personas de todas las comunas</option>
            {(comunas.data ?? []).map((c) => (
              <option key={c.id} value={c.id}>
                {c.nombre}
              </option>
            ))}
          </select>
          <button
            className="btn"
            disabled={descargando}
            onClick={() => exportar(rutaPersonas(), "personas-itagui.csv")}
          >
            {filtroComuna
              ? `Personas de ${filtroComuna.nombre}`
              : "Exportar personas"}
          </button>
          <button
            className="btn"
            disabled={descargando}
            onClick={() => exportar("/reportes/exportar/barrios", "barrios-itagui.csv")}
          >
            Exportar barrios
          </button>
          <button
            className="btn"
            disabled={descargando}
            onClick={() => exportar("/reportes/exportar/resumen", "resumen-comunas.csv")}
          >
            Exportar resumen por comuna
          </button>
        </div>
        <p className="ayuda">
          Los archivos se generan con delimitador ";" y se abren directamente en
          Excel o LibreOffice.
        </p>
      </div>
    </div>
  );
}
