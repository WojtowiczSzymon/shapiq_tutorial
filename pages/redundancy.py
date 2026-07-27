
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


st.title("Redundancy Index")
st.write("In order to determine the interaction type we can use redundancy index, which gives positive values for redundancy feature pairs")

with st.container(key="try-it-border_2"):
    st.header("Try it yourself!")
    equation_input = st.text_input(
        "Enter another equation, and it will return redundancy in each pair of inputs:",
        value="f1 and f2",
        help="Use variables like f[1], f1, brackets (), and operators: and, or, not",
        key="input2"
    )

    normalized_eq = normalize_equation(equation_input)

    variables = sorted(list(set(re.findall(r'\bf\d+\b', normalized_eq))))

    if not variables:
        st.info("Please enter an equation containing variables like f[1] or f1.")
        st.stop()

    st.write(f"**Detected Variables:** {', '.join(variables)}")

    st.subheader("Variable Values")
    cols = st.columns(len(variables))
    var_states2= {}


    for i, var in enumerate(variables):
        with cols[i]:
            key="equation2"+str(i)      
            if key not in st.session_state:
                st.session_state[key] = False
            current_val = st.session_state[key]
            var_states2[var] = st.checkbox(f"{var}={current_val}", key=key)
    vars = np.asarray(list([bool(var_states2[key]) for key in var_states2.keys()]))

    try:
        data=all_permutations(len(vars))
        explainer = shapiq.TabularExplainer(
            model=evaluate_expression,
            data=data,
            index="Rred",
            max_order=2,
            normalize=False,
            sample_size=len(data),
        )
        interaction_values = explainer.explain(vars, budget=256)
        interaction_values.get_n_order(2).plot_upset(show=False)
        
        fig = plt.gcf()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.error(f"Invalid equation format. Error: {e}")

