import time
from datetime import timedelta

import streamlit as st

from main import TiKitBoard

if "board" not in st.session_state:
    st.session_state.board = TiKitBoard()
    st.session_state.board.connect_with_retries()

if "light_state" not in st.session_state:
    st.session_state.light_state = False


def loaded_screen():
    board: TiKitBoard = st.session_state.board
    st.markdown("# Scheduled Timing Test Mode GUI")

    if st.button("Toggle light"):
        st.session_state.light_state = not st.session_state.light_state
        if st.session_state.light_state:
            board.send_message(b"light_on")
        else:
            board.send_message(b"light_off")
        st.toast(f"Light is now {st.session_state.light_state}")

    if st.checkbox("Bypass light setting"):
        board.send_message(b"ignore_ambient_light")
    else:
        board.send_message(b"factor_ambient_light")

    st.subheader("Set timer")

    col1, col2, col3 = st.columns(3)
    with col1:
        hours = st.number_input("Hours", min_value=0, max_value=23, value=0, step=1)
    with col2:
        minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=1)
    with col3:
        seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)

    if st.button("Submit timer"):
        duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
        total_milliseconds = int(duration.total_seconds()) * 1000

        board.write_key_to_storage("timer_length", total_milliseconds)
        board.send_message(b"cancel_timer")
        time.sleep(0.2)
        message = f"timer={total_milliseconds}".encode("ascii")
        board.send_message(message)

        st.toast(f"Current timer length is {duration} long.")


def unloaded_screen():
    placeholder = st.empty()
    placeholder.write("Loading...")


@st.fragment(run_every="1s")
def draw():
    board: TiKitBoard = st.session_state.board

    if board.is_board_connected():
        loaded_screen()
        board.check_serial()
    else:
        unloaded_screen()
        board.connect_with_retries(max_retries=1)


draw()
