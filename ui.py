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

    timer_number_input = st.number_input(
        "Set lighting length (in hours)",
        min_value=0.0,
        max_value=12.0,
        value=6.0,
        step=0.1,
        format="%.1f",
        on_change=timer_input_changed,
    )


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
