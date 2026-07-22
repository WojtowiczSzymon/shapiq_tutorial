import streamlit as st
import re
import pandas as pd
import itertools
import shapiq
import numpy as np
import matplotlib.pyplot as plt


st.title("Shapley Values")

# 1. User Input
st.write("Understanding Shapley Values can be difficult - so here's a presentation. Shapley values are meant to measure how much of an impact individual variable or a group of variables has on a function (or any other model that takes several inputs and has a return value. We'll demonstrate this on a logical equation - please input one, and you'll see each variables impact.)")
equation_input = st.text_input(
    "Enter a logical equation:",
    value="(f[1] and f[2]) or not f[3]",
    help="Use variables like f[1], f1, brackets (), and operators: and, or, not"
)
def all_permutations(stop) -> np.ndarray:
    """Generates all permutations of binary inputs up to a specified length."""
    return np.array(list(itertools.product([True, False], repeat=stop)))

# 2. Normalize variable names: convert f[1] -> f1 for easier parsing
def normalize_equation(eq: str) -> str:
    # Replaces f[1] with f1
    return re.sub(r'f\[(\d+)\]', r'f\1', eq)

normalized_eq = normalize_equation(equation_input)

# 3. Extract unique variables (e.g., f1, f2, f3)
variables = sorted(list(set(re.findall(r'\bf\d+\b', normalized_eq))))

if not variables:
    st.info("Please enter an equation containing variables like f[1] or f1.")
    st.stop()

st.write(f"**Detected Variables:** {', '.join(variables)}")

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

    # Allowed operators / safe environment
    allowed_globals = {"__builtins__": {}}

    outputs = np.zeros(var_values.shape[0])
    for i, row in enumerate(var_values):
        outputs[i] = bool(eval(expr, allowed_globals, create_var_dict(row)))
    return outputs

# Mode Selection
mode = st.radio("Choose evaluation mode:", ["Interactive Inputs", "Generate Truth Table"])

if mode == "Interactive Inputs":
    
    st.subheader("Variable Values")
    cols = st.columns(len(variables))
    var_states = {}

    
    for i, var in enumerate(variables):
        with cols[i]:
            var_states[var] = st.checkbox(f"{var}", value=True)
    vars = np.asarray(list([bool(var_states[key]) for key in var_states.keys()]))
            
    try:
        data=all_permutations(len(vars))
        explainer = shapiq.TabularExplainer(
            model=evaluate_expression,
            data=data,
            index="k-SII",
            max_order=2,
            normalize=False,
            sample_size=len(data),
        )

        interaction_values = explainer.explain(vars, budget=256)
        interaction_values.plot_waterfall(show=False)

        fig = plt.gcf()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.error(f"Invalid equation format. Error: {e}")

else:  # Truth Table Mode
    st.subheader("Truth Table")
    
    # Generate all combinations of True/False
    combinations = list(itertools.product([True, False], repeat=len(variables)))
    
    rows = []
    try:
        for combo in combinations:
            var_dict = dict(zip(variables, combo))
            res = evaluate_expression(normalized_eq, var_dict)
            
            row = {**var_dict, "Result": res}
            rows.append(row)
            
        df = pd.DataFrame(rows)
        st.dataframe(df, use_container_width=True)
        
    except Exception as e:
        st.error(f"Could not compute truth table. Error: {e}")