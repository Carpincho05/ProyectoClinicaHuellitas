"""Modelo: conexión y persistencia SQLite de Huellitas."""
import hashlib
import secrets
import sqlite3
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
DB_PATH = APP_DIR / "huellitas.db"


def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 180_000)
    return salt.hex() + "$" + digest.hex()


def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        candidate = hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return secrets.compare_digest(candidate, digest_hex)
    except (ValueError, TypeError, AttributeError):
        return False


class Database:
    def __init__(self, db_path=DB_PATH):
        self.connection = sqlite3.connect(db_path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute("PRAGMA foreign_keys = ON")
        self.create_schema()
        self.seed_admin()

    def create_schema(self):
        self.connection.executescript("""
        CREATE TABLE IF NOT EXISTS employees(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, phone TEXT, email TEXT UNIQUE,
            position TEXT NOT NULL, role TEXT NOT NULL,
            username TEXT NOT NULL UNIQUE, password_hash TEXT NOT NULL,
            active INTEGER NOT NULL DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS owners(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL, dui TEXT UNIQUE, phone TEXT NOT NULL,
            email TEXT, address TEXT, created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS pets(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL, species TEXT NOT NULL, breed TEXT,
            age INTEGER CHECK(age IS NULL OR age >= 0), sex TEXT, notes TEXT,
            owner_id INTEGER NOT NULL REFERENCES owners(id) ON DELETE RESTRICT
        );
        CREATE TABLE IF NOT EXISTS appointments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL REFERENCES pets(id) ON DELETE RESTRICT,
            vet_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            appointment_date TEXT NOT NULL, appointment_time TEXT NOT NULL,
            reason TEXT, status TEXT NOT NULL DEFAULT 'Programada',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS consultations(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL REFERENCES pets(id) ON DELETE RESTRICT,
            vet_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
            consult_date TEXT NOT NULL, reason TEXT NOT NULL,
            diagnosis TEXT NOT NULL, observations TEXT, treatment TEXT
        );
        CREATE TABLE IF NOT EXISTS payments(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            owner_id INTEGER NOT NULL REFERENCES owners(id) ON DELETE RESTRICT,
            pet_id INTEGER REFERENCES pets(id) ON DELETE RESTRICT,
            description TEXT NOT NULL, amount REAL NOT NULL CHECK(amount >= 0),
            payment_date TEXT NOT NULL, method TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pagado'
        );
        """)
        self.connection.commit()

    def seed_admin(self):
        exists = self.fetch_one("SELECT id FROM employees WHERE username=?", ("admin",))
        if not exists:
            self.execute("""INSERT INTO employees
                (full_name, phone, email, position, role, username, password_hash)
                VALUES (?, ?, ?, ?, ?, ?, ?)""",
                ("Administrador General", "", "admin@huellitas.local", "Administrador",
                 "Administrador", "admin", hash_password("Huellitas2026!")))

    def fetch_all(self, sql, params=()):
        return self.connection.execute(sql, params).fetchall()

    def fetch_one(self, sql, params=()):
        return self.connection.execute(sql, params).fetchone()

    def execute(self, sql, params=()):
        cursor = self.connection.execute(sql, params)
        self.connection.commit()
        return cursor.lastrowid

    def close(self):
        self.connection.close()
