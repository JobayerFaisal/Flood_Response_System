import streamlit as st
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from dashboard.utils.state import init_state

init_state()
st.title("⏳ Timeline Replay")

if st.session_state.timeline is None:
    st.warning("Run simulation first.")
    st.stop()

timeline = st.session_state.timeline

step = st.slider("Step", 0, len(timeline)-1, st.session_state.selected_step)
st.session_state.selected_step = step

st.json(timeline[step])