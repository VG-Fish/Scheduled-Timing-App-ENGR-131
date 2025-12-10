import os
import time
from typing import Any, Dict, Optional, Self

import serial


class TiKitBoard:
    """
    This class provides a mean to establish a connection between Purdue's FYE TI Kit board and the connected computer.
    Additionally, this class provides useful methods to write information to the host computer, allowing data to persist
    beyond sessions.

    Methods
    ----------
    1. `connect_with_retries(self: Self, max_retries: Optional[int] = None) -> None`
    2. `read_serial(self: Self) -> Optional[bytes]`
    3. `is_board_connected(self: Self) -> bool`
    4. `send_message(self: Self, message: bytes) -> None`
    5. `write_key_to_storage(self: Self, key: str, value: Any) -> None`
    6. `remove_key_from_storage(self: Self, key: str) -> None`
    7. `get_value_from_storage(self: Self, key: str) -> Optional[Any]`
    8. `get_full_storage(self: Self) -> Optional[Dict[str, Any]]`
    """

    def __init__(
        self: Self,
        port: str,
        baud_rate: int = 9600,
        max_retries: int = 3,
        special_ending_character: bytes = b"\n",
        storage_file_path: str = "data.txt",
    ) -> None:
        """
        Parameters
        ----------
        `port`:
            The port the TI Kit Board is connected to. This value is accessible in the Energia IDE.
        `baud_rate`:
            The number of signal changes or "symbols" that occur per second. Communication between the board and host computer will
            only work if the `baud_rate` given to the class and on the TI Kit Board's side is the same. `9600` is what most people use.
        `max_retries`:
            If the TI Kit board can't be found instantly, a connection request will be attempted after one second. This process will keep
            happening until the number of retries equals `max_retries`. You may call `connect_with_retries()` method to retry the entire
            process again.
        `special_ending_character`:
            Sending and reading requests by the board and the computer both work by reading new strings that are waiting in the serial
            connection until `special_ending_character` is encountered. Both the computer and the board expect the same
            `special_ending_character`.
        `storage_file_path`:
            This parameter controls the name of the text file that's made for persistent memory. If you delete the text file, all the data
            contained inside will be lost.
        """

        self.connected: bool = False

        self.port: str = port
        self.baud_rate: int = baud_rate
        self.max_retries: int = max_retries
        self.serial: Optional[serial.Serial] = None
        self.special_ending_character: bytes = special_ending_character

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

    def _write_to_storage(self: Self) -> None:
        if not self.connected or self.serial is None:
            return

        with open(self.storage_file_path, "w") as f:
            for key, value in self.storage.items():
                f.write(f"{key}={value}")

    def connect_with_retries(self: Self, max_retries: Optional[int] = None) -> None:
        """Open the serial connection, retrying on failure.

        Parameters
        ----------
        `max_retries`:
            Maximum number of connection attempts. If not given,
            uses the instance's ``max_retries``.
        """

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

    def read_serial(self: Self) -> Optional[bytes]:
        """Read a single message from the serial port.

        Returns
        -------
        `Optional[bytes]`
            The bytes read (without the ending character), or `None`
            if no data is available or the board is disconnected.
        """

        if not self.connected or self.serial is None:
            return

        try:
            if self.serial.in_waiting:
                data: bytes = self.serial.read_until(self.special_ending_character)[:-1]
                print(f"Incoming data: {data}")
                return data

        except (OSError, serial.SerialException, AttributeError):
            self.connected = False
            try:
                self.serial.close()
            except Exception:
                pass
            self.serial = None
            print("No longer have serial in check_serial")

    def is_board_connected(self: Self) -> bool:
        """Checks if the TI Kit Board is connected.

        Returns
        -------
        `bool`
            returns `True` if the board is connected, else `False` if no board is found.
        """

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
        """Sends a message to the board if connected, else nothing is done."""

        if not self.connected or self.serial is None:
            return

        self.serial.write(message + self.special_ending_character)

    def write_key_to_storage(self: Self, key: str, value: Any) -> None:
        """Adds a key-value pair and saves it to memory if the board is connected."""

        if not self.connected or self.serial is None:
            return

        self.storage[key] = value

        self._write_to_storage()

    def remove_key_from_storage(self: Self, key: str) -> None:
        """Removes a key-value pair and saves it to memory if the board is connected."""

        if not self.connected or self.serial is None:
            return

        _ = self.storage.pop(key, None)

        self._write_to_storage()

    def get_value_from_storage(self: Self, key: str) -> Optional[Any]:
        """Retrieves a value from memory if the board is connected.

        Returns
        -------
        `Optional[Any]`
            returns `None` if the key isn't found or if the board isn't connected, else returns the value.
        """

        if not self.connected or self.serial is None:
            return

        return self.storage.get(key, None)

    def get_full_storage(self: Self) -> Optional[Dict[str, Any]]:
        """Retrieves the full dictionary if the board is connected.

        Returns
        -------
        `Optional[Any]`
            returns `None` if the board isn't connected, else returns the full dictionary.
        """

        if not self.connected or self.serial is None:
            return

        return self.storage
