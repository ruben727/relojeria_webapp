# ============================================================================
# DATOS INICIALES
# Los relojes de esta lista se insertan al arrancar la app (en cada deploy).
# Para agregar uno nuevo: añádelo a la lista, haz commit y push.
# ============================================================================

SEED_RELOJES = [
    {
        "modelo": "Submariner Date",
        "marca": "Rolex",
        "precio": 10500.0,
        "stock": 2
    },
]

def seed_db(conn):
    '''Inserta los relojes de SEED_RELOJES que aún no existan (por modelo y marca)'''
    for reloj in SEED_RELOJES:
        existe = conn.execute(
            "SELECT 1 FROM relojes WHERE modelo = ? AND marca = ?",
            (reloj["modelo"], reloj["marca"])
        ).fetchone()
        if not existe:
            conn.execute(
                """INSERT INTO relojes (modelo, marca, precio, stock)
                   VALUES (?, ?, ?, ?)""",
                (reloj["modelo"], reloj["marca"], reloj["precio"], reloj["stock"])
            )
    conn.commit()
