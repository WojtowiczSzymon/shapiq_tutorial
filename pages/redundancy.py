
import streamlit as st
import re
import pandas as pd
import itertools
import shapiq
import numpy as np
import matplotlib.pyplot as plt

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
st.write("In order to determine the interaction type we can use redundancy index, which gives positive values for redundancy feature pairs. There are multiple ways to calculate redundancy index, we can calculate them from the following equations:")


st.latex(r"""
\begin{aligned}
g_u(S) &= f_i(S \cup \{u\}) - f_i(S)   &  g_v(S) = f_i(S \cup \{v\}) - f_i(S) \\[8pt]
g_{uv}(S) &= f_i(S \cup \{u, v\}) - f_i(S)   &   g_{\max}(S) = \max\{g_u(S), g_v(S)\} \\[8pt]
\text{base}(S) &= \max(0, \min(g_{uv}(S), g_{\max}(S)))   &   \text{span}(S) = g_{uv}(S) - g_{\max}(S)
\end{aligned}
""")

st.latex(
    r"R_{\text{red}, i}(u, v) = \frac{\text{base\_mean}(u, v)}{1 +"
    r" \text{span\_mean}(u, v)}"
)


st.write("The alternative is to use index like this:")

st.latex(
    
    r"Idx(u, v) = \frac{\text{I}(u, v)}{\text{I}(u) +"
    r" \text{I}(v) + {I}(u, v)}"
)

st.write("Where they differ is in the way they distinguish between redundancy and antagonism. The first index prefers redundancy, while the second index prefers antagonism. For example, if we have an AND gate with inputs 1 and 0, if we look at 0 first then 1 seems redundant, since the output will be 0 either way, but if we look at 1 first then 0 seems antagonistic, because it negates the positive input 1 has. For our purposes we'll use the first index.")
with st.container(key="try-it-border_2"):
    st.header("Try it yourself!")
    with st.form(key="form1"):
        equation_input = st.text_input(
                "Enter another equation, and it will return redundancy in each pair of inputs:",
                value="f1 and f2",
                help="Use variables like f[1], f1; brackets (); operators: and, or, not, ^ (xor)",
                key="input2"
            )
        submitted = st.form_submit_button("Confirm")
    
                
    st.markdown('</div>', unsafe_allow_html=True)

    normalized_eq = normalize_equation(equation_input)

    variables = sorted(list(set(re.findall(r'\bf\d+\b', normalized_eq))))

    if not variables:
        st.info("Please enter an equation containing variables like f[1] or f1.")
        st.stop()

    st.write(f"**Detected Variables:** {', '.join(variables)}")

    st.write("Toggle whether you want to set each variable to True or False.")
    cols = st.columns(len(variables))


    var_states = {}
    choice = {}
    for i, var in enumerate(variables):
        with cols[i]:
            key="switch1"+str(i)      
            if key not in st.session_state:
                st.session_state[key] = False
            current_val = st.session_state[key]
            choice[var] =  st.segmented_control(
                label=f"{var}",
                options=[f"{var}=False", f"{var}=True"],
                default=f"{var}=False",
                key=key,
                required=True
            )
            var_states[var] = (choice[var] == f"{var}=True")
            
    vars = np.asarray(list([bool(var_states[key]) for key in var_states.keys()]))

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

