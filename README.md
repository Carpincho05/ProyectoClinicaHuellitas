# Huellitas - Sistema de Gestión para Clínica Veterinaria

Aplicación de escritorio desarrollada en Python con Tkinter y SQLite.

## Requisitos
- Windows 10/11
- Python 3.10 o superior (Tkinter normalmente viene incluido)
- No requiere instalar paquetes externos.

## Ejecutar
1. Extrae la carpeta `Huellitas_Veterinaria`.
2. Abre CMD o PowerShell dentro de esa carpeta.
3. Ejecuta: `python main.py`
4. Inicia sesión con:
   - Usuario: `admin`
   - Contraseña: `Huellitas2026!`
5. Cambia la contraseña del administrador desde el módulo Empleados: edita el registro del administrador y escribe una contraseña nueva.

## Módulos
- Propietarios: alta, consulta, edición y eliminación.
- Mascotas: registro relacionado con propietarios.
- Citas: programación, consulta, modificación y cancelación; evita dos citas programadas para el mismo veterinario en la misma fecha y hora.
- Consultas e historial: motivo, diagnóstico, observaciones y tratamiento.
- Empleados: administración de personal y cuentas de acceso.
- Pagos: registro de cobros por propietario y mascota.

## Roles
- Administrador: acceso a todos los módulos.
- Recepcionista: propietarios, mascotas, citas y pagos.
- Veterinario: mascotas, citas e historial clínico.

## Base de datos
Al iniciar por primera vez se crea automáticamente `huellitas.db` en la misma carpeta.
No borres ese archivo si deseas conservar los registros.
Realiza copias de seguridad periódicas copiando `huellitas.db` con el programa cerrado.

## Notas importantes
- Las fechas se escriben como AAAA-MM-DD (ejemplo: 2026-11-10).
- Las horas se escriben como HH:MM (ejemplo: 14:30).
- La cuenta inicial es de demostración académica. Cambia la contraseña antes de usar datos reales.
- El sistema es una base funcional académica; antes de un despliegue comercial se recomienda añadir copias automáticas, auditoría, cifrado de base de datos y pruebas de aceptación.
