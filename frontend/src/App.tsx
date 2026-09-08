import type { ReactNode } from "react";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import Layout from "./components/Layout";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Comunas from "./pages/Comunas";
import Barrios from "./pages/Barrios";
import Personas from "./pages/Personas";
import Roles from "./pages/Roles";
import Usuarios from "./pages/Usuarios";

function RequiereAuth({ children }: { children: ReactNode }) {
  const { token } = useAuth();
  const location = useLocation();
  if (!token) return <Navigate to="/login" replace state={{ desde: location }} />;
  return <>{children}</>;
}

function RequiereRol({ rol, children }: { rol: string; children: ReactNode }) {
  const { rol: rolUsuario } = useAuth();
  if (rolUsuario !== rol) return <Navigate to="/" replace />;
  return <>{children}</>;
}

export default function App() {
  const { token } = useAuth();

  return (
    <Routes>
      <Route
        path="/login"
        element={token ? <Navigate to="/" replace /> : <Login />}
      />
      <Route
        path="/"
        element={
          <RequiereAuth>
            <Layout />
          </RequiereAuth>
        }
      >
        <Route index element={<Dashboard />} />
        <Route path="comunas" element={<Comunas />} />
        <Route path="barrios" element={<Barrios />} />
        <Route path="personas" element={<Personas />} />
        <Route
          path="roles"
          element={
            <RequiereRol rol="ADMIN">
              <Roles />
            </RequiereRol>
          }
        />
        <Route
          path="usuarios"
          element={
            <RequiereRol rol="ADMIN">
              <Usuarios />
            </RequiereRol>
          }
        />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
