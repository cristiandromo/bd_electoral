import { useState } from "react";
import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const NAV = [
  { to: "/", etiqueta: "Inicio", roles: null, fin: true },
  { to: "/comunas", etiqueta: "Comunas", roles: null },
  { to: "/barrios", etiqueta: "Barrios", roles: null },
  { to: "/personas", etiqueta: "Personas", roles: null },
  { to: "/roles", etiqueta: "Roles", roles: ["ADMIN"] },
  { to: "/usuarios", etiqueta: "Usuarios", roles: ["ADMIN"] },
];

export default function Layout() {
  const { usuario, rol, logout } = useAuth();
  const navigate = useNavigate();
  const [abierto, setAbierto] = useState(false);

  const nombre =
    usuario?.persona
      ? `${usuario.persona.nombres} ${usuario.persona.apellidos}`.trim()
      : usuario?.email ?? "";

  const items = NAV.filter((i) => i.roles === null || i.roles.includes(rol ?? ""));

  const cerrar = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="app-shell">
      <header className="topbar">
        <button
          className="btn btn-menu"
          aria-label="Abrir menú"
          onClick={() => setAbierto(true)}
        >
          ☰
        </button>
        <span className="brand">{">_ bditagui"}</span>
      </header>

      <div
        className={`backdrop${abierto ? " visible" : ""}`}
        onClick={() => setAbierto(false)}
      />

      <aside className={`sidebar${abierto ? " open" : ""}`}>
        <div className="brand">
          bditagui<small>Municipio de Itagüí</small>
        </div>
        <nav>
          {items.map((i) => (
            <NavLink
              key={i.to}
              to={i.to}
              end={i.fin}
              className={({ isActive }) => (isActive ? "active" : "")}
              onClick={() => setAbierto(false)}
            >
              {i.etiqueta}
            </NavLink>
          ))}
        </nav>
        <div className="user-box">
          <div className="nombre">{nombre}</div>
          <div className="rol">{rol ?? ""}</div>
          <button className="btn btn-ghost btn-sm" onClick={cerrar}>
            Cerrar sesión
          </button>
        </div>
      </aside>

      <main className="content">
        <Outlet />
      </main>
    </div>
  );
}
