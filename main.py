"""
HUELLITAS - Sistema de Gestión para Clínica Veterinaria
Python 3.10+ | Tkinter | SQLite
Ejecutar: python main.py
"""
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, hashlib, secrets, re
from datetime import datetime, date
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
DB_PATH = APP_DIR / "huellitas.db"
BG = "#F4F7F4"
PANEL = "#FFFFFF"
GREEN = "#246B52"
DARK = "#183D32"
MINT = "#E4F1EA"
TEXT = "#23352E"
MUTED = "#718078"
RED = "#B94141"

def hash_password(password, salt=None):
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 180_000)
    return salt.hex() + "$" + digest.hex()

def verify_password(password, stored):
    try:
        salt_hex, digest_hex = stored.split("$", 1)
        candidate = hash_password(password, bytes.fromhex(salt_hex)).split("$", 1)[1]
        return secrets.compare_digest(candidate, digest_hex)
    except Exception:
        return False

class Database:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA foreign_keys = ON")
        self.create_schema()
        self.seed_admin()

    def create_schema(self):
        self.conn.executescript("""
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
            age INTEGER, sex TEXT, notes TEXT,
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
        self.conn.commit()

    def seed_admin(self):
        row = self.conn.execute("SELECT id FROM employees WHERE username='admin'").fetchone()
        if not row:
            self.conn.execute("""INSERT INTO employees
                (full_name, phone, email, position, role, username, password_hash)
                VALUES(?,?,?,?,?,?,?)""",
                ("Administrador General", "", "admin@huellitas.local",
                 "Administrador", "Administrador", "admin", hash_password("Huellitas2026!")))
            self.conn.commit()

    def rows(self, sql, params=()):
        return self.conn.execute(sql, params).fetchall()

    def run(self, sql, params=()):
        cur = self.conn.execute(sql, params)
        self.conn.commit()
        return cur.lastrowid

    def close(self):
        self.conn.close()

MODULES = {
 "Propietarios": {
  "table":"owners", "columns":["id","full_name","dui","phone","email","address"],
  "labels":["ID","Nombre completo","DUI","Teléfono","Correo","Dirección"],
  "fields":[("full_name","Nombre completo","text"),("dui","DUI","text"),("phone","Teléfono","text"),("email","Correo","text"),("address","Dirección","text")]
 },
 "Mascotas": {
  "table":"pets", "columns":["id","name","species","breed","age","sex","owner_id"],
  "labels":["ID","Nombre","Especie","Raza","Edad","Sexo","Propietario"],
  "fields":[("name","Nombre","text"),("species","Especie","choice",["Perro","Gato","Ave","Conejo","Otro"]),("breed","Raza","text"),("age","Edad (años)","number"),("sex","Sexo","choice",["Macho","Hembra","No especificado"]),("owner_id","Propietario","fk_owner")]
 },
 "Citas": {
  "table":"appointments", "columns":["id","pet_id","vet_id","appointment_date","appointment_time","reason","status"],
  "labels":["ID","Mascota","Veterinario","Fecha","Hora","Motivo","Estado"],
  "fields":[("pet_id","Mascota","fk_pet"),("vet_id","Veterinario","fk_vet"),("appointment_date","Fecha (AAAA-MM-DD)","date"),("appointment_time","Hora (HH:MM)","time"),("reason","Motivo","text"),("status","Estado","choice",["Programada","Atendida","Cancelada"])]
 },
 "Consultas e historial": {
  "table":"consultations", "columns":["id","pet_id","vet_id","consult_date","reason","diagnosis","observations","treatment"],
  "labels":["ID","Mascota","Veterinario","Fecha","Motivo","Diagnóstico","Observaciones","Tratamiento"],
  "fields":[("pet_id","Mascota","fk_pet"),("vet_id","Veterinario","fk_vet"),("consult_date","Fecha (AAAA-MM-DD)","date"),("reason","Motivo","text"),("diagnosis","Diagnóstico","text"),("observations","Observaciones","text"),("treatment","Tratamiento","text")]
 },
 "Empleados": {
  "table":"employees", "columns":["id","full_name","phone","email","position","role","username","active"],
  "labels":["ID","Nombre","Teléfono","Correo","Cargo","Rol","Usuario","Activo"],
  "fields":[("full_name","Nombre completo","text"),("phone","Teléfono","text"),("email","Correo","text"),("position","Cargo","text"),("role","Rol","choice",["Administrador","Recepcionista","Veterinario"]),("username","Usuario","text"),("password","Contraseña (solo al crear/cambiar)","password"),("active","Estado","choice",["Activo","Inactivo"])]
 },
 "Pagos": {
  "table":"payments", "columns":["id","owner_id","pet_id","description","amount","payment_date","method","status"],
  "labels":["ID","Propietario","Mascota","Descripción","Monto","Fecha","Método","Estado"],
  "fields":[("owner_id","Propietario","fk_owner"),("pet_id","Mascota","fk_pet_optional"),("description","Descripción","text"),("amount","Monto ($)","money"),("payment_date","Fecha (AAAA-MM-DD)","date"),("method","Método","choice",["Efectivo","Tarjeta","Transferencia"]),("status","Estado","choice",["Pagado","Pendiente","Anulado"])]
 }
}

class HuellitasApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.db = Database()
        self.user = None
        self.title("Huellitas | Gestión Veterinaria")
        self.geometry("1180x740")
        self.minsize(980, 640)
        self.configure(bg=BG)
        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.show_login()

    def on_close(self):
        self.db.close()
        self.destroy()

    def style(self):
        s = ttk.Style(self)
        try: s.theme_use("clam")
        except tk.TclError: pass
        s.configure("Treeview", background="white", fieldbackground="white",
                    foreground=TEXT, rowheight=30, borderwidth=0, font=("Segoe UI", 9))
        s.configure("Treeview.Heading", background=MINT, foreground=DARK,
                    font=("Segoe UI", 9, "bold"), relief="flat")
        s.map("Treeview", background=[("selected", GREEN)], foreground=[("selected","white")])
        s.configure("TCombobox", padding=6)
        s.configure("TEntry", padding=7)

    def clear(self):
        for w in self.winfo_children(): w.destroy()

    def show_login(self):
        self.clear(); self.style()
        outer = tk.Frame(self, bg=BG); outer.pack(fill="both", expand=True)
        card = tk.Frame(outer, bg=PANEL, padx=42, pady=38, highlightthickness=1, highlightbackground="#DCE8DF")
        card.place(relx=.5, rely=.5, anchor="center", width=430, height=510)
        tk.Label(card, text="🐾", font=("Segoe UI Emoji", 38), bg=PANEL, fg=GREEN).pack(pady=(8,0))
        tk.Label(card, text="HUELLITAS", font=("Segoe UI", 24, "bold"), bg=PANEL, fg=DARK).pack()
        tk.Label(card, text="Sistema de Gestión Veterinaria", font=("Segoe UI", 10), bg=PANEL, fg=MUTED).pack(pady=(0,28))
        tk.Label(card, text="Usuario", bg=PANEL, fg=TEXT, font=("Segoe UI",10,"bold")).pack(anchor="w")
        username = ttk.Entry(card); username.pack(fill="x", pady=(6,16)); username.insert(0,"admin")
        tk.Label(card, text="Contraseña", bg=PANEL, fg=TEXT, font=("Segoe UI",10,"bold")).pack(anchor="w")
        password = ttk.Entry(card, show="•"); password.pack(fill="x", pady=(6,20))
        def login(event=None):
            u = username.get().strip()
            row = self.db.rows("SELECT * FROM employees WHERE username=? AND active=1",(u,))
            if row and verify_password(password.get(), row[0]["password_hash"]):
                self.user = dict(row[0]); self.show_dashboard()
            else:
                messagebox.showerror("Acceso denegado","Usuario o contraseña incorrectos, o cuenta inactiva.")
        btn = tk.Button(card,text="INICIAR SESIÓN",command=login,bg=GREEN,fg="white",
                        activebackground=DARK,activeforeground="white",relief="flat",
                        font=("Segoe UI",10,"bold"),cursor="hand2",pady=12)
        btn.pack(fill="x")
        tk.Label(card,text="Acceso inicial: admin / Huellitas2026!",bg=PANEL,fg=MUTED,
                 font=("Segoe UI",8)).pack(pady=18)
        password.bind("<Return>",login); username.focus_set()

    def show_dashboard(self):
        self.clear(); self.style()
        top = tk.Frame(self,bg=DARK,height=70); top.pack(fill="x")
        tk.Label(top,text="🐾  HUELLITAS",bg=DARK,fg="white",font=("Segoe UI",18,"bold")).pack(side="left",padx=24,pady=16)
        tk.Label(top,text=f"{self.user['full_name']}  |  {self.user['role']}",bg=DARK,fg="#D5E8DC",
                 font=("Segoe UI",10)).pack(side="right",padx=20)
        body=tk.Frame(self,bg=BG); body.pack(fill="both",expand=True)
        side=tk.Frame(body,bg="#EAF2EC",width=220); side.pack(side="left",fill="y"); side.pack_propagate(False)
        tk.Label(side,text="MENÚ PRINCIPAL",bg="#EAF2EC",fg=MUTED,font=("Segoe UI",9,"bold")).pack(anchor="w",padx=18,pady=(25,12))
        allowed=self.allowed_modules()
        for name in allowed:
            tk.Button(side,text="   "+name,anchor="w",command=lambda n=name:self.show_module(n),
                      bg="#EAF2EC",fg=DARK,activebackground=MINT,relief="flat",
                      font=("Segoe UI",10),cursor="hand2",pady=10).pack(fill="x",padx=8)
        tk.Button(side,text="   Cerrar sesión",anchor="w",command=self.logout,bg="#EAF2EC",fg=RED,
                  relief="flat",font=("Segoe UI",10),pady=10).pack(side="bottom",fill="x",padx=8,pady=18)
        content=tk.Frame(body,bg=BG,padx=34,pady=30); content.pack(fill="both",expand=True)
        tk.Label(content,text="Panel de control",bg=BG,fg=DARK,font=("Segoe UI",23,"bold")).pack(anchor="w")
        tk.Label(content,text="Resumen general de Clínica Veterinaria Huellitas",bg=BG,fg=MUTED,
                 font=("Segoe UI",10)).pack(anchor="w",pady=(4,24))
        stats=[
          ("Propietarios","SELECT COUNT(*) n FROM owners"),
          ("Mascotas","SELECT COUNT(*) n FROM pets"),
          ("Citas programadas","SELECT COUNT(*) n FROM appointments WHERE status='Programada'"),
          ("Empleados activos","SELECT COUNT(*) n FROM employees WHERE active=1")
        ]
        grid=tk.Frame(content,bg=BG);grid.pack(fill="x")
        for i,(label,sql) in enumerate(stats):
            val=self.db.rows(sql)[0]["n"]
            box=tk.Frame(grid,bg=PANEL,padx=20,pady=22,highlightbackground="#DCE8DF",highlightthickness=1)
            box.grid(row=0,column=i,sticky="nsew",padx=(0,12))
            tk.Label(box,text=label,bg=PANEL,fg=MUTED,font=("Segoe UI",9)).pack(anchor="w")
            tk.Label(box,text=str(val),bg=PANEL,fg=GREEN,font=("Segoe UI",25,"bold")).pack(anchor="w",pady=(7,0))
            grid.columnconfigure(i,weight=1)
        tk.Label(content,text="Accesos rápidos",bg=BG,fg=DARK,font=("Segoe UI",14,"bold")).pack(anchor="w",pady=(35,14))
        quick=tk.Frame(content,bg=BG);quick.pack(anchor="w")
        for name in ["Propietarios","Mascotas","Citas","Consultas e historial"]:
            if name in allowed:
                tk.Button(quick,text=name,command=lambda n=name:self.show_module(n),bg=GREEN,fg="white",
                          activebackground=DARK,relief="flat",padx=18,pady=12,cursor="hand2").pack(side="left",padx=(0,10))
        tk.Label(content,text="La información se guarda localmente en huellitas.db.",bg=BG,fg=MUTED,
                 font=("Segoe UI",9)).pack(anchor="w",side="bottom",pady=10)

    def allowed_modules(self):
        role=self.user["role"]
        if role=="Administrador": return list(MODULES.keys())
        if role=="Recepcionista": return ["Propietarios","Mascotas","Citas","Pagos"]
        return ["Mascotas","Citas","Consultas e historial"]

    def logout(self):
        self.user=None; self.show_login()

    def display_value(self, module, row, col):
        val=row[col]
        if val is None: return ""
        if col=="owner_id":
            x=self.db.rows("SELECT full_name FROM owners WHERE id=?",(val,)); return x[0][0] if x else ""
        if col=="pet_id":
            x=self.db.rows("SELECT name FROM pets WHERE id=?",(val,)); return x[0][0] if x else ""
        if col=="vet_id":
            x=self.db.rows("SELECT full_name FROM employees WHERE id=?",(val,)); return x[0][0] if x else ""
        if col=="active": return "Activo" if val else "Inactivo"
        if col=="amount": return f"$ {float(val):.2f}"
        return str(val)

    def query_module(self,name):
        cfg=MODULES[name]; table=cfg["table"]
        if name=="Citas":
            return self.db.rows("""SELECT a.* FROM appointments a ORDER BY appointment_date DESC, appointment_time DESC""")
        if name=="Consultas e historial":
            return self.db.rows("SELECT * FROM consultations ORDER BY consult_date DESC")
        return self.db.rows(f"SELECT * FROM {table} ORDER BY id DESC")

    def show_module(self,name):
        self.clear(); self.style()
        top=tk.Frame(self,bg=DARK);top.pack(fill="x")
        tk.Button(top,text="← Inicio",command=self.show_dashboard,bg=DARK,fg="white",relief="flat",
                  font=("Segoe UI",10),cursor="hand2").pack(side="left",padx=18,pady=18)
        tk.Label(top,text=name,bg=DARK,fg="white",font=("Segoe UI",17,"bold")).pack(side="left",padx=12)
        tk.Label(top,text=self.user["full_name"],bg=DARK,fg="#D5E8DC").pack(side="right",padx=20)
        area=tk.Frame(self,bg=BG,padx=24,pady=22);area.pack(fill="both",expand=True)
        bar=tk.Frame(area,bg=BG);bar.pack(fill="x",pady=(0,14))
        search=ttk.Entry(bar,width=34);search.pack(side="left",ipady=4)
        tk.Label(bar,text="Buscar en los registros",bg=BG,fg=MUTED).pack(side="left",padx=10)
        table_frame=tk.Frame(area,bg=PANEL);table_frame.pack(fill="both",expand=True)
        cfg=MODULES[name]; cols=cfg["columns"]
        tree=ttk.Treeview(table_frame,columns=cols,show="headings")
        for c,lbl in zip(cols,cfg["labels"]):
            tree.heading(c,text=lbl);tree.column(c,width=125,anchor="w")
        vs=ttk.Scrollbar(table_frame,orient="vertical",command=tree.yview);hs=ttk.Scrollbar(table_frame,orient="horizontal",command=tree.xview)
        tree.configure(yscrollcommand=vs.set,xscrollcommand=hs.set)
        tree.pack(side="top",fill="both",expand=True);vs.pack(side="right",fill="y");hs.pack(side="bottom",fill="x")
        def refresh():
            tree.delete(*tree.get_children())
            for row in self.query_module(name):
                values=[self.display_value(name,row,c) for c in cols]
                tree.insert("","end",iid=str(row["id"]),values=values)
        def selected_id():
            sel=tree.selection()
            if not sel:
                messagebox.showwarning("Selecciona un registro","Selecciona una fila de la tabla primero.")
                return None
            return int(sel[0])
        def filtered(*_):
            term=search.get().strip().lower()
            tree.delete(*tree.get_children())
            for row in self.query_module(name):
                values=[self.display_value(name,row,c) for c in cols]
                if not term or term in " ".join(map(str,values)).lower():
                    tree.insert("","end",iid=str(row["id"]),values=values)
        search.bind("<KeyRelease>",filtered)
        actions=tk.Frame(area,bg=BG);actions.pack(fill="x",pady=(14,0))
        tk.Button(actions,text="+ Nuevo registro",command=lambda:self.edit_record(name,None,refresh),bg=GREEN,fg="white",relief="flat",padx=15,pady=10).pack(side="left",padx=(0,8))
        tk.Button(actions,text="Editar seleccionado",command=lambda:self.edit_record(name,selected_id(),refresh),bg="#DCEBE1",fg=DARK,relief="flat",padx=15,pady=10).pack(side="left",padx=8)
        tk.Button(actions,text="Eliminar seleccionado",command=lambda:self.delete_record(name,selected_id(),refresh),bg="#F8E6E6",fg=RED,relief="flat",padx=15,pady=10).pack(side="left",padx=8)
        tk.Button(actions,text="Actualizar",command=refresh,bg="#E7ECE8",fg=DARK,relief="flat",padx=15,pady=10).pack(side="right")
        refresh()

    def fk_options(self,kind):
        if kind in ("fk_owner","fk_owner_optional"):
            return [(r["full_name"],r["id"]) for r in self.db.rows("SELECT id,full_name FROM owners ORDER BY full_name")]
        if kind in ("fk_pet","fk_pet_optional"):
            return [(r["name"],r["id"]) for r in self.db.rows("SELECT id,name FROM pets ORDER BY name")]
        if kind=="fk_vet":
            return [(r["full_name"],r["id"]) for r in self.db.rows("SELECT id,full_name FROM employees WHERE role='Veterinario' AND active=1 ORDER BY full_name")]
        return []

    def edit_record(self,name,record_id,refresh):
        if record_id is None and name=="Empleados" and self.user["role"]!="Administrador":
            messagebox.showerror("Permiso denegado","Solo el administrador puede crear empleados y cuentas de acceso.");return
        cfg=MODULES[name]; table=cfg["table"]
        old=None
        if record_id:
            old=self.db.rows(f"SELECT * FROM {table} WHERE id=?",(record_id,))[0]
        win=tk.Toplevel(self);win.title(("Editar " if old else "Nuevo ")+name);win.configure(bg=BG)
        win.transient(self);win.grab_set();win.geometry("540x650")
        tk.Label(win,text=("Editar registro" if old else "Registrar nuevo"),bg=BG,fg=DARK,font=("Segoe UI",18,"bold")).pack(anchor="w",padx=24,pady=(20,4))
        tk.Label(win,text="Completa los campos y guarda la información.",bg=BG,fg=MUTED).pack(anchor="w",padx=24,pady=(0,12))
        canvas=tk.Canvas(win,bg=BG,highlightthickness=0);scroll=ttk.Scrollbar(win,orient="vertical",command=canvas.yview)
        inner=tk.Frame(canvas,bg=BG);inner.bind("<Configure>",lambda e:canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0),window=inner,anchor="nw",width=485);canvas.configure(yscrollcommand=scroll.set)
        canvas.pack(side="left",fill="both",expand=True,padx=(20,0));scroll.pack(side="right",fill="y")
        widgets={}
        for field in cfg["fields"]:
            key,label,typ=field[:3]
            tk.Label(inner,text=label,bg=BG,fg=TEXT,font=("Segoe UI",9,"bold")).pack(anchor="w",pady=(9,3))
            if typ=="choice":
                w=ttk.Combobox(inner,values=field[3],state="readonly")
                if key=="active": w.set("Activo")
                else: w.set(field[3][0])
            elif typ.startswith("fk_"):
                opts=self.fk_options(typ)
                values=[x[0] for x in opts]
                if typ=="fk_pet_optional": values=["(Sin mascota)"]+values
                w=ttk.Combobox(inner,values=values,state="readonly")
                if values: w.set(values[0])
                w._fk_options=opts
            else:
                w=ttk.Entry(inner,show="•" if typ=="password" else "")
                if typ=="date": w.insert(0,date.today().isoformat())
                if typ=="time": w.insert(0,"09:00")
            w.pack(fill="x",ipady=5)
            widgets[key]=(w,typ)
            if old and key in old.keys() and typ!="password":
                val=old[key]
                if typ=="choice" and key=="active": w.set("Activo" if val else "Inactivo")
                elif typ.startswith("fk_"):
                    opts=self.fk_options(typ)
                    if typ=="fk_pet_optional" and val is None: w.set("(Sin mascota)")
                    else:
                        for label2,id2 in opts:
                            if id2==val: w.set(label2);break
                else:
                    w.insert(0,str(val if val is not None else ""))
        def save():
            data={}
            for key,(w,typ) in widgets.items():
                value=w.get().strip()
                if typ.startswith("fk_"):
                    if typ=="fk_pet_optional" and value=="(Sin mascota)":
                        data[key]=None; continue
                    if not value and typ=="fk_pet_optional": data[key]=None;continue
                    opts=w._fk_options
                    match=next((i for label2,i in opts if label2==value),None)
                    if match is None:
                        messagebox.showerror("Dato requerido",f"Selecciona un valor válido para {key}.",parent=win);return
                    data[key]=match
                elif typ=="number":
                    if value and (not value.isdigit() or int(value)<0):
                        messagebox.showerror("Dato inválido","La edad debe ser un número entero igual o mayor que cero.",parent=win);return
                    data[key]=int(value) if value else None
                elif typ=="money":
                    try: data[key]=float(value.replace(",",""))
                    except: messagebox.showerror("Dato inválido","El monto debe ser numérico.",parent=win);return
                    if data[key]<0:
                        messagebox.showerror("Dato inválido","El monto no puede ser negativo.",parent=win);return
                elif typ=="choice":
                    data[key]= (1 if value=="Activo" else 0) if key=="active" else value
                elif typ=="password":
                    if value: data["password_hash"]=hash_password(value)
                    elif not old:
                        messagebox.showerror("Dato requerido","La contraseña es obligatoria para el nuevo empleado.",parent=win);return
                else: data[key]=value
            required=["full_name","phone"] if name=="Propietarios" else (["full_name","position","role","username"] if name=="Empleados" else [])
            if name=="Mascotas": required=["name","species","owner_id"]
            if name=="Citas": required=["pet_id","vet_id","appointment_date","appointment_time"]
            if name=="Consultas e historial": required=["pet_id","vet_id","consult_date","reason","diagnosis"]
            if name=="Pagos": required=["owner_id","description","amount","payment_date","method"]
            for k in required:
                if k not in data or data[k] in ("",None):
                    messagebox.showerror("Dato requerido",f"El campo {k} es obligatorio.",parent=win);return
            # Los campos únicos opcionales vacíos se guardan como NULL para permitir varios registros sin DUI/correo.
            for k in ("dui", "email"):
                if k in data and data[k] == "": data[k] = None
            for k in ("appointment_date","consult_date","payment_date"):
                if k in data:
                    try: datetime.strptime(data[k],"%Y-%m-%d")
                    except ValueError:
                        messagebox.showerror("Fecha inválida","Usa el formato AAAA-MM-DD, por ejemplo 2026-11-10.",parent=win);return
            if "appointment_time" in data:
                try: datetime.strptime(data["appointment_time"],"%H:%M")
                except ValueError:
                    messagebox.showerror("Hora inválida","Usa el formato HH:MM, por ejemplo 09:30.",parent=win);return
            if "email" in data and data["email"] and not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$",data["email"]):
                messagebox.showerror("Correo inválido","Escribe un correo electrónico válido.",parent=win);return
            if "phone" in data and data["phone"] and not re.match(r"^[0-9+() -]{7,20}$",data["phone"]):
                messagebox.showerror("Teléfono inválido","Revisa el número de teléfono.",parent=win);return
            if name=="Citas" and data.get("status")=="Programada":
                conflict=self.db.rows("""SELECT id FROM appointments WHERE vet_id=? AND appointment_date=? AND appointment_time=? AND status='Programada' AND id<>COALESCE(?, -1)""",
                    (data["vet_id"],data["appointment_date"],data["appointment_time"],record_id))
                if conflict:
                    messagebox.showerror("Horario ocupado","El veterinario ya tiene una cita programada en esa fecha y hora.",parent=win);return
            try:
                if name=="Empleados" and "password_hash" not in data and old:
                    data.pop("password_hash",None)
                if old:
                    if not data: return
                    keys=list(data)
                    self.db.run(f"UPDATE {table} SET "+",".join(k+"=?" for k in keys)+" WHERE id=?",tuple(data[k] for k in keys)+(record_id,))
                else:
                    keys=list(data)
                    self.db.run(f"INSERT INTO {table} ("+",".join(keys)+") VALUES ("+",".join("?" for _ in keys)+")",tuple(data[k] for k in keys))
                messagebox.showinfo("Guardado","La información se guardó correctamente.",parent=win)
                win.destroy();refresh()
            except sqlite3.IntegrityError as e:
                messagebox.showerror("No se pudo guardar","El dato puede estar duplicado o relacionado con otro registro.\nDetalle: "+str(e),parent=win)
            except sqlite3.Error as e:
                messagebox.showerror("Error de base de datos",str(e),parent=win)
        tk.Button(inner,text="GUARDAR REGISTRO",command=save,bg=GREEN,fg="white",relief="flat",
                  font=("Segoe UI",10,"bold"),pady=12,cursor="hand2").pack(fill="x",pady=24)

    def delete_record(self,name,record_id,refresh):
        if record_id is None:return
        if name=="Empleados" and self.user["role"]!="Administrador":
            messagebox.showerror("Permiso denegado","Solo el administrador puede eliminar empleados.");return
        if not messagebox.askyesno("Confirmar eliminación","¿Seguro que deseas eliminar este registro?\nEsta acción no se puede deshacer."):return
        table=MODULES[name]["table"]
        try:
            self.db.run(f"DELETE FROM {table} WHERE id=?",(record_id,))
            refresh()
        except sqlite3.IntegrityError:
            messagebox.showerror("No se puede eliminar","Este registro está relacionado con otros datos. Primero revisa sus citas, mascotas, consultas o pagos.")
        except sqlite3.Error as e:
            messagebox.showerror("Error",str(e))

if __name__=="__main__":
    app=HuellitasApp()
    app.mainloop()
