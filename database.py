import sqlite3
import json
from datetime import datetime
import bcrypt

DB_NAME = "detective.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
    ''')
    
    # Investigations history table (Stores ONLY JSON results, NEVER raw CSVs)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS investigations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            filename TEXT,
            timestamp TEXT,
            result_json TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def hash_password(password: str) -> str:
    # Encode password to bytes and truncate to 72 bytes (bcrypt limit)
    pwd_bytes = password.encode('utf-8')[:72]
    hashed = bcrypt.hashpw(pwd_bytes, bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    pwd_bytes = plain_password.encode('utf-8')[:72]
    return bcrypt.checkpw(pwd_bytes, hashed_password.encode('utf-8'))

def create_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                       (username, hash_password(password)))
        conn.commit()
        user_id = cursor.lastrowid
        return {"success": True, "user_id": user_id, "username": username}
    except sqlite3.IntegrityError:
        return {"success": False, "error": "Username already taken."}
    finally:
        conn.close()

def authenticate_user(username, password):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, password_hash FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    
    if row and verify_password(password, row[1]):
        return {"success": True, "user_id": row[0], "username": username}
    return {"success": False, "error": "Invalid username or password."}

def save_investigation(user_id, filename, result_data):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO investigations (user_id, filename, timestamp, result_json) VALUES (?, ?, ?, ?)",
        (user_id, filename, timestamp, json.dumps(result_data))
    )
    conn.commit()
    conn.close()

def get_user_investigations(user_id):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, filename, timestamp, result_json FROM investigations WHERE user_id = ? ORDER BY id DESC", (user_id,))
    rows = cursor.fetchall()
    conn.close()
    
    history = []
    for r in rows:
        history.append({
            "id": r[0],
            "filename": r[1],
            "timestamp": r[2],
            "result": json.loads(r[3])
        })
    return history

# Initialize DB on module import
init_db()