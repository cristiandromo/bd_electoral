# -*- coding: utf-8 -*-
"""Genera seed_itagui.sql: comunas + 84 barrios oficiales de Itagüí + 20 personas de prueba."""

# Fuente: Wikipedia — División administrativa de Itagüí (Acuerdo 17 del 30/dic/2024)
COMUNAS = {
    1: ["Artex", "Zona Industrial No. 1", "Villa Paula", "Los Naranjos", "Centro",
        "Asturias", "Playa Rica", "San Isidro", "Satexco", "San Juan Bautista",
        "Las Mercedes", "San José", "Araucaria", "La Gloria", "La Independencia",
        "Zona Industrial No. 2", "La Santa Cruz"],
    2: ["Camparola", "San Pío X", "Monteverde", "La Palma", "Montesacro",
        "Las Margaritas", "Samaria", "Santa Ana", "El Palmar", "Samaria Robles del Sur",
        "Malta", "La Finca", "Santa Catalina", "Yarumito", "Zona Industrial No. 3"],
    3: ["San Francisco", "Triana", "San Antonio", "San Gabriel", "Las Brisas",
        "Pilsen", "Ditaires", "San Javier", "Bariloche", "19 de Abril",
        "Reserva Campestre", "Villa Lía", "Glorieta Pilsen", "Villas de San Antonio",
        "San Agustín"],
    4: ["Simón Bolívar", "Colinas del Sur", "La Mayorista", "El Carmelo", "El Guayabo",
        "San Fernando", "La Esmeralda", "Viviendas del Sur", "La Hortencia",
        "Villa Ventura", "Santa María No. 2", "Santa María No. 1", "Santa María No. 3"],
    5: ["Balcones de Sevilla", "La Aldea", "Las Américas", "Las Acacias", "El Tablazo",
        "Loma Linda", "Calatrava", "Terranova", "Ferrara"],
    6: ["Fátima", "El Rosario", "Santa María La Nueva", "La Unión", "El Progreso",
        "Loma de los Zuleta", "Los Olivares"],
    7: ["Del Valle", "El Porvenir 2", "El Porvenir 1", "La Villas", "San Pablo",
        "Jardines de San José", "Tierra Verde", "El Arenal"],
}

# nombre -> (comuna, apellido-resumen) para las personas de prueba
PERSONAS = [
    ("Juan Pablo", "Restrepo Mejía", 1, "Centro"),
    ("María Fernanda", "Giraldo Zapata", 1, "Las Mercedes"),
    ("Carlos Andrés", "Ospina Cardona", 2, "Camparola"),
    ("Laura Vanessa", "Vélez Arango", 2, "Samaria"),
    ("Andrés Felipe", "Montoya Salazar", 3, "Ditaires"),
    ("Sara Isabel", "Correa Londoño", 3, "San Gabriel"),
    ("Diego Alejandro", "Uribe Castaño", 4, "Simón Bolívar"),
    ("Valentina", "Patiño Quintero", 4, "Santa María No. 1"),
    ("Sebastián", "Herrera Ríos", 5, "El Tablazo"),
    ("Camila Andrea", "Muñoz Cano", 5, "Loma Linda"),
    ("Julián Esteban", "Rojas Sierra", 6, "El Rosario"),
    ("Daniela", "Cifuentes Barrios", 6, "La Unión"),
    ("Miguel Ángel", "Gaviria Botero", 7, "San Pablo"),
    ("Natalia", "Escobar Rendón", 7, "Tierra Verde"),
    ("Santiago", "Betancur Gil", 3, "Pilsen"),
    ("Manuela", "Castaño Vásquez", 4, "San Fernando"),
    ("Felipe", "Arroyave Naranjo", 2, "La Finca"),
    ("Isabella", "Mejía Cárdenas", 6, "Fátima"),
    ("Samuel", "Londoño Restrepo", 5, "Calatrava"),
    ("Gabriela", "Suárez Marín", 1, "San José"),
]

def sql():
    out = []
    out.append("-- =============================================================")
    out.append("-- Datos de prueba: Itagüí (comunas + barrios) y 20 personas")
    out.append("-- Fuente: División administrativa de Itagüí (Acuerdo 17, 30/dic/2024)")
    out.append("-- https://es.wikipedia.org/wiki/Itagüí")
    out.append("-- =============================================================")
    out.append("USE bditagui;")
    out.append("")

    # Comunas
    out.append("INSERT INTO comunas (numero, nombre, descripcion) VALUES")
    rows = []
    for n in sorted(COMUNAS):
        desc = f"Comuna urbana {n} del municipio de Itagüí"
        rows.append(f"    ({n}, 'Comuna {n}', '{desc}')")
    out.append(",\n".join(rows))
    out.append("ON DUPLICATE KEY UPDATE nombre = VALUES(nombre), descripcion = VALUES(descripcion);")
    out.append("")

    # Barrios
    out.append("INSERT INTO barrios (comuna_id, nombre) VALUES")
    rows = []
    for n in sorted(COMUNAS):
        for b in COMUNAS[n]:
            esc = b.replace("'", "''")
            rows.append(
                f"    ((SELECT id FROM comunas WHERE numero = {n}), '{esc}')"
            )
    out.append(",\n".join(rows))
    out.append(
        "ON DUPLICATE KEY UPDATE nombre = VALUES(nombre);"
    )
    out.append("")

    # Personas
    out.append("INSERT INTO personas")
    out.append("    (tipo_documento, documento, nombres, apellidos, telefono, direccion, barrio_id)")
    out.append("VALUES")
    rows = []
    for i, (nombres, apellidos, comuna, barrio) in enumerate(PERSONAS, start=1):
        doc = f"102044{i:04d}"
        prefijo = ["300", "301", "302", "303", "304", "305", "310", "311", "312", "313"][i % 10]
        tel = f"+57 {prefijo} 555 {1000 + i * 11}"
        calle = 42 + (i % 12)
        cra = 46 + (i % 9)
        num = 10 + i
        dir_ = f"Calle {calle} # {cra}-{num:02d}"
        rows.append(
            f"    ('CC', '{doc}', '{nombres}', '{apellidos}', '{tel}', '{dir_}',"
            f" (SELECT b.id FROM barrios b JOIN comunas c ON b.comuna_id = c.id"
            f" WHERE c.numero = {comuna} AND b.nombre = '{barrio.replace(chr(39), chr(39) + chr(39))}'))"
        )
    out.append(",\n".join(rows))
    out.append("ON DUPLICATE KEY UPDATE documento = VALUES(documento);")
    out.append("")

    return "\n".join(out) + "\n"


if __name__ == "__main__":
    import sys
    dest = sys.argv[1] if len(sys.argv) > 1 else "seed_itagui.sql"
    with open(dest, "w", encoding="utf-8") as f:
        f.write(sql())
    n_barrios = sum(len(v) for v in COMUNAS.values())
    print(f"Escrito {dest}: {len(COMUNAS)} comunas, {n_barrios} barrios, {len(PERSONAS)} personas")
