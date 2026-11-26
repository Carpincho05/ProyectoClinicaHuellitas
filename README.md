# Huellitas Veterinaria – versión MVC

Esta versión reorganiza el sistema en **Modelo–Vista–Controlador (MVC)**, conserva SQLite y corrige el problema al editar fechas y horas.

## 1. Requisitos

- Python 3.10 o superior.
- Tkinter (normalmente se instala junto con Python).
- SQLite (incluido en Python).
- No necesita instalar paquetes externos.

## 2. Cómo ejecutar

1. Descomprime la carpeta `Huellitas_MVC`.
2. Abre esa carpeta en Visual Studio Code, PyCharm o desde el Explorador de Windows.
3. Abre una terminal dentro de `Huellitas_MVC`.
4. Ejecuta:

   ```powershell
   python main.py
   ```

5. Accede con la cuenta inicial si la base de datos no tenía ya una cuenta de administrador:
   - Usuario: `admin`
   - Contraseña: `Huellitas2026!`

La base de datos que utiliza esta versión es `Huellitas_MVC/huellitas.db`.

## 3. Estructura MVC

```text
Huellitas_MVC/
│   main.py
│   huellitas.db
│   README.md
│   requirements.txt
│
├── models/
│   ├── __init__.py
│   ├── database.py
│   └── modules.py
│
├── controllers/
│   ├── __init__.py
│   └── app_controller.py
│
└── views/
    ├── __init__.py
    └── main_window.py
```

### Modelo (`models/`)

- `database.py`: crea y administra la conexión SQLite, las tablas, las consultas y el hash de contraseñas.
- `modules.py`: define los módulos, columnas y campos que muestran los formularios.

### Vista (`views/`)

- `main_window.py`: contiene las ventanas Tkinter, formularios, tablas, botones, menú y diseño adaptable. La vista solicita operaciones al controlador; no contiene consultas SQL de negocio.

### Controlador (`controllers/`)

- `app_controller.py`: valida credenciales, permisos, datos, fechas, horas, montos y conflictos de citas; coordina las operaciones entre la vista y el modelo.

### Inicio (`main.py`)

Crea el modelo de base de datos, el controlador y la ventana principal.


## 4. Pruebas

Desde la carpeta del proyecto ejecuta:

```powershell
python -m compileall -q .
```

La comprobación anterior verifica sintaxis. También se debe abrir la aplicación en Windows y probar inicio de sesión, altas, ediciones, eliminaciones y permisos con cuentas de cada rol. La interfaz gráfica no se puede certificar únicamente con la compilación de los archivos.
