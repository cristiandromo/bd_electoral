import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";
import { api } from "../api/client";

interface Conteos {
  comunas: number;
  barrios: number;
  personas: number;
}

const MSG_POR_ROL: Record<string, string> = {
  ADMIN: "Tienes control total sobre la información.",
  OPERADOR: "Puedes crear y editar registros operativos.",
  CONSULTA: "Tu acceso es de solo lectura.",
};

export default function Dashboard() {
  const { usuario, rol } = useAuth();
  const [conteos, setConteos] = useState<Conteos | null>(null);

  useEffect(() => {
    Promise.all([
      api.get<unknown[]>("/comunas"),
      api.get<unknown[]>("/barrios"),
      api.get<unknown[]>("/personas"),
    ])
      .then(([c, b, p]) => setConteos({ comunas: c.length, barrios: b.length, personas: p.length }))
      .catch(() => setConteos({ comunas: 0, barrios: 0, personas: 0 }));
  }, []);

  const nombre = usuario?.persona
    ? `${usuario.persona.nombres} ${usuario.persona.apellidos}`.trim()
    : usuario?.email;

  return (
    <div>
      <div className="page-head">
        <h2>Hola, {nombre ?? "usuario"}</h2>
      </div>
      <p className="alerta alerta-info" style={{ marginTop: 0 }}>
        Rol <strong>{rol}</strong>. {MSG_POR_ROL[rol ?? ""] ?? ""}
      </p>

      <div className="grid-stats">
        {[
          { valor: conteos?.comunas ?? "…", etiqueta: "Comunas", to: "/comunas" },
          { valor: conteos?.barrios ?? "…", etiqueta: "Barrios", to: "/barrios" },
          { valor: conteos?.personas ?? "…", etiqueta: "Personas", to: "/personas" },
        ].map((s) => (
          <Link to={s.to} key={s.etiqueta} className="stat">
            <div className="valor">{s.valor}</div>
            <div className="etiqueta">{s.etiqueta}</div>
          </Link>
        ))}
      </div>

      <div className="card">
        <h3 style={{ marginTop: 0 }}>Atajos</h3>
        <div className="acciones" style={{ justifyContent: "flex-start" }}>
          <Link className="btn btn-primary" to="/comunas">
            Administrar comunas
          </Link>
          <Link className="btn" to="/barrios">
            Administrar barrios
          </Link>
          <Link className="btn" to="/personas">
            Administrar personas
          </Link>
          {rol === "ADMIN" && (
            <Link className="btn" to="/usuarios">
              Usuarios del sistema
            </Link>
          )}
        </div>
      </div>
    </div>
  );
}
