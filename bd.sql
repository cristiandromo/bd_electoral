-- =========================================================
-- Base de datos: bditagui
-- Versión mejorada — validaciones, comentarios e índices
-- =========================================================

-- 1. Base de datos
CREATE DATABASE IF NOT EXISTS bditagui
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;
USE bditagui;

-- ---------------------------------------------------------
-- 2. Comunas
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS comunas (
    id            SMALLINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    numero        TINYINT UNSIGNED NOT NULL UNIQUE,
    nombre        VARCHAR(80) NOT NULL UNIQUE,
    descripcion   VARCHAR(255) NULL,
    CONSTRAINT chk_comunas_numero CHECK (numero BETWEEN 1 AND 20)
) ENGINE=InnoDB
  COMMENT='Comunas del municipio de Itagüí';

-- ---------------------------------------------------------
-- 3. Barrios
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS barrios (
    id          MEDIUMINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    comuna_id   SMALLINT UNSIGNED NOT NULL,
    nombre      VARCHAR(100) NOT NULL,
    CONSTRAINT fk_barrios_comuna
        FOREIGN KEY (comuna_id) REFERENCES comunas(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT uq_barrio_por_comuna
        UNIQUE (nombre, comuna_id)
) ENGINE=InnoDB
  COMMENT='Barrios asociados a cada comuna';

CREATE INDEX idx_barrios_comuna ON barrios(comuna_id);

-- ---------------------------------------------------------
-- 4. Roles
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS roles (
    id            TINYINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    nombre        VARCHAR(30) NOT NULL UNIQUE COMMENT 'ADMIN, OPERADOR, CONSULTA, etc.',
    descripcion   VARCHAR(150) NULL
) ENGINE=InnoDB
  COMMENT='Roles del sistema para control de acceso';

-- Datos semilla: evita que las apps dependan de INSERTs manuales sueltos
INSERT INTO roles (nombre, descripcion) VALUES
    ('ADMIN',    'Acceso total al sistema'),
    ('OPERADOR', 'Puede crear y editar registros operativos'),
    ('CONSULTA', 'Acceso de solo lectura')
ON DUPLICATE KEY UPDATE descripcion = VALUES(descripcion);

-- ---------------------------------------------------------
-- 5. Personas (entidad central)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS personas (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    tipo_documento    ENUM('CC', 'TI', 'CE', 'PAS') NOT NULL DEFAULT 'CC',
    documento         VARCHAR(20) NOT NULL,
    nombres           VARCHAR(80) NOT NULL,
    apellidos         VARCHAR(80) NOT NULL,
    telefono          VARCHAR(20) NULL,
    direccion         VARCHAR(150) NULL,
    barrio_id         MEDIUMINT UNSIGNED NULL,
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_personas_barrio
        FOREIGN KEY (barrio_id) REFERENCES barrios(id)
        ON DELETE SET NULL ON UPDATE CASCADE,
    -- El documento es único por tipo: dos tipos distintos no deberían
    -- compartir el mismo número (evita choques CC/TI/CE improbables
    -- pero posibles al migrar datos históricos)
    CONSTRAINT uq_personas_documento UNIQUE (tipo_documento, documento),
    CONSTRAINT chk_personas_telefono CHECK (telefono IS NULL OR telefono REGEXP '^[0-9+ ()-]{7,20}$')
) ENGINE=InnoDB
  COMMENT='Registro central de personas naturales';

CREATE INDEX idx_personas_apellidos_nombres ON personas(apellidos, nombres);
CREATE INDEX idx_personas_barrio ON personas(barrio_id);
CREATE INDEX idx_personas_documento ON personas(documento);

-- ---------------------------------------------------------
-- 6. Usuarios (credenciales vinculadas a una persona)
-- ---------------------------------------------------------
CREATE TABLE IF NOT EXISTS usuarios (
    id                INT UNSIGNED AUTO_INCREMENT PRIMARY KEY,
    persona_id        INT UNSIGNED NOT NULL UNIQUE,
    email             VARCHAR(150) NOT NULL UNIQUE,
    password_hash     VARCHAR(255) NOT NULL,
    rol_id            TINYINT UNSIGNED NOT NULL,
    activo            BOOLEAN NOT NULL DEFAULT TRUE,
    intentos_fallidos TINYINT UNSIGNED NOT NULL DEFAULT 0,
    ultimo_login      DATETIME NULL,
    creado_en         TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    actualizado_en    TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_usuarios_persona
        FOREIGN KEY (persona_id) REFERENCES personas(id)
        ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_usuarios_rol
        FOREIGN KEY (rol_id) REFERENCES roles(id)
        ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT chk_usuarios_email CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$')
) ENGINE=InnoDB
  COMMENT='Credenciales de acceso, una por persona';

CREATE INDEX idx_usuarios_rol ON usuarios(rol_id);
CREATE INDEX idx_usuarios_email_activo ON usuarios(email, activo);
CREATE INDEX idx_usuarios_activo ON usuarios(activo);
