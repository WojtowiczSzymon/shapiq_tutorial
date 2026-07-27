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

st.title("Shapley Values")

# 1. User Input
st.markdown("Understanding Shapley Values can be difficult - so here is a presentation. Shapley values are meant to measure how much of an impact individual variable or a group (coalition) of variables has on a function output. This also can be applied to neural networks, as they can take several inputs and output a single value, just like a function. Shapley value is measured in how much does the **expected value change with a given variable enabled**. We'll demonstrate this on a logical expression -  for example, if we have an AND gate, with inputs [1,0] the first variable has shapley value 1/4, because it increases expected value from 1/4 to 1/2 (and 1/2 - 1/4 = 1/4). To see the interactive chart please input an expression, and you'll see each variable's impact.")



with st.container(key="try-it-border_1"):
    st.header("Try it yourself!")
    col_left, col_right = st.columns(2)
    with col_left:
        with st.container(border=False):
            
            with st.form(key="form"):
                equation_input = st.text_input(
                    "Enter a logical expression:",
                    value="f1 and f2",
                    help="Use variables like f[1], f1; brackets (); operators: and, or, not, ^ (xor)"
                )
                submitted = st.form_submit_button("Confirm")

            
            st.markdown('</div>', unsafe_allow_html=True)

            normalized_eq = normalize_equation(equation_input)

            variables = sorted(list(set(re.findall(r'\bf\d+\b', normalized_eq))))

            if not variables:
                st.info("Please enter an equation containing variables like f[1] or f1.")
                st.stop()

            st.write(f"**Detected Variables:** {', '.join(variables)}")



            st.subheader("Variable Values")
            st.write("check the box next to a variable in order to set it to TRUE, leave if unchecked to set it to FALSE")
            cols = st.columns(len(variables))


            var_states = {}
            for i, var in enumerate(variables):
                with cols[i]:
                    key="equation1"+str(i)      
                    if key not in st.session_state:
                        st.session_state[key] = False
                    current_val = st.session_state[key]
                    var_states[var] = st.checkbox(f"{var}={current_val}", key=key)
            vars = np.asarray(list([bool(var_states[key]) for key in var_states.keys()]))
                    
            

    with col_right:
        with st.container(border=True):
            st.subheader("How to read a waterfall chart")
            st.markdown("Begin at the bottom of the chart. You will see arrows pointing either left or right, with negative or positive values. On the x-axis you start in the point of an **expected value** - if you were to average out all possible outputs a function can have (based on all possible inputs) that's the value you would get. Starting from that point, any variable, or coalition of those, can either increase, or decrease the expected score. If you follow all the arrows, from bottom to top, you will end up either in 0 or in 1 (in case of a logical function) - that depends on whether the equation you inputed, and variable's values either produce 1 or 0 as result.")
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
        interaction_values.plot_waterfall(show=False, feature_names=variables)

        fig = plt.gcf()
        st.pyplot(fig)
        plt.close(fig)
    except Exception as e:
        st.error(f"Invalid equation format. Error: {e}")

