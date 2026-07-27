
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

st.title("How to interpret those values")
st.write("Chances are, if you inputed an equation that goes like this:   \nf1 or (f2 and f3 and ...)   \nf1 shapley value will be the biggest, whether negative or positive. We can easily infer from that that it likely will be a deciding factor in the outcome of this equation, but that may manifest in diffrent ways.")




with st.container(border=True):
    st.subheader("Types of interactions")
    st.write("Let's focus on interactions of 2 variables for now. They can be of 3 types:")
    st.markdown(
        """
    * **Redundancy:** One of the inputs is inconsequential to the result. Think of a situation when we have AND gate, and one of the inputs is 0 - even if the other one is 1, it's redundant, because the result is 0 anyway
    * **Synergy:** Two inputs work together to increase the score even more than they would individualy.
    * **Antagonism:** Even if two inputs would increase the score by themselves, they bring it down when together. The example would be XOR gate (it needs an odd number of ones to return 1) - one 1 increases the score, but [1,1] decrease it significantly
    """
    )

