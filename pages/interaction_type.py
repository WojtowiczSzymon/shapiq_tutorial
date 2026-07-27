
import streamlit as st
import re
import pandas as pd
import itertools
import shapiq
import numpy as np
import matplotlib.pyplot as plt
from shapiq.interaction_type_explainer import TypeExplainer

from define import all_permutations, normalize_equation, create_var_dict, evaluate_expression, normalized_eq

st.html("""
<style>
/* Target the main content block */
.stMainBlockContainer {
    padding-top: 2rem !important;    /* Default is ~6rem (reduces top gap) */
    padding-bottom: 2rem !important; /* Bottom padding */
    padding-left: 2rem !important;   /* Left margin/padding */
    padding-right: 2rem !important;  /* Right margin/padding */
    max-width: 1200px !important;    /* Optional: control max width */
}
</style>
""")
st.html("""
<style>
/* Target the container using its key */
div[class*="try-it-border"] {
    border: 2px solid #90D5FF !important; /* Custom border color */
    border-radius: 10px;
    padding: 16px;
    h2 {
        color: #90D5FF !important;
    }
}
</style>
""")

st.title("Interaction Type")
st.write("We shall use previously established values to calculate the type of the interaction between 2 inputs")
st.markdown(
    """
* **Synergy:** We determine the interaction type is synergy if main effects (single variable interaction value) of 2 variables and value of their interaction all have the same sign. In that case, they are all "pushing" the score in the same direction, so we conclude they must have a synergy
* **Redundancy:** If the effect is concluded not to be synergy, AND redundancy index value is greater than 0, it's redundancy
* **Antagonism:** In remaining cases it's antagonism
"""
)
with st.container(key="try-it-border_3"):
    st.header("Try it yourself!")
    equation_input = st.text_input(
    "Enter equation and you will see type of interaction within each pair. Remember - this will heavily depend on variable value",
    value="f1 ^ f2 or (not f3 and f4)",
    help="Use variables like f[1], f1, brackets (), and operators: and, or, not",
    key="input3"
    )

    normalized_eq = normalize_equation(equation_input)

    variables = sorted(list(set(re.findall(r'\bf\d+\b', normalized_eq))))

    if not variables:
        st.info("Please enter an equation containing variables like f[1] or f1.")
        st.stop()

    st.write(f"**Detected Variables:** {', '.join(variables)}")

    st.subheader("Variable Values")
    cols = st.columns(len(variables))
    var_states3= {}


    for i, var in enumerate(variables):
        with cols[i]:
            key="equation3"+str(i)      
            if key not in st.session_state:
                st.session_state[key] = False
            current_val = st.session_state[key]
            var_states3[var] = st.checkbox(f"{var}={current_val}", key=key)
    vars = np.asarray(list([bool(var_states3[key]) for key in var_states3.keys()]))
    try:
        data=all_permutations(len(vars))
        types=TypeExplainer(vars, evaluate_expression, data).explain()
        ind=0
        for i in range(len(vars)-1):
            for j in range(i+1,len(vars)):
                if types[ind]=="synergy":
                    st.success(f"(f{i+1},f{j+1}) {types[ind]}")
                elif types[ind]=="redundancy":
                    st.warning(f"(f{i+1},f{j+1}) {types[ind]}")
                else:
                    st.error(f"(f{i+1},f{j+1}) {types[ind]}")
                ind+=1
    except:
        st.error("TypeExplainer error")