"""Pruebas básicas del controlador; ejecutar: python -m unittest discover -s tests."""
import tempfile
import unittest
from pathlib import Path

from models.database import Database
from controllers.app_controller import AppController


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db = Database(Path(self.temp_dir.name) / "test.db")
        self.controller = AppController(self.db)
        self.assertTrue(self.controller.login("admin", "Huellitas2026!"))

    def tearDown(self):
        self.db.close()
        self.temp_dir.cleanup()

    def test_admin_can_access_all_modules(self):
        self.assertEqual(len(self.controller.allowed_modules()), 6)

    def test_invalid_date_is_rejected(self):
        with self.assertRaises(ValueError):
            self.controller.save_record("Citas", None, {
                "pet_id": 1, "vet_id": 1, "appointment_date": "2026-99-99",
                "appointment_time": "09:00", "reason": "Control", "status": "Programada"
            })

    def test_negative_amount_is_rejected(self):
        with self.assertRaises(ValueError):
            self.controller.save_record("Pagos", None, {
                "owner_id": 1, "pet_id": None, "description": "Consulta",
                "amount": "-10", "payment_date": "2026-11-23",
                "method": "Efectivo", "status": "Pagado"
            })


if __name__ == "__main__":
    unittest.main()
