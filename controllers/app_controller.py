"""Controlador: reglas de acceso, validación y operaciones del sistema."""
import re
import sqlite3
from datetime import date, datetime

from models.database import hash_password, verify_password
from models.modules import MODULES


class AppController:
    def __init__(self, database):
        self.db = database
        self.user = None

    def login(self, username, password):
        row = self.db.fetch_one(
            "SELECT * FROM employees WHERE username=? AND active=1", (username.strip(),)
        )
        if row and verify_password(password, row["password_hash"]):
            self.user = dict(row)
            return True
        return False

    def logout(self):
        self.user = None

    def allowed_modules(self):
        if not self.user:
            return []
        role = self.user["role"]
        if role == "Administrador":
            return list(MODULES)
        if role == "Recepcionista":
            return ["Propietarios", "Mascotas", "Citas", "Pagos"]
        if role == "Veterinario":
            return ["Mascotas", "Citas", "Consultas e historial"]
        return []

    def can_access(self, module):
        return module in self.allowed_modules()

    def get_stats(self):
        return {
            "Propietarios": self.db.fetch_one("SELECT COUNT(*) n FROM owners")["n"],
            "Mascotas": self.db.fetch_one("SELECT COUNT(*) n FROM pets")["n"],
            "Citas programadas": self.db.fetch_one("SELECT COUNT(*) n FROM appointments WHERE status='Programada'")["n"],
            "Empleados activos": self.db.fetch_one("SELECT COUNT(*) n FROM employees WHERE active=1")["n"],
        }

    def query_module(self, name):
        if not self.can_access(name):
            raise PermissionError("No tienes permiso para consultar este módulo.")
        table = MODULES[name]["table"]
        if name == "Citas":
            return self.db.fetch_all("SELECT * FROM appointments ORDER BY appointment_date DESC, appointment_time DESC")
        if name == "Consultas e historial":
            return self.db.fetch_all("SELECT * FROM consultations ORDER BY consult_date DESC")
        return self.db.fetch_all(f"SELECT * FROM {table} ORDER BY id DESC")

    def display_value(self, row, column):
        value = row[column]
        if value is None:
            return ""
        lookup = {
            "owner_id": ("owners", "full_name"),
            "pet_id": ("pets", "name"),
            "vet_id": ("employees", "full_name"),
        }
        if column in lookup:
            table, field = lookup[column]
            found = self.db.fetch_one(f"SELECT {field} value FROM {table} WHERE id=?", (value,))
            return found["value"] if found else ""
        if column == "active":
            return "Activo" if value else "Inactivo"
        if column == "amount":
            return f"$ {float(value):.2f}"
        return str(value)

    def fk_options(self, kind):
        if kind in ("fk_owner", "fk_owner_optional"):
            rows = self.db.fetch_all("SELECT id, full_name label FROM owners ORDER BY full_name")
        elif kind in ("fk_pet", "fk_pet_optional"):
            rows = self.db.fetch_all("SELECT id, name label FROM pets ORDER BY name")
        elif kind == "fk_vet":
            rows = self.db.fetch_all("""SELECT id, full_name label FROM employees
                WHERE role='Veterinario' AND active=1 ORDER BY full_name""")
        else:
            rows = []
        return [(r["label"], r["id"]) for r in rows]

    def save_record(self, name, record_id, raw_data):
        if not self.can_access(name):
            raise PermissionError("No tienes permiso para modificar este módulo.")
        if name == "Empleados" and self.user["role"] != "Administrador":
            raise PermissionError("Solo el administrador puede administrar empleados.")

        config = MODULES[name]
        table = config["table"]
        old = None
        if record_id is not None:
            old = self.db.fetch_one(f"SELECT * FROM {table} WHERE id=?", (record_id,))
            if not old:
                raise ValueError("El registro seleccionado ya no existe.")

        data = dict(raw_data)
        self._validate(name, data, record_id)

        if name == "Empleados":
            password = data.pop("password", "")
            if password:
                data["password_hash"] = hash_password(password)
            elif not old:
                raise ValueError("La contraseña es obligatoria para un empleado nuevo.")

        for optional in ("dui", "email", "address", "breed", "sex", "notes", "reason", "observations", "treatment"):
            if optional in data and data[optional] == "":
                data[optional] = None

        if old:
            if not data:
                return
            columns = list(data)
            sql = f"UPDATE {table} SET " + ", ".join(f"{col}=?" for col in columns) + " WHERE id=?"
            values = tuple(data[col] for col in columns) + (record_id,)
        else:
            columns = list(data)
            sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({', '.join('?' for _ in columns)})"
            values = tuple(data[col] for col in columns)
        try:
            self.db.execute(sql, values)
        except sqlite3.IntegrityError as exc:
            raise ValueError("No se pudo guardar. Revisa datos duplicados y relaciones con otros registros.\n" + str(exc)) from exc

    def _validate(self, name, data, record_id):
        required_by_module = {
            "Propietarios": ["full_name", "phone"],
            "Mascotas": ["name", "species", "owner_id"],
            "Citas": ["pet_id", "vet_id", "appointment_date", "appointment_time"],
            "Consultas e historial": ["pet_id", "vet_id", "consult_date", "reason", "diagnosis"],
            "Empleados": ["full_name", "position", "role", "username"],
            "Pagos": ["owner_id", "description", "amount", "payment_date", "method"],
        }
        for key in required_by_module[name]:
            if data.get(key) in (None, ""):
                raise ValueError(f"El campo {key} es obligatorio.")

        if "age" in data and data["age"] not in (None, ""):
            try:
                age = int(data["age"])
                if not 0 <= age <= 150:
                    raise ValueError
                data["age"] = age
            except (ValueError, TypeError):
                raise ValueError("La edad debe ser un número entero entre 0 y 150.")
        elif "age" in data:
            data["age"] = None

        if "amount" in data:
            try:
                data["amount"] = float(str(data["amount"]).replace(",", ""))
                if data["amount"] < 0:
                    raise ValueError
            except (ValueError, TypeError):
                raise ValueError("El monto debe ser un número igual o mayor que cero.")

        for field in ("appointment_date", "consult_date", "payment_date"):
            if field in data:
                try:
                    datetime.strptime(data[field], "%Y-%m-%d")
                except (ValueError, TypeError):
                    raise ValueError(f"La fecha {field} debe usar AAAA-MM-DD.")
        if "appointment_time" in data:
            try:
                datetime.strptime(data["appointment_time"], "%H:%M")
            except (ValueError, TypeError):
                raise ValueError("La hora debe usar el formato HH:MM (ejemplo: 09:30).")

        for field in ("email",):
            if data.get(field) and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", data[field]):
                raise ValueError("Escribe un correo electrónico válido.")
        if data.get("phone") and not re.fullmatch(r"[0-9+() -]{7,20}", data["phone"]):
            raise ValueError("Revisa el número de teléfono (7 a 20 caracteres permitidos).")

        if name == "Empleados" and data.get("role") not in ("Administrador", "Recepcionista", "Veterinario"):
            raise ValueError("Selecciona un rol válido.")
        if name == "Citas" and data.get("status") == "Programada":
            conflict = self.db.fetch_one("""SELECT id FROM appointments
                WHERE vet_id=? AND appointment_date=? AND appointment_time=?
                AND status='Programada' AND id<>COALESCE(?, -1)""",
                (data["vet_id"], data["appointment_date"], data["appointment_time"], record_id))
            if conflict:
                raise ValueError("El veterinario ya tiene una cita programada en esa fecha y hora.")

    def delete_record(self, name, record_id):
        if not self.can_access(name):
            raise PermissionError("No tienes permiso para eliminar en este módulo.")
        if name == "Empleados" and self.user["role"] != "Administrador":
            raise PermissionError("Solo el administrador puede eliminar empleados.")
        table = MODULES[name]["table"]
        try:
            self.db.execute(f"DELETE FROM {table} WHERE id=?", (record_id,))
        except sqlite3.IntegrityError as exc:
            raise ValueError("No se puede eliminar porque este registro está relacionado con otros datos.") from exc
