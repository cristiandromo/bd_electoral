import { useCallback, useEffect, useState } from "react";
import { api } from "../api/client";

interface UseListResult<T> {
  data: T[] | null;
  error: string | null;
  cargando: boolean;
  recargar: () => void;
}

export function useList<T>(path: string): UseListResult<T> {
  const [data, setData] = useState<T[] | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [cargando, setCargando] = useState(true);

  const recargar = useCallback(() => {
    setCargando(true);
    api
      .get<T[]>(path)
      .then((d) => {
        setData(d);
        setError(null);
      })
      .catch((e: unknown) =>
        setError(e instanceof Error ? e.message : "Error al cargar"),
      )
      .finally(() => setCargando(false));
  }, [path]);

  useEffect(() => {
    recargar();
  }, [recargar]);

  return { data, error, cargando, recargar };
}
