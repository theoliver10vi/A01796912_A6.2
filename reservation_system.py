#!/usr/bin/env python3
"""
Actividad 6.2 - Reservation System

Implementa un sistema simple de reservaciones con persistencia en JSON.

Clases:
- Hotel
- Customer
- Reservation

Requisitos clave:
- Manejo de errores en datos inválidos (no se detiene el programa).
- Persistencia en archivos JSON (carpeta data/).
- Pruebas unitarias con unittest (ver tests/).
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Any


DATA_DIR = "data"
HOTELS_FILE = "hotels.json"
CUSTOMERS_FILE = "customers.json"
RESERVATIONS_FILE = "reservations.json"


def _asegurar_directorio_data(data_dir: str) -> None:
    """Crea el directorio de datos si no existe."""
    os.makedirs(data_dir, exist_ok=True)


def _ruta(data_dir: str, filename: str) -> str:
    """Devuelve la ruta completa de un archivo dentro del data_dir."""
    return os.path.join(data_dir, filename)


def _leer_json_lista(path: str) -> list[dict[str, Any]]:
    """
    Lee un JSON y devuelve una lista de dicts.

    Si el archivo no existe, lo crea con [] y regresa [].
    Si el JSON está corrupto o no es lista, imprime error y regresa [].
    Si encuentra elementos no-dict, los omite e imprime error.
    """
    if not os.path.exists(path):
        try:
            with open(path, "w", encoding="utf-8") as f_out:
                json.dump([], f_out)
        except OSError as exc:
            print(f"ERROR: No se pudo crear archivo {path}: {exc}")
        return []

    try:
        with open(path, "r", encoding="utf-8") as f_in:
            data = json.load(f_in)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"ERROR: JSON inválido en {path}: {exc}")
        return []

    if not isinstance(data, list):
        print(f"ERROR: Se esperaba lista en {path}, pero llegó {type(data)}")
        return []

    registros: list[dict[str, Any]] = []
    for i, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            print(f"ERROR: Elemento #{i} no es dict en {path}, se omite.")
            continue
        registros.append(item)
    return registros


def _escribir_json_lista(path: str, data: list[dict[str, Any]]) -> None:
    """Escribe una lista de dicts como JSON (pretty)."""
    try:
        with open(path, "w", encoding="utf-8") as f_out:
            json.dump(data, f_out, ensure_ascii=False, indent=2)
    except OSError as exc:
        print(f"ERROR: No se pudo escribir {path}: {exc}")


def _siguiente_id(registros: list[dict[str, Any]]) -> int:
    """Calcula el siguiente id basado en el máximo id existente."""
    max_id = 0
    for reg in registros:
        value = reg.get("id")
        if isinstance(value, int) and value > max_id:
            max_id = value
    return max_id + 1


def _validar_str_no_vacio(valor: Any, campo: str) -> str:
    """Valida que un valor sea string no vacío."""
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{campo} debe ser un string no vacío.")
    return valor.strip()


def _validar_int_no_neg(valor: Any, campo: str) -> int:
    """Valida que un valor sea entero no negativo."""
    if isinstance(valor, bool):
        raise ValueError(f"{campo} inválido.")
    if not isinstance(valor, int) or valor < 0:
        raise ValueError(f"{campo} debe ser int >= 0.")
    return valor


def _validar_int_pos(valor: Any, campo: str) -> int:
    """Valida que un valor sea entero positivo (> 0)."""
    val = _validar_int_no_neg(valor, campo)
    if val <= 0:
        raise ValueError(f"{campo} debe ser int > 0.")
    return val


@dataclass(frozen=True)
class Hotel:
    """Entidad Hotel."""
    hotel_id: int
    nombre: str
    ubicacion: str
    habitaciones_total: int
    habitaciones_disponibles: int

    def to_dict(self) -> dict[str, Any]:
        """Convierte a dict serializable."""
        return {
            "id": self.hotel_id,
            "nombre": self.nombre,
            "ubicacion": self.ubicacion,
            "habitaciones_total": self.habitaciones_total,
            "habitaciones_disponibles": self.habitaciones_disponibles,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Hotel | None:
        """
        Construye un Hotel de forma segura.
        Si el dict está incompleto o mal tipado, imprime error y regresa None.
        """
        try:
            hotel_id = _validar_int_pos(data["id"], "hotel.id")
            nombre = _validar_str_no_vacio(data["nombre"], "hotel.nombre")
            ubicacion = _validar_str_no_vacio(
                data["ubicacion"],
                "hotel.ubicacion",
            )
            total = _validar_int_no_neg(
                data["habitaciones_total"], "hotel.habitaciones_total"
            )
            disp = _validar_int_no_neg(
                data["habitaciones_disponibles"],
                "hotel.habitaciones_disponibles",
            )
            if disp > total:
                raise ValueError("hotel.habitaciones_disponibles > total")
            return Hotel(hotel_id, nombre, ubicacion, total, disp)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: Registro de hotel inválido: {exc}")
            return None


@dataclass(frozen=True)
class Customer:
    """Entidad Customer."""
    customer_id: int
    nombre: str
    email: str

    def to_dict(self) -> dict[str, Any]:
        """Convierte a dict serializable."""
        return {
            "id": self.customer_id,
            "nombre": self.nombre,
            "email": self.email,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Customer | None:
        """Construye un Customer de forma segura."""
        try:
            cust_id = _validar_int_pos(data["id"], "customer.id")
            nombre = _validar_str_no_vacio(data["nombre"], "customer.nombre")
            email = _validar_str_no_vacio(data["email"], "customer.email")
            return Customer(cust_id, nombre, email)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: Registro de cliente inválido: {exc}")
            return None


@dataclass(frozen=True)
class Reservation:
    """Entidad Reservation."""
    reservation_id: int
    hotel_id: int
    customer_id: int
    habitaciones: int
    fecha_inicio: str
    fecha_fin: str
    estatus: str

    def to_dict(self) -> dict[str, Any]:
        """Convierte a dict serializable."""
        return {
            "id": self.reservation_id,
            "hotel_id": self.hotel_id,
            "customer_id": self.customer_id,
            "habitaciones": self.habitaciones,
            "fecha_inicio": self.fecha_inicio,
            "fecha_fin": self.fecha_fin,
            "estatus": self.estatus,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Reservation | None:
        """Construye una Reservation de forma segura."""
        try:
            res_id = _validar_int_pos(data["id"], "reservation.id")
            hotel_id = _validar_int_pos(
                data["hotel_id"],
                "reservation.hotel_id",
            )
            cust_id = _validar_int_pos(
                data["customer_id"], "reservation.customer_id"
            )
            habs = _validar_int_pos(
                data["habitaciones"],
                "reservation.habitaciones",
            )
            ini = _validar_str_no_vacio(
                data["fecha_inicio"],
                "reservation.fecha_inicio",
            )
            fin = _validar_str_no_vacio(
                data["fecha_fin"],
                "reservation.fecha_fin",
            )
            est = _validar_str_no_vacio(data["estatus"], "reservation.estatus")
            return Reservation(res_id, hotel_id, cust_id, habs, ini, fin, est)
        except (KeyError, TypeError, ValueError) as exc:
            print(f"ERROR: Registro de reservación inválido: {exc}")
            return None


class ReservationSystem:
    """Orquestador con operaciones CRUD y persistencia."""

    def __init__(self, data_dir: str = DATA_DIR) -> None:
        self._data_dir = data_dir
        _asegurar_directorio_data(self._data_dir)
        self._hotels_path = _ruta(self._data_dir, HOTELS_FILE)
        self._customers_path = _ruta(self._data_dir, CUSTOMERS_FILE)
        self._reservations_path = _ruta(self._data_dir, RESERVATIONS_FILE)

        # Asegura que existan los archivos base
        _leer_json_lista(self._hotels_path)
        _leer_json_lista(self._customers_path)
        _leer_json_lista(self._reservations_path)

    # ---------------- Hotels ----------------

    def crear_hotel(
        self,
        nombre: str,
        ubicacion: str,
        habitaciones_total: int,
    ) -> int:
        """Crea un hotel y regresa su id."""
        nombre = _validar_str_no_vacio(nombre, "nombre")
        ubicacion = _validar_str_no_vacio(ubicacion, "ubicacion")
        total = _validar_int_pos(habitaciones_total, "habitaciones_total")

        hoteles = _leer_json_lista(self._hotels_path)
        new_id = _siguiente_id(hoteles)
        hotel = Hotel(new_id, nombre, ubicacion, total, total)
        hoteles.append(hotel.to_dict())
        _escribir_json_lista(self._hotels_path, hoteles)
        return new_id

    def eliminar_hotel(self, hotel_id: int) -> bool:
        """Elimina un hotel por id. True si lo eliminó."""
        hotel_id = _validar_int_pos(hotel_id, "hotel_id")
        hoteles = _leer_json_lista(self._hotels_path)
        before = len(hoteles)
        hoteles = [h for h in hoteles if h.get("id") != hotel_id]
        _escribir_json_lista(self._hotels_path, hoteles)
        return len(hoteles) < before

    def obtener_hotel(self, hotel_id: int) -> Hotel | None:
        """Obtiene un hotel por id (parseo seguro)."""
        hotel_id = _validar_int_pos(hotel_id, "hotel_id")
        hoteles = _leer_json_lista(self._hotels_path)
        for h in hoteles:
            if h.get("id") == hotel_id:
                hotel = Hotel.from_dict(h)
                if hotel is None:
                    print("ERROR: Hotel corrupto, se omite.")
                return hotel
        return None

    def modificar_hotel(
        self,
        hotel_id: int,
        nombre: str | None = None,
        ubicacion: str | None = None,
    ) -> bool:
        """
        Modifica campos básicos de un hotel.
        No modifica totales/disponibles aquí (eso lo maneja reservación).
        """
        hotel_id = _validar_int_pos(hotel_id, "hotel_id")
        hoteles = _leer_json_lista(self._hotels_path)

        cambiado = False
        for h in hoteles:
            if h.get("id") != hotel_id:
                continue

            if nombre is not None:
                h["nombre"] = _validar_str_no_vacio(nombre, "nombre")
                cambiado = True

            if ubicacion is not None:
                h["ubicacion"] = _validar_str_no_vacio(ubicacion, "ubicacion")
                cambiado = True

        if cambiado:
            _escribir_json_lista(self._hotels_path, hoteles)
        return cambiado

    # ---------------- Customers ----------------

    def crear_cliente(self, nombre: str, email: str) -> int:
        """Crea un cliente y regresa su id."""
        nombre = _validar_str_no_vacio(nombre, "nombre")
        email = _validar_str_no_vacio(email, "email")

        clientes = _leer_json_lista(self._customers_path)
        new_id = _siguiente_id(clientes)
        cliente = Customer(new_id, nombre, email)
        clientes.append(cliente.to_dict())
        _escribir_json_lista(self._customers_path, clientes)
        return new_id

    def eliminar_cliente(self, customer_id: int) -> bool:
        """Elimina un cliente por id. True si lo eliminó."""
        customer_id = _validar_int_pos(customer_id, "customer_id")
        clientes = _leer_json_lista(self._customers_path)
        before = len(clientes)
        clientes = [c for c in clientes if c.get("id") != customer_id]
        _escribir_json_lista(self._customers_path, clientes)
        return len(clientes) < before

    def obtener_cliente(self, customer_id: int) -> Customer | None:
        """Obtiene un cliente por id (parseo seguro)."""
        customer_id = _validar_int_pos(customer_id, "customer_id")
        clientes = _leer_json_lista(self._customers_path)
        for c in clientes:
            if c.get("id") == customer_id:
                cliente = Customer.from_dict(c)
                if cliente is None:
                    print("ERROR: Cliente corrupto, se omite.")
                return cliente
        return None

    def modificar_cliente(
        self,
        customer_id: int,
        nombre: str | None = None,
        email: str | None = None,
    ) -> bool:
        """Modifica campos de un cliente."""
        customer_id = _validar_int_pos(customer_id, "customer_id")
        clientes = _leer_json_lista(self._customers_path)

        cambiado = False
        for c in clientes:
            if c.get("id") != customer_id:
                continue

            if nombre is not None:
                c["nombre"] = _validar_str_no_vacio(nombre, "nombre")
                cambiado = True

            if email is not None:
                c["email"] = _validar_str_no_vacio(email, "email")
                cambiado = True

        if cambiado:
            _escribir_json_lista(self._customers_path, clientes)
        return cambiado

    # ---------------- Reservations ----------------

    def crear_reservacion(
        self,
        customer_id: int,
        hotel_id: int,
        habitaciones: int,
        fecha_inicio: str,
        fecha_fin: str,
    ) -> int:
        """
        Crea una reservación y descuenta disponibilidad del hotel.

        Lanza ValueError si hotel/cliente no existen o no hay disponibilidad.
        """
        customer_id = _validar_int_pos(customer_id, "customer_id")
        hotel_id = _validar_int_pos(hotel_id, "hotel_id")
        habitaciones = _validar_int_pos(habitaciones, "habitaciones")
        fecha_inicio = _validar_str_no_vacio(fecha_inicio, "fecha_inicio")
        fecha_fin = _validar_str_no_vacio(fecha_fin, "fecha_fin")

        if self.obtener_cliente(customer_id) is None:
            raise ValueError("El cliente no existe.")

        hotel = self.obtener_hotel(hotel_id)
        if hotel is None:
            raise ValueError("El hotel no existe o está corrupto.")

        if hotel.habitaciones_disponibles < habitaciones:
            raise ValueError("No hay habitaciones disponibles suficientes.")

        # Actualiza hotel (descuenta disponibilidad)
        hoteles = _leer_json_lista(self._hotels_path)
        for h in hoteles:
            if h.get("id") == hotel_id:
                disp = h.get("habitaciones_disponibles")
                if not isinstance(disp, int):
                    raise ValueError("Hotel corrupto: disponibles inválidas.")
                h["habitaciones_disponibles"] = disp - habitaciones
        _escribir_json_lista(self._hotels_path, hoteles)

        # Crea reservación
        reservaciones = _leer_json_lista(self._reservations_path)
        new_id = _siguiente_id(reservaciones)
        reserva = Reservation(
            reservation_id=new_id,
            hotel_id=hotel_id,
            customer_id=customer_id,
            habitaciones=habitaciones,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            estatus="activa",
        )
        reservaciones.append(reserva.to_dict())
        _escribir_json_lista(self._reservations_path, reservaciones)
        return new_id

    def cancelar_reservacion(self, reservation_id: int) -> bool:
        reservation_id = _validar_int_pos(reservation_id, "reservation_id")
        reservaciones = _leer_json_lista(self._reservations_path)

        reserva_obj: Reservation | None = None
        for r in reservaciones:
            if r.get("id") == reservation_id:
                reserva_obj = Reservation.from_dict(r)
                if reserva_obj is None:
                    print("ERROR: Reservación corrupta, se omite.")
                    return False
                if r.get("estatus") == "cancelada":
                    return False
                r["estatus"] = "cancelada"
                break

        if reserva_obj is None:
            return False

        _escribir_json_lista(self._reservations_path, reservaciones)

        # Regresa disponibilidad al hotel
        hoteles = _leer_json_lista(self._hotels_path)
        for h in hoteles:
            if h.get("id") == reserva_obj.hotel_id:
                disp = h.get("habitaciones_disponibles")
                total = h.get("habitaciones_total")
                if not isinstance(disp, int) or not isinstance(total, int):
                    print("ERROR: Hotel corrupto al reponer disponibilidad.")
                    return True
                nuevo = disp + reserva_obj.habitaciones
                h["habitaciones_disponibles"] = min(nuevo, total)
        _escribir_json_lista(self._hotels_path, hoteles)
        return True

    def obtener_reservacion(self, reservation_id: int) -> Reservation | None:
        """Obtiene una reservación por id (parseo seguro)."""
        reservation_id = _validar_int_pos(reservation_id, "reservation_id")
        reservaciones = _leer_json_lista(self._reservations_path)
        for r in reservaciones:
            if r.get("id") == reservation_id:
                reserva = Reservation.from_dict(r)
                if reserva is None:
                    print("ERROR: Reservación corrupta, se omite.")
                return reserva
        return None
