import streamlit as st
import re
import pandas as pd
import itertools
import shapiq
import numpy as np
import matplotlib.pyplot as plt

def all_permutations(stop) -> np.ndarray:
    """Generates all permutations of binary inputs up to a specified length."""
    return np.array(list(itertools.product([True, False], repeat=stop)))

# 2. Normalize variable names: convert f[1] -> f1 for easier parsing
def normalize_equation(eq: str) -> str:
    # Replaces f[1] with f1
    global normalized_eq
    normalized_eq = re.sub(r'f\[(\d+)\]', r'f\1', eq)
    return normalized_eq

def create_var_dict(bool_array):
    """
    Converts a 1D boolean array or list into a dict with keys 'f1', 'f2', ...
    Works with both standard Python lists and 1D NumPy boolean arrays.
    """
    return {f"f{i+1}": val for i, val in enumerate(bool_array)}

# 4. Safe Evaluation Helper
def evaluate_expression(var_values: np.ndarray) -> bool:
    """
    Evaluates the logical expression safely using Python's eval 
    with a restricted global/local environment.
    """
    global normalized_eq
    expr = normalized_eq
    print("expr:", expr)

    # Allowed operators / safe environment
    allowed_globals = {"__builtins__": {}}

    outputs = np.zeros(var_values.shape[0])
    for i, row in enumerate(var_values):
        outputs[i] = bool(eval(expr, allowed_globals, create_var_dict(row)))
    return outputs

def colored_segmented_control(var_name: str, switch_series:str, default_true: bool = False):
    """
    Renders a binary segmented control and dynamically sets its active 
    background to RED when False and GREEN when True.
    """
    key = f"{switch_series}_{var_name}_control"
    options = [f"{var_name}=False", f"{var_name}=True"]
    default_val = f"{var_name}=True" if default_true else f"{var_name}=False"

    # 1. Render control
    choice = st.segmented_control(
        label=f"{var_name} Setting",
        options=options,
        default=default_val,
        key=key
    )
    
    # 2. Determine state & corresponding color
    is_true = choice.endswith("True")
    active_color = "#2e7d32" if is_true else "#c62828"  # Green vs Red

    # 3. Inject explicit background override scoped to THIS specific widget instance
    st.html(f"""
    <style>
        div.st-key-{key} div[data-testid="stSegmentedControl"] button[aria-pressed="true"],
        div.st-key-{key} div[data-testid="stSegmentedControl"] button[aria-selected="true"] {{
            background-color: {active_color} !important;
            color: #ffffff !important;
            border-color: {active_color} !important;
        }}
    </style>
    """)

    return is_true

normalized_eq=None



