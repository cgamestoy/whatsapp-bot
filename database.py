import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "pintureria.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def buscar_productos(termino):
    conn = get_connection()
    cursor = conn.cursor()

    query = """
    SELECT nombre, categoria, stock, precio
    FROM productos
    WHERE LOWER(nombre) LIKE ?
       OR LOWER(categoria) LIKE ?
    ORDER BY nombre ASC
    LIMIT 10
    """

    patron = f"%{termino.lower()}%"
    cursor.execute(query, (patron, patron))
    resultados = cursor.fetchall()
    conn.close()

    return [dict(r) for r in resultados]


def listar_productos(limit=20):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT nombre, categoria, stock, precio
        FROM productos
        ORDER BY nombre ASC
        LIMIT ?
    """, (limit,))

    resultados = cursor.fetchall()
    conn.close()

    return [dict(r) for r in resultados]