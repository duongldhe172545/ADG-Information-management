import sqlite3
try:
    db = sqlite3.connect('d:/ADG-Dealer/web/data/app.db', timeout=5)
    db.execute('DELETE FROM customers')
    db.execute("DELETE FROM sqlite_sequence WHERE name='customers'")
    db.commit()
    count = db.execute('SELECT COUNT(*) FROM customers').fetchone()[0]
    print("Database is completely clean! Records:", count)
finally:
    db.close()
