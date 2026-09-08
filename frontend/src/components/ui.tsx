import type { ReactNode } from "react";

export function Alerta({
  tipo,
  children,
}: {
  tipo: "error" | "info";
  children: ReactNode;
}) {
  const clase = tipo === "error" ? "alerta-error" : "alerta-info";
  return <div className={`alerta ${clase}`}>{children}</div>;
}

export function Modal({
  titulo,
  onClose,
  children,
}: {
  titulo: string;
  onClose: () => void;
  children: ReactNode;
}) {
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={(e) => e.stopPropagation()}>
        <h3>{titulo}</h3>
        {children}
      </div>
    </div>
  );
}

export function Cargando() {
  return <p className="vacio">Cargando…</p>;
}

export function Vacio({ mensaje }: { mensaje: string }) {
  return <p className="vacio">{mensaje}</p>;
}
