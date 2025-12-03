import os
import time
from typing import Any, Callable, Dict, List, Optional, Self

import serial


class TiKitBoard:
    def __init__(
        self: Self,
        port: str = "/dev/cu.usbmodem1103",
        baud_rate: int = 9600,
        max_retries: int = 3,
        special_ending_character: bytes = b"\n",
        storage_file_path: str = "data.txt",
        special_commands: Dict[str, Callable] = {},
    ) -> None:
        self.connected: bool = False

        self.port: str = port
        self.baud_rate: int = baud_rate
        self.max_retries: int = max_retries
        self.serial: Optional[serial.Serial] = None
        self.special_ending_character: bytes = special_ending_character

        self.storage_file_path: str = storage_file_path
        self.storage: Dict[str, Any] = {}

        self.special_commands: Dict[str, Callable] = special_commands

    def _init_storage(self: Self) -> None:
        self.storage.clear()

        if os.path.isfile(self.storage_file_path):
            with open(self.storage_file_path, "r") as f:
                for line in f.readlines():
                    key, _, value = line.partition("=")
                    self.storage[key] = value

        with open(self.storage_file_path, "w") as f:
            f.close()

    def _write_to_storage(self: Self) -> None:
        if not self.connected or self.serial is None:
            return

        with open(self.storage_file_path, "w") as f:
            for key, value in self.storage.items():
                f.write(f"{key}={value}")

    def connect_with_retries(self: Self, max_retries: Optional[int] = None) -> None:
        if max_retries is None:
            max_retries = self.max_retries

        num_tries: int = 0
        self.connected = False
        self.serial = None

        while num_tries < max_retries and not self.connected:
            try:
                print("Trying to connect...")
                self.serial = serial.Serial(self.port, self.baud_rate, timeout=1)
                print("Successfully connected.")
                self.connected = True
            except serial.SerialException:
                print("Failed to connect. Trying again in one second...\n")
                num_tries += 1
                time.sleep(1)

        self._init_storage()

    def check_serial(self: Self) -> None:
        if not self.connected or self.serial is None:
            return

        try:
            if self.serial.in_waiting:
                data: bytes = self.serial.read_until(self.special_ending_character)[:-1]
                print(f"Incoming data: {data}")
                if data.startswith(b"timer="):
                    _, _, value = data.partition(b"=")
                    self.write_key_to_storage("timer_length", int(value))
                elif data == b"timer_finished":
                    self.write_key_to_storage("timer_length", 0)

        except (OSError, serial.SerialException, AttributeError):
            self.connected = False
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
            print("No longer have serial in check_serial")

    def is_board_connected(self: Self) -> bool:
        if self.serial is None or not getattr(self.serial, "is_open", False):
            self.connected = False
            return False

        try:
            _ = self.serial.in_waiting
            self.connected = True
        except (OSError, serial.SerialException, AttributeError):
            self.connected = False

            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
            print("No longer have serial in is_board_connected")
        return self.connected

    def send_message(self: Self, message: bytes) -> None:
        if not self.connected or self.serial is None:
            return

        self.serial.write(message + self.special_ending_character)

    def write_key_to_storage(self: Self, key: str, value: Any) -> None:
        if not self.connected or self.serial is None:
            return

        self.storage[key] = value

        self._write_to_storage()

    def get_value_from_storage(self: Self, key: str) -> Optional[List[str]]:
        if not self.connected or self.serial is None:
            return

        return self.storage.get(key, None)

    def get_full_storage(self: Self) -> Optional[Dict[str, Any]]:
        if not self.connected or self.serial is None:
            return

        return self.storage
