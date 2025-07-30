def get_all_clients():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL)')
    cur.execute('SELECT url FROM clients')
    clients = [row[0] for row in cur.fetchall()]
    conn.close()
    return clients

def add_client(url):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS clients (id INTEGER PRIMARY KEY AUTOINCREMENT, url TEXT UNIQUE NOT NULL)')
    try:
        cur.execute('INSERT INTO clients (url) VALUES (?)', (url.strip(),))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def remove_client(url):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute('DELETE FROM clients WHERE url = ?', (url.strip(),))
    conn.commit()
    conn.close()
    return True
import sqlite3
import os

def get_db_path():
    return os.path.join(os.path.dirname(__file__), '..', 'clients.db')

def init_db():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE NOT NULL
    )''')
    conn.commit()
    conn.close()

def load_clients():
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT url FROM clients')
    clients = [row[0] for row in c.fetchall()]
    conn.close()
    return clients

def add_client(url):
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    try:
        c.execute('INSERT OR IGNORE INTO clients (url) VALUES (?)', (url,))
        conn.commit()
    finally:
        conn.close()

def import_from_csv(csv_path):
    with open(csv_path, encoding='utf-8') as f:
        for line in f:
            url = line.strip()
            if url:
                add_client(url)
