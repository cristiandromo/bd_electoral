import { NavLink, Outlet } from "react-router-dom";

const TABS = [
  { to: "/admin", etiqueta: "Resumen", fin: true },
  { to: "/admin/usuarios", etiqueta: "Usuarios" },
  { to: "/admin/roles", etiqueta: "Roles" },
  { to: "/admin/reportes", etiqueta: "Reportes" },
];

export default function AdminLayout() {
  return (
    <div>
      <nav className="admin-tabs" aria-label="Módulo de administración">
        {TABS.map((t) => (
          <NavLink
            key={t.to}
            to={t.to}
            end={t.fin}
            className={({ isActive }) => (isActive ? "active" : "")}
          >
            {t.etiqueta}
          </NavLink>
        ))}
      </nav>
      <Outlet />
    </div>
  );
}
