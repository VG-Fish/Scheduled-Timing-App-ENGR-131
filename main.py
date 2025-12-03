import os
import time
from typing import Any, Dict, List, Optional, Self

import serial


class TiKitBoard:
    def __init__(
        self: Self,
        port: str = "/dev/cu.usbmodem1103",
        baud_rate: int = 9600,
        max_retries: int = 3,
        storage_file_path: str = "data.txt",
    ) -> None:
        self.connected: bool = False

        self.port: str = port
        self.baud_rate: int = baud_rate
        self.max_retries: int = max_retries
        self.serial: Optional[serial.Serial] = None

        self.storage_file_path: str = storage_file_path
        self.storage: Dict[str, Any] = {}

    def _init_storage(self: Self) -> None:
        self.storage.clear()

        if os.path.isfile(self.storage_file_path):
            with open(self.storage_file_path, "r") as f:
                for line in f.readlines():
                    key, _, value = line.partition("=")
                    self.storage[key] = value

        with open(self.storage_file_path, "w") as f:
            f.close()

    def _get_timer_data(self: Self) -> int:
        if not self.connected:
            return -1

        with open("data.txt", "r") as f:
            data: str = f.readline()
            current_timer_length_ms: int = int(data.partition("=")[-1])
        return current_timer_length_ms

    def _write_to_storage(self: Self) -> None:
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
                data: bytes = self.serial.read_until(b"\n")[:-1]
                if data == b"load_timer_data":
                    timer_length: str = f"{self._get_timer_data()}\n"
                    print(f"Sending {timer_length.encode('utf-8')}")
                    self.serial.write(timer_length.encode("utf-8"))
        except (OSError, serial.SerialException, AttributeError):
            # lost connection mid-loop
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

        self.serial.write(message)

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
