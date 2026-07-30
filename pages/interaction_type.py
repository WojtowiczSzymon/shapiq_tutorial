
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

st.title("Interaction Type")
st.write("We shall use previously established values to calculate the type of the interaction between 2 inputs")
st.markdown(
    """
* **Synergy:** We determine the interaction type is synergy if main effects (single variable interaction value) of 2 variables and value of their interaction all have the same sign. In that case, they are all "pushing" the score in the same direction, so we conclude they must have a synergy
* **Redundancy:** If the effect is concluded not to be synergy, AND redundancy index value is greater than 0, it's redundancy
* **Antagonism:** In remaining cases it's antagonism
"""
)
def explain(vars, evaluate_expression, data):
    """
    Explain interaction type by returning an array of their names
    """
    n = len(vars)
    explainer = shapiq.TabularExplainer(
        model=evaluate_expression,
        data=data,
        index="k-SII",
        max_order=2,
        normalize=False,
        sample_size=len(data),
    )
    ind=n+1
    result=[]
    values_sii = np.asarray(explainer.explain(vars, budget=256))
    for i in range(1, n + 1):
        for j in range(i + 1, n + 1):
            value1 = values_sii[i]
            value2 = values_sii[j]
            values_combined = values_sii[ind]
            index = values_combined / (value1 + value2 + values_combined)
            ind+=1
            if values_combined > -0.00001 and values_combined < 0.00001:
                result.append("independence")
            elif (value1 > -0.00001 and value2 > -0.00001 and values_combined > -0.00001) or (value1 < 0.0001 and value2 < 0.0001 and values_combined < 0.0001):
                result.append("synergy")
            elif index < 0:
                result.append("redundancy")
            else:
                result.append("antagonism")
    return result
with st.container(key="try-it-border_3"):
    st.header("Try it yourself!")
   
    with st.form(key="form1"):
        equation_input = st.text_input(
                "Enter equation and you will see type of interaction within each pair. Remember - this will heavily depend on variable value",
                value="f1 and f2 or f3",
                help="Use variables like f[1], f1; brackets (); operators: and, or, not, ^ (xor)",
                key="input3"
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


    var_states3 = {}
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
            var_states3[var] = (choice[var] == f"{var}=True")
            
    vars = np.asarray(list([bool(var_states3[key]) for key in var_states3.keys()]))
    try:
        print("trying")
        data=all_permutations(len(vars))
        types=explain(vars, evaluate_expression, data)
        print("types:", types)
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