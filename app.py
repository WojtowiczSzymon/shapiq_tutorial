import streamlit as st
import re
import pandas as pd
import itertools

st.title("Logical Equation Evaluator")

# 1. User Input
equation_input = st.text_input(
    "Enter a logical equation:",
    value="(f[1] and f[2]) or not f[3]",
    help="Use variables like f[1], f1, brackets (), and operators: and, or, not"
)

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

# 4. Safe Evaluation Helper
def evaluate_expression(expr: str, var_values: dict) -> bool:
    """
    Evaluates the logical expression safely using Python's eval 
    with a restricted global/local environment.
    """
    # Allowed operators / safe environment
    allowed_globals = {"__builtins__": None}
    
    # Map variable values (booleans)
    return bool(eval(expr, allowed_globals, var_values))

# Mode Selection
mode = st.radio("Choose evaluation mode:", ["Interactive Inputs", "Generate Truth Table"])

if mode == "Interactive Inputs":
    st.subheader("Variable Values")
    cols = st.columns(len(variables))
    var_states = {}
    
    for i, var in enumerate(variables):
        with cols[i]:
            var_states[var] = st.checkbox(f"{var}", value=True)
            
    try:
        result = evaluate_expression(normalized_eq, var_states)
        st.success(f"**Result:** `{result}`")
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