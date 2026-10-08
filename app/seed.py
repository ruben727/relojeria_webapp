
SEED_RELOJES = [
    {
        "modelo": "Reloj de pulsera clásico",
        "marca": "UTEQ",
        "precio": 10500.0,
        "stock": 3
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
