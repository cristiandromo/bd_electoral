#!/usr/bin/env bash
# Gestiona una instancia local de MariaDB para el proyecto (puerto 3307).
# No usa el MySQL/MariaDB del sistema.
#
# Uso:
#   scripts/mariadb-local.sh start    # inicializa (1a vez) y arranca
#   scripts/mariadb-local.sh stop
#   scripts/mariadb-local.sh status

set -euo pipefail

BASE="${HOME}/.bditagui/mysql"
DATADIR="${BASE}/data"
SOCKET="${BASE}/mysql.sock"
PIDFILE="${BASE}/mariadb.pid"
LOG="${BASE}/error.log"
PORT="3307"
BIND="127.0.0.1"

MARIADB_BIN="$(command -v mariadbd || command -v mysqld)"
INSTALL_BIN="$(command -v mariadb-install-db || command -v mysql_install_db)"
ADMIN_BIN="$(command -v mariadb-admin || command -v mysqladmin)"

comando="${1:-status}"

iniciar() {
  mkdir -p "${BASE}"
  if [ ! -d "${DATADIR}/mysql" ]; then
    echo "Inicializando datadir en ${DATADIR} ..."
    "${INSTALL_BIN}" --no-defaults \
      --datadir="${DATADIR}" \
      --auth-root-authentication-method=normal \
      --skip-test-db >/dev/null
  fi

  if [ -S "${SOCKET}" ]; then
    echo "MariaDB ya está corriendo (socket ${SOCKET})."
    return 0
  fi

  nohup "${MARIADB_BIN}" --no-defaults \
    --datadir="${DATADIR}" \
    --port="${PORT}" \
    --bind-address="${BIND}" \
    --socket="${SOCKET}" \
    --pid-file="${PIDFILE}" \
    --log-error="${LOG}" \
    >/dev/null 2>&1 &

  for _ in $(seq 1 20); do
    [ -S "${SOCKET}" ] && break
    sleep 0.5
  done

  if [ -S "${SOCKET}" ]; then
    echo "MariaDB listo en 127.0.0.1:${PORT} (root sin contraseña)."
  else
    echo "No se pudo iniciar MariaDB. Revisa ${LOG}" >&2
    exit 1
  fi
}

detener() {
  if [ -S "${SOCKET}" ]; then
    "${ADMIN_BIN}" --socket="${SOCKET}" -u root shutdown >/dev/null 2>&1 || true
    echo "MariaDB detenido."
  else
    echo "MariaDB no está corriendo."
  fi
}

estado() {
  if [ -S "${SOCKET}" ]; then
    echo "MariaDB corriendo en 127.0.0.1:${PORT}."
  else
    echo "MariaDB detenido. Inícialo con: scripts/mariadb-local.sh start"
  fi
}

case "${comando}" in
  start) iniciar ;;
  stop) detener ;;
  status) estado ;;
  *)
    echo "Uso: $0 {start|stop|status}" >&2
    exit 2
    ;;
esac
