import streamlit as st
from backend.synthetic.scenario_runner import run_scenario

def init_state():
    if "timeline" not in st.session_state:
        st.session_state.timeline = None

    if "selected_step" not in st.session_state:
        st.session_state.selected_step = 0

def run_simulation(scenario, seed, steps):
    st.session_state.timeline = run_scenario(scenario, seed, steps)
    st.session_state.selected_step = len(st.session_state.timeline) - 1