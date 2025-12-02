from enum import Enum
from typing import Self

import serial


class LightState(Enum):
    Off = 0
    On = 1


class TiKitBoard:
    def __init__(self: Self, port="/dev/cu.usbmodem1103", baud_rate=9600) -> None:
        self.serial = serial.Serial(port, baud_rate, timeout=1)
        self.timer_string = "timer_length="
        with open("data.txt", "w") as f:
            f.write(f"{self.timer_string}6")

    def change_light_state(self: Self, light_state: LightState) -> None:
        if light_state.value == 1:
            self.serial.write(b"light_on\n")
        else:
            self.serial.write(b"light_off\n")

    def _convert_hours_to_milliseconds(self: Self, x: float) -> int:
        return int(x * 60 * 60 * 1000)

    def _get_timer_data(self: Self) -> int:
        with open("data.txt", "r") as f:
            data = f.readline()
            current_timer_length_hr = float(data.partition("=")[-1])
            current_timer_length_ms = self._convert_hours_to_milliseconds(
                current_timer_length_hr
            )
        return current_timer_length_ms

    def check_serial(self: Self) -> None:
        data = self.serial.read_until(b"\n")[:-1]
        if data == b"load_timer_data":
            timer_length = f"{self._get_timer_data()}\n"
            print(f"Sending {timer_length.encode('utf-8')}")
            self.serial.write(timer_length.encode("utf-8"))
