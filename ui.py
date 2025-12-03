from datetime import timedelta

import streamlit as st

from main import TiKitBoard

if "board" not in st.session_state:
    st.session_state.board = TiKitBoard()
    board = st.session_state.board
    board.connect_with_retries()
    # Six hours is the default timer length.
    board.write_key_to_storage("timer_length", 6 * 60 * 60 * 1000)


def loaded_screen():
    board: TiKitBoard = st.session_state.board
    st.markdown("# Scheduled Timing GUI")

    if "light_state" not in st.session_state:
        st.session_state.light_state = False

    if st.button("Toggle light"):
        st.session_state.light_state = not st.session_state.light_state
        print(st.session_state.light_state)
        if st.session_state.light_state:
            board.send_message(b"light_on\n")
        else:
            board.send_message(b"light_off\n")
        st.toast(f"Light is now {st.session_state.light_state}")

    def timer_input_changed():
        st.toast("Saved!")

    st.subheader("Set timer")

    col1, col2, col3 = st.columns(3)
    with col1:
        hours = st.number_input("Hours", min_value=0, max_value=23, value=0, step=1)
    with col2:
        minutes = st.number_input("Minutes", min_value=0, max_value=59, value=0, step=1)
    with col3:
        seconds = st.number_input("Seconds", min_value=0, max_value=59, value=0, step=1)

    duration = timedelta(hours=hours, minutes=minutes, seconds=seconds)
    total_seconds = int(duration.total_seconds())

    st.write(f"Timer length: {duration} ({total_seconds} seconds)")


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
