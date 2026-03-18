import os
import csv
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "data", "productos.csv")
DB_PATH = os.path.join(BASE_DIR, "pintureria.db")

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS productos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    categoria TEXT NOT NULL,
    stock INTEGER NOT NULL,
    precio REAL NOT NULL
)
""")

cursor.execute("DELETE FROM productos")

with open(CSV_PATH, newline="", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    print("Encabezados detectados:", reader.fieldnames)

    for row in reader:
        cursor.execute("""
            INSERT INTO productos (nombre, categoria, stock, precio)
            VALUES (?, ?, ?, ?)
        """, (
            row["nombre"],
            row["categoria"],
            int(row["stock"]),
            float(row["precio"])
        ))

conn.commit()
conn.close()

print("Productos importados correctamente")