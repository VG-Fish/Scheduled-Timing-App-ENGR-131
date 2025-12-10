# Scheduled Timing Prototype Web App for ENGR 13100 @ Purdue

## Important Links & Info
- [TiKit Board Information](https://engineering.purdue.edu/fye_tikit/)
  - The MSP-EXP430FR5994 board found in the TiKits will be referred to as "TiKit Board."
- [PyPI Page](https://pypi.org/project/ti_kit_board_communication/)

## This project creates a web app using the streamlit Python library to interact with the TiKit board visually.

The goal of this project was to create a web app for users to interact with the TiKit Board. The web app, built with the `streamlit` Python library, allows users to turn the TiKit Board's built-in LED on and off. Users can also set timers with a maximum time limit of one day. The timer is displayed on the four-digit display. After the timers have completed, a sound will play, and the TiKit Board's built-in LED will turn on. 

The `pyserial` Python library was used to establish a connection between the TiKit Board and the connected computer. This project works by sending and receiving messages over the established serial port connection.

## How to install this library

1. Install the Python library:
  - `pip install ti_kit_board_communication`
2. Import the Python library in your code:
  - `from ti_kit_board_communication.main import TiKitBoard`



## Example Usage: Scehduled Timing Prototype

_Check out `example/ui.py` in this Github repo to see some example usage._

### Goal:
The goal of the scheduled timing prototype was to create a timer-based intelligent lighting system that combines sunlight sensing with automated LED supplementation. The web app and TiKit Board are shown below.


<img src="images/web_ui.png" alt="Logo" width="1080" />

*Web app*

<img src="images/board_picture.png" alt="Logo" width="1080" />

*TiKit Board*
