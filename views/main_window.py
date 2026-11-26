
"""Vista: interfaz Tkinter adaptable para Huellitas Veterinaria."""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date

from models.modules import MODULES

BG = "#F4F7F4"
PANEL = "#FFFFFF"
GREEN = "#246B52"
DARK = "#183D32"
MINT = "#E4F1EA"
TEXT = "#23352E"
MUTED = "#718078"
RED = "#B94141"


class HuellitasWindow(tk.Tk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.title("Huellitas | Gestión Veterinaria")
        self.geometry("1180x760")
        self.minsize(760, 560)
        self.configure(bg=BG)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

        self._configure_styles()
        self.show_login()

    def _configure_styles(self):
        style = ttk.Style(self)

        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure(
            "Treeview",
            background="white",
            fieldbackground="white",
            foreground=TEXT,
            rowheight=30,
            borderwidth=0,
            font=("Segoe UI", 9)
        )

        style.configure(
            "Treeview.Heading",
            background=MINT,
            foreground=DARK,
            font=("Segoe UI", 9, "bold"),
            relief="flat"
        )

        style.map(
            "Treeview",
            background=[("selected", GREEN)],
            foreground=[("selected", "white")]
        )

        style.configure("TCombobox", padding=6)
        style.configure("TEntry", padding=7)

    def on_close(self):
        self.controller.db.close()
        self.destroy()

    def clear(self):
        for widget in self.winfo_children():
            widget.destroy()

    def show_login(self):
        self.clear()

        outer = tk.Frame(self, bg=BG)
        outer.pack(fill="both", expand=True)

        card = tk.Frame(
            outer,
            bg=PANEL,
            padx=34,
            pady=30,
            highlightthickness=1,
            highlightbackground="#DCE8DF"
        )

        card.place(
            relx=.5,
            rely=.5,
            anchor="center",
            relwidth=.82,
            relheight=.78
        )

        card.configure(width=440, height=520)
        card.pack_propagate(False)

        tk.Label(
            card,
            text="🐾",
            font=("Segoe UI Emoji", 36),
            bg=PANEL,
            fg=GREEN
        ).pack(pady=(5, 0))

        tk.Label(
            card,
            text="HUELLITAS",
            font=("Segoe UI", 23, "bold"),
            bg=PANEL,
            fg=DARK
        ).pack()

        tk.Label(
            card,
            text="Sistema de Gestión Veterinaria",
            font=("Segoe UI", 10),
            bg=PANEL,
            fg=MUTED
        ).pack(pady=(0, 25))

        tk.Label(
            card,
            text="Usuario",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        username = ttk.Entry(card)
        username.pack(fill="x", pady=(6, 15), ipady=3)
        username.insert(0, "admin")

        tk.Label(
            card,
            text="Contraseña",
            bg=PANEL,
            fg=TEXT,
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w")

        password = ttk.Entry(card, show="•")
        password.pack(fill="x", pady=(6, 18), ipady=3)

        def login(event=None):
            if self.controller.login(username.get(), password.get()):
                self.show_dashboard()
            else:
                messagebox.showerror(
                    "Acceso denegado",
                    "Usuario o contraseña incorrectos, o cuenta inactiva.",
                    parent=self
                )
                password.delete(0, "end")
                password.focus_set()

        tk.Button(
            card,
            text="INICIAR SESIÓN",
            command=login,
            bg=GREEN,
            fg="white",
            activebackground=DARK,
            activeforeground="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            cursor="hand2",
            pady=12
        ).pack(fill="x")

        tk.Label(
            card,
            text="Acceso inicial: admin / Huellitas2026!",
            bg=PANEL,
            fg=MUTED,
            font=("Segoe UI", 8)
        ).pack(pady=18)

        password.bind("<Return>", login)
        username.bind("<Return>", lambda _e: password.focus_set())
        username.focus_set()

    def _header(self, title, back_command=None):
        top = tk.Frame(self, bg=DARK)
        top.pack(fill="x")

        if back_command:
            tk.Button(
                top,
                text="← Inicio",
                command=back_command,
                bg=DARK,
                fg="white",
                relief="flat",
                font=("Segoe UI", 10),
                cursor="hand2"
            ).pack(side="left", padx=16, pady=15)

        tk.Label(
            top,
            text=title,
            bg=DARK,
            fg="white",
            font=("Segoe UI", 17, "bold")
        ).pack(side="left", padx=12, pady=14)

        if self.controller.user:
            tk.Label(
                top,
                text=self.controller.user["full_name"],
                bg=DARK,
                fg="#D5E8DC"
            ).pack(side="right", padx=18)

        return top

    def show_dashboard(self):
        self.clear()

        self._header("🐾  HUELLITAS")

        body = tk.Frame(self, bg=BG)
        body.pack(fill="both", expand=True)

        side = tk.Frame(body, bg="#EAF2EC", width=195)
        side.pack(side="left", fill="y")
        side.pack_propagate(False)

        tk.Label(
            side,
            text="MENÚ PRINCIPAL",
            bg="#EAF2EC",
            fg=MUTED,
            font=("Segoe UI", 9, "bold")
        ).pack(anchor="w", padx=15, pady=(22, 10))

        allowed = self.controller.allowed_modules()

        for name in allowed:
            tk.Button(
                side,
                text="  " + name,
                anchor="w",
                command=lambda n=name: self.show_module(n),
                bg="#EAF2EC",
                fg=DARK,
                activebackground=MINT,
                relief="flat",
                font=("Segoe UI", 9),
                cursor="hand2",
                pady=9
            ).pack(fill="x", padx=7)

        tk.Button(
            side,
            text="  Cerrar sesión",
            anchor="w",
            command=self.logout,
            bg="#EAF2EC",
            fg=RED,
            relief="flat",
            font=("Segoe UI", 9),
            cursor="hand2",
            pady=9
        ).pack(side="bottom", fill="x", padx=7, pady=15)

        content = tk.Frame(body, bg=BG, padx=24, pady=24)
        content.pack(side="left", fill="both", expand=True)

        tk.Label(
            content,
            text="Panel de control",
            bg=BG,
            fg=DARK,
            font=("Segoe UI", 22, "bold")
        ).pack(anchor="w")

        tk.Label(
            content,
            text="Resumen general de Clínica Veterinaria Huellitas",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 10)
        ).pack(anchor="w", pady=(4, 20))

        stats_frame = tk.Frame(content, bg=BG)
        stats_frame.pack(fill="x")

        stats = self.controller.get_stats()
        cards = []

        for label, value in stats.items():
            box = tk.Frame(
                stats_frame,
                bg=PANEL,
                padx=15,
                pady=16,
                highlightbackground="#DCE8DF",
                highlightthickness=1
            )

            tk.Label(
                box,
                text=label,
                bg=PANEL,
                fg=MUTED,
                font=("Segoe UI", 9)
            ).pack(anchor="w")

            tk.Label(
                box,
                text=str(value),
                bg=PANEL,
                fg=GREEN,
                font=("Segoe UI", 23, "bold")
            ).pack(anchor="w", pady=(5, 0))

            cards.append(box)

        def arrange_cards(_event=None):
            width = max(stats_frame.winfo_width(), 300)
            columns = 2 if width < 720 else 4

            for index, box in enumerate(cards):
                box.grid_forget()
                box.grid(
                    row=index // columns,
                    column=index % columns,
                    sticky="nsew",
                    padx=5,
                    pady=5
                )

            for col in range(columns):
                stats_frame.columnconfigure(col, weight=1)

        stats_frame.bind("<Configure>", arrange_cards)
        self.after(80, arrange_cards)

        tk.Label(
            content,
            text="Accesos rápidos",
            bg=BG,
            fg=DARK,
            font=("Segoe UI", 14, "bold")
        ).pack(anchor="w", pady=(24, 10))

        quick = tk.Frame(content, bg=BG)
        quick.pack(fill="x")

        quick_buttons = []

        for name in (
            "Propietarios",
            "Mascotas",
            "Citas",
            "Consultas e historial"
        ):
            if name in allowed:
                button = tk.Button(
                    quick,
                    text=name,
                    command=lambda n=name: self.show_module(n),
                    bg=GREEN,
                    fg="white",
                    activebackground=DARK,
                    relief="flat",
                    padx=12,
                    pady=10,
                    cursor="hand2"
                )

                quick_buttons.append(button)

        # Reorganiza los accesos rápidos según el ancho disponible.
        def arrange_quick_buttons(_event=None):
            width = max(quick.winfo_width(), 300)

            if width < 430:
                columns = 1
            elif width < 700:
                columns = 2
            else:
                columns = 4

            for index, button in enumerate(quick_buttons):
                button.grid_forget()
                button.grid(
                    row=index // columns,
                    column=index % columns,
                    sticky="ew",
                    padx=4,
                    pady=4
                )

            for column in range(columns):
                quick.columnconfigure(column, weight=1)

        quick.bind("<Configure>", arrange_quick_buttons)
        self.after(100, arrange_quick_buttons)

        tk.Label(
            content,
            text="La información se guarda localmente en huellitas.db.",
            bg=BG,
            fg=MUTED,
            font=("Segoe UI", 9)
        ).pack(anchor="w", side="bottom", pady=8)

    def logout(self):
        self.controller.logout()
        self.show_login()

    def show_module(self, name):
        if not self.controller.can_access(name):
            messagebox.showerror(
                "Permiso denegado",
                "No tienes acceso a este módulo.",
                parent=self
            )
            return

        self.clear()
        self._header(name, self.show_dashboard)

        area = tk.Frame(self, bg=BG, padx=18, pady=18)
        area.pack(fill="both", expand=True)

        toolbar = tk.Frame(area, bg=BG)
        toolbar.pack(fill="x", pady=(0, 12))

        search = ttk.Entry(toolbar)
        search.pack(side="left", fill="x", expand=True, ipady=4)

        tk.Label(
            toolbar,
            text="Buscar en los registros",
            bg=BG,
            fg=MUTED
        ).pack(side="left", padx=10)

        table_frame = tk.Frame(area, bg=PANEL)
        table_frame.pack(fill="both", expand=True)

        config = MODULES[name]
        columns = config["columns"]

        tree = ttk.Treeview(
            table_frame,
            columns=columns,
            show="headings"
        )

        for column, label in zip(columns, config["labels"]):
            tree.heading(column, text=label)
            tree.column(
                column,
                width=130,
                minwidth=80,
                anchor="w",
                stretch=True
            )

        vertical = ttk.Scrollbar(
            table_frame,
            orient="vertical",
            command=tree.yview
        )

        horizontal = ttk.Scrollbar(
            table_frame,
            orient="horizontal",
            command=tree.xview
        )

        tree.configure(
            yscrollcommand=vertical.set,
            xscrollcommand=horizontal.set
        )

        tree.grid(row=0, column=0, sticky="nsew")
        vertical.grid(row=0, column=1, sticky="ns")
        horizontal.grid(row=1, column=0, sticky="ew")

        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)

        def load_rows(term=""):
            tree.delete(*tree.get_children())

            for row in self.controller.query_module(name):
                values = [
                    self.controller.display_value(row, col)
                    for col in columns
                ]

                if (
                    not term
                    or term.casefold() in " ".join(map(str, values)).casefold()
                ):
                    tree.insert(
                        "",
                        "end",
                        iid=str(row["id"]),
                        values=values
                    )

        def selected_id():
            selection = tree.selection()

            if not selection:
                messagebox.showwarning(
                    "Selecciona un registro",
                    "Selecciona una fila de la tabla primero.",
                    parent=self
                )
                return None

            return int(selection[0])

        def refresh():
            load_rows(search.get().strip())

        search.bind("<KeyRelease>", lambda _event: refresh())

        # Barra de botones adaptable al tamaño de la ventana.
        actions = tk.Frame(area, bg=BG)
        actions.pack(fill="x", pady=(12, 0))

        action_buttons = [
            tk.Button(
                actions,
                text="+ Nuevo registro",
                command=lambda: self.edit_record(name, None, refresh),
                bg=GREEN,
                fg="white",
                activebackground=DARK,
                relief="flat",
                padx=13,
                pady=9,
                cursor="hand2"
            ),

            tk.Button(
                actions,
                text="Editar seleccionado",
                command=lambda: self.edit_record(
                    name,
                    selected_id(),
                    refresh
                ),
                bg="#DCEBE1",
                fg=DARK,
                relief="flat",
                padx=13,
                pady=9,
                cursor="hand2"
            ),

            tk.Button(
                actions,
                text="Eliminar seleccionado",
                command=lambda: self.delete_record(
                    name,
                    selected_id(),
                    refresh
                ),
                bg="#F8E6E6",
                fg=RED,
                relief="flat",
                padx=13,
                pady=9,
                cursor="hand2"
            ),

            tk.Button(
                actions,
                text="Actualizar",
                command=refresh,
                bg="#E7ECE8",
                fg=DARK,
                relief="flat",
                padx=13,
                pady=9,
                cursor="hand2"
            )
        ]

        # Una columna en ventanas pequeñas, dos en medianas y cuatro en grandes.
        def arrange_action_buttons(_event=None):
            width = max(actions.winfo_width(), 320)

            if width < 480:
                columns = 1
            elif width < 850:
                columns = 2
            else:
                columns = 4

            for index, button in enumerate(action_buttons):
                button.grid_forget()
                button.grid(
                    row=index // columns,
                    column=index % columns,
                    sticky="ew",
                    padx=4,
                    pady=4
                )

            for column in range(columns):
                actions.columnconfigure(column, weight=1)

        actions.bind("<Configure>", arrange_action_buttons)
        self.after(100, arrange_action_buttons)

        refresh()

    def edit_record(self, name, record_id, refresh):

        if (
            record_id is None
            and name == "Empleados"
            and self.controller.user["role"] != "Administrador"
        ):
            messagebox.showerror(
                "Permiso denegado",
                "Solo el administrador puede crear empleados.",
                parent=self
            )
            return

        config = MODULES[name]
        table = config["table"]

        old = (
            self.controller.db.fetch_one(
                f"SELECT * FROM {table} WHERE id=?",
                (record_id,)
            )
            if record_id
            else None
        )

        if record_id and not old:
            messagebox.showerror(
                "Registro no encontrado",
                "Actualiza la tabla e inténtalo nuevamente.",
                parent=self
            )
            return

        window = tk.Toplevel(self)
        window.title(("Editar " if old else "Nuevo ") + name)
        window.configure(bg=BG)
        window.transient(self)
        window.grab_set()
        window.geometry("560x650")
        window.minsize(360, 420)

        window.columnconfigure(0, weight=1)
        window.rowconfigure(0, weight=0)
        window.rowconfigure(1, weight=1)
        window.rowconfigure(2, weight=0)

        tk.Label(
            window,
            text=("Editar registro" if old else "Registrar nuevo"),
            bg=BG,
            fg=DARK,
            font=("Segoe UI", 18, "bold")
        ).grid(
            row=0,
            column=0,
            sticky="w",
            padx=22,
            pady=(18, 3)
        )

        form_container = tk.Frame(window, bg=BG)
        form_container.grid(
            row=1,
            column=0,
            sticky="nsew",
            padx=18,
            pady=8
        )

        form_container.rowconfigure(0, weight=1)
        form_container.columnconfigure(0, weight=1)

        canvas = tk.Canvas(
            form_container,
            bg=BG,
            highlightthickness=0
        )

        scrollbar = ttk.Scrollbar(
            form_container,
            orient="vertical",
            command=canvas.yview
        )

        inner = tk.Frame(canvas, bg=BG)

        inner_id = canvas.create_window(
            (0, 0),
            window=inner,
            anchor="nw"
        )

        inner.bind(
            "<Configure>",
            lambda _e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.bind(
            "<Configure>",
            lambda e: canvas.itemconfigure(
                inner_id,
                width=e.width
            )
        )

        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        widgets = {}

        for field in config["fields"]:
            key, label, kind = field[:3]

            tk.Label(
                inner,
                text=label,
                bg=BG,
                fg=TEXT,
                font=("Segoe UI", 9, "bold")
            ).pack(anchor="w", pady=(9, 3))

            if kind == "choice":
                widget = ttk.Combobox(
                    inner,
                    values=field[3],
                    state="readonly"
                )

                widget.set(
                    "Activo" if key == "active" else field[3][0]
                )

            elif kind.startswith("fk_"):
                options = self.controller.fk_options(kind)
                values = [item[0] for item in options]

                if kind == "fk_pet_optional":
                    values = ["(Sin mascota)"] + values

                widget = ttk.Combobox(
                    inner,
                    values=values,
                    state="readonly"
                )

                if values:
                    widget.set(values[0])

                widget._fk_options = options

            else:
                widget = ttk.Entry(
                    inner,
                    show="•" if kind == "password" else ""
                )

                # Valores predeterminados únicamente al crear un registro.
                if not old and kind == "date":
                    widget.insert(0, date.today().isoformat())

                elif not old and kind == "time":
                    widget.insert(0, "09:00")

            widget.pack(fill="x", ipady=5)
            widgets[key] = (widget, kind)

            # Al editar se carga el valor anterior una sola vez.
            if old and key in old.keys() and kind != "password":
                value = old[key]

                if kind == "choice" and key == "active":
                    widget.set(
                        "Activo" if value else "Inactivo"
                    )

                elif kind.startswith("fk_"):

                    if (
                        kind == "fk_pet_optional"
                        and value is None
                    ):
                        widget.set("(Sin mascota)")

                    else:
                        for option_label, option_id in widget._fk_options:
                            if option_id == value:
                                widget.set(option_label)
                                break

                else:
                    widget.insert(
                        0,
                        str(value if value is not None else "")
                    )

        def save():
            data = {}

            for key, (widget, kind) in widgets.items():
                value = widget.get().strip()

                if kind.startswith("fk_"):

                    if (
                        kind == "fk_pet_optional"
                        and value in ("", "(Sin mascota)")
                    ):
                        data[key] = None
                        continue

                    match = next(
                        (
                            option_id
                            for option_label, option_id in widget._fk_options
                            if option_label == value
                        ),
                        None
                    )

                    if match is None:
                        messagebox.showerror(
                            "Dato requerido",
                            f"Selecciona un valor válido para {key}.",
                            parent=window
                        )
                        return

                    data[key] = match

                elif kind == "choice":
                    data[key] = (
                        1 if value == "Activo" else 0
                    ) if key == "active" else value

                else:
                    data[key] = value

            try:
                self.controller.save_record(
                    name,
                    record_id,
                    data
                )

                messagebox.showinfo(
                    "Guardado",
                    "La información se guardó correctamente.",
                    parent=window
                )

                window.destroy()
                refresh()

            except (ValueError, PermissionError) as exc:
                messagebox.showerror(
                    "No se pudo guardar",
                    str(exc),
                    parent=window
                )

        # El pie queda fuera del área desplazable para que Guardar
        # permanezca visible aunque el formulario sea más alto.
        footer = tk.Frame(window, bg=BG)
        footer.grid(
            row=2,
            column=0,
            sticky="ew",
            padx=20,
            pady=(5, 18)
        )

        tk.Button(
            footer,
            text="GUARDAR REGISTRO",
            command=save,
            bg=GREEN,
            fg="white",
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            pady=11,
            cursor="hand2"
        ).pack(fill="x")

    def delete_record(self, name, record_id, refresh):

        if record_id is None:
            return

        if not messagebox.askyesno(
            "Confirmar eliminación",
            "¿Seguro que deseas eliminar este registro?\n"
            "Esta acción no se puede deshacer.",
            parent=self
        ):
            return

        try:
            self.controller.delete_record(name, record_id)
            refresh()

        except (ValueError, PermissionError) as exc:
            messagebox.showerror(
                "No se puede eliminar",
                str(exc),
                parent=self
            )
