import json
import os
import tempfile
import unittest

from reservation_system import ReservationSystem


class TestReservationSystem(unittest.TestCase):
    """Pruebas unitarias para ReservationSystem."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.system = ReservationSystem(data_dir=self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_crear_y_obtener_hotel(self):
        hotel_id = self.system.crear_hotel("Hotel A", "Puebla", 10)
        hotel = self.system.obtener_hotel(hotel_id)
        self.assertIsNotNone(hotel)
        self.assertEqual(hotel.hotel_id, hotel_id)
        self.assertEqual(hotel.habitaciones_disponibles, 10)

    def test_modificar_hotel(self):
        hotel_id = self.system.crear_hotel("Hotel A", "Puebla", 10)
        ok = self.system.modificar_hotel(hotel_id, nombre="Hotel B")
        self.assertTrue(ok)
        hotel = self.system.obtener_hotel(hotel_id)
        self.assertEqual(hotel.nombre, "Hotel B")

    def test_eliminar_hotel(self):
        hotel_id = self.system.crear_hotel("Hotel A", "Puebla", 10)
        ok = self.system.eliminar_hotel(hotel_id)
        self.assertTrue(ok)
        self.assertIsNone(self.system.obtener_hotel(hotel_id))

    def test_crear_y_obtener_cliente(self):
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        cliente = self.system.obtener_cliente(cid)
        self.assertIsNotNone(cliente)
        self.assertEqual(cliente.customer_id, cid)

    def test_modificar_cliente(self):
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        ok = self.system.modificar_cliente(cid, email="ana2@test.com")
        self.assertTrue(ok)
        cliente = self.system.obtener_cliente(cid)
        self.assertEqual(cliente.email, "ana2@test.com")

    def test_eliminar_cliente(self):
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        ok = self.system.eliminar_cliente(cid)
        self.assertTrue(ok)
        self.assertIsNone(self.system.obtener_cliente(cid))

    def test_crear_reservacion_descuenta_disponibilidad(self):
        hid = self.system.crear_hotel("Hotel A", "Puebla", 10)
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        rid = self.system.crear_reservacion(
            customer_id=cid,
            hotel_id=hid,
            habitaciones=3,
            fecha_inicio="2026-02-22",
            fecha_fin="2026-02-24",
        )
        self.assertIsInstance(rid, int)

        hotel = self.system.obtener_hotel(hid)
        self.assertEqual(hotel.habitaciones_disponibles, 7)

    def test_cancelar_reservacion_repone_disponibilidad(self):
        hid = self.system.crear_hotel("Hotel A", "Puebla", 5)
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        rid = self.system.crear_reservacion(
            cid, hid, 2, "2026-02-22", "2026-02-24"
        )
        ok = self.system.cancelar_reservacion(rid)
        self.assertTrue(ok)

        hotel = self.system.obtener_hotel(hid)
        self.assertEqual(hotel.habitaciones_disponibles, 5)

    # ---------------- NEGATIVOS (>= 5) ----------------

    def test_reservacion_sin_cliente_falla(self):
        hid = self.system.crear_hotel("Hotel A", "Puebla", 5)
        with self.assertRaises(ValueError):
            self.system.crear_reservacion(
                customer_id=999,
                hotel_id=hid,
                habitaciones=1,
                fecha_inicio="2026-02-22",
                fecha_fin="2026-02-23",
            )

    def test_reservacion_sin_hotel_falla(self):
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        with self.assertRaises(ValueError):
            self.system.crear_reservacion(
                customer_id=cid,
                hotel_id=999,
                habitaciones=1,
                fecha_inicio="2026-02-22",
                fecha_fin="2026-02-23",
            )

    def test_reservacion_sin_disponibilidad_falla(self):
        hid = self.system.crear_hotel("Hotel A", "Puebla", 1)
        cid = self.system.crear_cliente("Ana", "ana@test.com")
        with self.assertRaises(ValueError):
            self.system.crear_reservacion(
                cid, hid, 2, "2026-02-22", "2026-02-23"
            )

    def test_cancelar_reservacion_inexistente(self):
        ok = self.system.cancelar_reservacion(999)
        self.assertFalse(ok)

    def test_json_corrupto_no_detiene(self):
        # Rompemos hotels.json
        hotels_path = os.path.join(self.tmp.name, "hotels.json")
        with open(hotels_path, "w", encoding="utf-8") as f_out:
            f_out.write("{not json}")

        # Debe regresar None, pero no explotar
        self.assertIsNone(self.system.obtener_hotel(1))

    def test_registro_hotel_incompleto_no_revienta(self):
        # Metemos un hotel corrupto (faltan llaves)
        hotels_path = os.path.join(self.tmp.name, "hotels.json")
        with open(hotels_path, "w", encoding="utf-8") as f_out:
            json.dump([{"id": 1, "nombre": "Hotel X"}], f_out)

        # Debe detectar error y regresar None
        hotel = self.system.obtener_hotel(1)
        self.assertIsNone(hotel)

    def test_registro_cliente_tipo_incorrecto_no_revienta(self):
        customers_path = os.path.join(self.tmp.name, "customers.json")
        with open(customers_path, "w", encoding="utf-8") as f_out:
            json.dump([{"id": "uno", "nombre": 123, "email": []}], f_out)

        cliente = self.system.obtener_cliente(1)
        self.assertIsNone(cliente)


if __name__ == "__main__":
    unittest.main()
