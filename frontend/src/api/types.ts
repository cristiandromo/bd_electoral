export type TipoDocumento = "CC" | "TI" | "CE" | "PAS";

export interface Comuna {
  id: number;
  numero: number;
  nombre: string;
  descripcion: string | null;
  barrios?: Barrio[];
}

export interface Barrio {
  id: number;
  comuna_id: number;
  nombre: string;
  comuna?: Comuna;
}

export interface Rol {
  id: number;
  nombre: string;
  descripcion: string | null;
}

export interface Persona {
  id: number;
  tipo_documento: TipoDocumento;
  documento: string;
  nombres: string;
  apellidos: string;
  telefono: string | null;
  direccion: string | null;
  barrio_id: number | null;
  creado_en: string;
  actualizado_en: string;
  barrio?: Barrio | null;
}

export interface Usuario {
  id: number;
  persona_id: number;
  email: string;
  rol_id: number;
  activo: boolean;
  ultimo_login: string | null;
  creado_en: string;
  persona: Persona | null;
  rol: Rol | null;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  usuario: Usuario;
}
