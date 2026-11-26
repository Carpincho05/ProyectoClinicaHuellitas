"""Punto de entrada de Huellitas Veterinaria (arquitectura MVC)."""
from models.database import Database
from controllers.app_controller import AppController
from views.main_window import HuellitasWindow


def main():
    database = Database()
    controller = AppController(database)
    app = HuellitasWindow(controller)
    app.mainloop()


if __name__ == "__main__":
    main()
