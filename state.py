"""Typed helpers around st.session_state.regions (a list[RegionEntry]),
replacing direct list mutation scattered across the UI code.
"""
import streamlit as st

from models import RegionEntry, make_region_entry


def init_state():
    if "regions" not in st.session_state:
        st.session_state.regions = []


def get_regions() -> list[RegionEntry]:
    return st.session_state.regions


def add_region(name: str, kcal: float):
    st.session_state.regions.append(make_region_entry(name, kcal))


def remove_region(index: int):
    st.session_state.regions.pop(index)


def clear_regions():
    st.session_state.regions.clear()
