import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { api, clearSession, getStoredUser, getToken, setSession } from "../api/client";
import type { LoginResponse, Usuario } from "../api/types";

interface AuthContextValue {
  usuario: Usuario | null;
  token: string | null;
  rol: string | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(() => getToken());
  const [usuario, setUsuario] = useState<Usuario | null>(() =>
    getStoredUser<Usuario>(),
  );

  const logout = useCallback(() => {
    clearSession();
    setUsuario(null);
    setToken(null);
  }, []);

  useEffect(() => {
    const onExpired = () => {
      clearSession();
      setUsuario(null);
      setToken(null);
    };
    window.addEventListener("auth-expired", onExpired);
    return () => window.removeEventListener("auth-expired", onExpired);
  }, []);

  const login = useCallback(async (email: string, password: string) => {
    const resp = await api.post<LoginResponse>("/auth/login", { email, password });
    setSession(resp.access_token, resp.usuario);
    setToken(resp.access_token);
    setUsuario(resp.usuario);
  }, []);

  const rol = usuario?.rol?.nombre ?? null;

  const value = useMemo(
    () => ({ usuario, token, rol, login, logout }),
    [usuario, token, rol, login, logout],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth debe usarse dentro de <AuthProvider>");
  return ctx;
}
