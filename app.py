import streamlit as st
import re
import pandas as pd
import itertools
import shapiq
import numpy as np
import matplotlib.pyplot as plt


st.title("Shapley Values")

# 1. User Input
st.write("Understanding Shapley Values can be difficult - so here's a presentation. Shapley values are meant to measure how much of an impact individual variable or a group (coalition) of variables has on a function output (this also works with for example neural networks, as they can take several inputs and output a signle value, just like a function). We'll demonstrate this on a logical equation - please input one, and you'll see each variables impact.")
equation_input = st.text_input(
    "Enter a logical equation:",
    value="(f1 and f2) or not f3",
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

st.subheader("Variable Values")
cols = st.columns(len(variables))
var_states = {}


for i, var in enumerate(variables):
    with cols[i]:
        var_states[var] = st.checkbox(f"{var}", value=True, key="equation1"+str(i))
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
st.subheader("How to read a waterfall chart")
st.write("Begin at the bottom of the chart. You will see arrows pointing either left or right, with negative or positive values. On the x-axis you start in the point of and Expected Value - if you were to average out all possible outputs a function can have (based on all possible inputs) that's the value you would get. Starting from that point, any variable, or coalition of those, can either increase, or decrease expected score. If you follow all the arrows, from bottom to the top, you will end up either in 0 or in 1 (in case of a logicall function) - that depends whether the equation you inputed, and variable's values produce a positive or a negative result.")
st.subheader("How to interpret those values")
st.write("Chances are, if you inputed an equation that go something like this:   \nf1 or (f2 and f3 and ...)   \nf1 value will have the biggest value, whether negative or positive. We can easily infer from that that it likely will be a deciding factor in the outcome of this equation, but that may manifest in diffrent ways.")


with st.container(border=True):
    st.subheader("Types of interactions")
    st.write("Let's focus on interactions of 2 variables for now. They can be of 3 types:")
    st.markdown(
        """
    * **Redundancy:** One of the inputs is useless to the result. Think if a situation when we have AND gate, and one of the inputs is 0 - even if the other one is 1, it's redundant, because the result is 0 anyway
    * **Synergy:** Two inputs work together to increase the score even more than they would individualy.
    * **Antagonism:** Even if two inputs would increase the score by themselves, they bring it down when together. The example would be XOR gate (it needs an odd number of ones to return 1) - one 1 increases the score, but [1,1] decrease it by a lot
    """
    )

st.subheader("Redundancy Index")
st.write("In order to determine the interaction type we can use redundancy index, which gives positive values for redundancy feature pairs. Try it yourself!")

equation_input = st.text_input(
    "Enter another equation, and it will return redundancy in each pair of inputs:",
    value="f1 and f2",
    help="Use variables like f[1], f1, brackets (), and operators: and, or, not"
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
        var_states2[var] = st.checkbox(f"{var}", value=True, key="equation2"+str(i))
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

with st.container(border=True):
    st.subheader("Type determination algorithm")
    st.write("We shall use previously established values to calculate the type of the interaction between 2 inputs")
    st.markdown(
        """
    * **Synergy:** We determine the interaction type is synergy if main effects (single variable interaction value) of 2 variables and value of their interaction all have the same sign - In that case, they are all "pushing" the score in the same direction, so we conclude they must have a synergy
    * **Redundancy:** If the effect is concluded not to be syngery, AND redundancy index value is greater than 0, it's redundancy
    * **Antagonism:** In remaining cases it's antagonism
    """
    )