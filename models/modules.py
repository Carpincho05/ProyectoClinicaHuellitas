"""Configuración de módulos, columnas y campos del sistema."""
MODULES = {
    "Propietarios": {
        "table": "owners", "columns": ["id", "full_name", "dui", "phone", "email", "address"],
        "labels": ["ID", "Nombre completo", "DUI", "Teléfono", "Correo", "Dirección"],
        "fields": [("full_name", "Nombre completo", "text"), ("dui", "DUI", "text"), ("phone", "Teléfono", "text"), ("email", "Correo", "text"), ("address", "Dirección", "text")]
    },
    "Mascotas": {
        "table": "pets", "columns": ["id", "name", "species", "breed", "age", "sex", "owner_id"],
        "labels": ["ID", "Nombre", "Especie", "Raza", "Edad", "Sexo", "Propietario"],
        "fields": [("name", "Nombre", "text"), ("species", "Especie", "choice", ["Perro", "Gato", "Ave", "Conejo", "Otro"]), ("breed", "Raza", "text"), ("age", "Edad (años)", "number"), ("sex", "Sexo", "choice", ["Macho", "Hembra", "No especificado"]), ("owner_id", "Propietario", "fk_owner")]
    },
    "Citas": {
        "table": "appointments", "columns": ["id", "pet_id", "vet_id", "appointment_date", "appointment_time", "reason", "status"],
        "labels": ["ID", "Mascota", "Veterinario", "Fecha", "Hora", "Motivo", "Estado"],
        "fields": [("pet_id", "Mascota", "fk_pet"), ("vet_id", "Veterinario", "fk_vet"), ("appointment_date", "Fecha (AAAA-MM-DD)", "date"), ("appointment_time", "Hora (HH:MM)", "time"), ("reason", "Motivo", "text"), ("status", "Estado", "choice", ["Programada", "Atendida", "Cancelada"])]
    },
    "Consultas e historial": {
        "table": "consultations", "columns": ["id", "pet_id", "vet_id", "consult_date", "reason", "diagnosis", "observations", "treatment"],
        "labels": ["ID", "Mascota", "Veterinario", "Fecha", "Motivo", "Diagnóstico", "Observaciones", "Tratamiento"],
        "fields": [("pet_id", "Mascota", "fk_pet"), ("vet_id", "Veterinario", "fk_vet"), ("consult_date", "Fecha (AAAA-MM-DD)", "date"), ("reason", "Motivo", "text"), ("diagnosis", "Diagnóstico", "text"), ("observations", "Observaciones", "text"), ("treatment", "Tratamiento", "text")]
    },
    "Empleados": {
        "table": "employees", "columns": ["id", "full_name", "phone", "email", "position", "role", "username", "active"],
        "labels": ["ID", "Nombre", "Teléfono", "Correo", "Cargo", "Rol", "Usuario", "Activo"],
        "fields": [("full_name", "Nombre completo", "text"), ("phone", "Teléfono", "text"), ("email", "Correo", "text"), ("position", "Cargo", "text"), ("role", "Rol", "choice", ["Administrador", "Recepcionista", "Veterinario"]), ("username", "Usuario", "text"), ("password", "Contraseña (solo al crear/cambiar)", "password"), ("active", "Estado", "choice", ["Activo", "Inactivo"])]
    },
    "Pagos": {
        "table": "payments", "columns": ["id", "owner_id", "pet_id", "description", "amount", "payment_date", "method", "status"],
        "labels": ["ID", "Propietario", "Mascota", "Descripción", "Monto", "Fecha", "Método", "Estado"],
        "fields": [("owner_id", "Propietario", "fk_owner"), ("pet_id", "Mascota (opcional)", "fk_pet_optional"), ("description", "Descripción", "text"), ("amount", "Monto ($)", "money"), ("payment_date", "Fecha (AAAA-MM-DD)", "date"), ("method", "Método", "choice", ["Efectivo", "Tarjeta", "Transferencia"]), ("status", "Estado", "choice", ["Pagado", "Pendiente", "Anulado"])]
    }
}
