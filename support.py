def build_bd(cur, con):
    cur.execute('''CREATE TABLE IF NOT EXISTS "Users" (
        "id"	INTEGER,
        "id_tg"	INTEGER,
        "username"	TEXT,
        "address"	TEXT,
        PRIMARY KEY("id" AUTOINCREMENT)
    )''')

    con.commit()