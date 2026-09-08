import { Link } from "react-router-dom";

interface Tarjeta {
  to: string;
  etiqueta: string;
  desc: string;
}

const GESTION_DATOS: Tarjeta[] = [
  {
    to: "/comunas",
    etiqueta: "Comunas",
    desc: "Crear y editar las comunas del municipio.",
  },
  {
    to: "/barrios",
    etiqueta: "Barrios",
    desc: "Administrar barrios por comuna.",
  },
  {
    to: "/personas",
    etiqueta: "Personas",
    desc: "Registro de personas y su ubicación.",
  },
];

const GESTION_SISTEMA: Tarjeta[] = [
  {
    to: "/admin/usuarios",
    etiqueta: "Usuarios",
    desc: "Crear accesos, asignar rol y activar o desactivar cuentas.",
  },
  {
    to: "/admin/roles",
    etiqueta: "Roles",
    desc: "Definir los roles disponibles del sistema.",
  },
  {
    to: "/admin/reportes",
    etiqueta: "Reportes",
    desc: "Conteos por comuna y exportación de datos a CSV.",
  },
];

function Grupo({ titulo, tarjetas }: { titulo: string; tarjetas: Tarjeta[] }) {
  return (
    <section className="seccion">
      <h3 className="grupo-titulo">{titulo}</h3>
      <div className="link-grid">
        {tarjetas.map((t) => (
          <Link key={t.to} to={t.to} className="link-card">
            <div className="etiqueta">{t.etiqueta}</div>
            <div className="desc">{t.desc}</div>
          </Link>
        ))}
      </div>
    </section>
  );
}

export default function AdminHome() {
  return (
    <div>
      <div className="page-head">
        <h2>Administración</h2>
      </div>
      <p className="alerta alerta-info" style={{ marginTop: 0 }}>
        Módulo exclusivo del rol <strong>ADMIN</strong>. Desde aquí se gestionan los
        datos del municipio y los accesos al sistema.
      </p>

      <Grupo titulo="Gestión de información" tarjetas={GESTION_DATOS} />
      <Grupo titulo="Administración del sistema" tarjetas={GESTION_SISTEMA} />
    </div>
  );
}
