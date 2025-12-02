import streamlit as st

from main import LightState, TiKitBoard

board = TiKitBoard()

st.markdown("# Scheduled Timing GUI")

if "light_state" not in st.session_state:
    st.session_state.light_state = False

if st.button("Toggle light"):
    st.session_state.light_state = not st.session_state.light_state
    print(st.session_state.light_state)
    if st.session_state.light_state:
        board.change_light_state(LightState.On)
    else:
        board.change_light_state(LightState.Off)
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


@st.fragment(run_every="1s")
def check_serial():
    board.check_serial()


check_serial()
