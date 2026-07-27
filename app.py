import streamlit as st

# Define your pages
home_page = st.Page("pages/start.py", title="Introduction", icon="🏠", default=True)
interpretation = st.Page("pages/interpretation.py", title="How to interpret", icon="📊")
redundancy_index = st.Page("pages/redundancy.py", title="Redundancy Index", icon="📈")
interaction_type = st.Page("pages/interaction_type.py", title="Interaction Type", icon="🔄")
quiz_page = st.Page("pages/quiz.py", title="Pop Quiz", icon="❓")

# Setup navigation menu in the sidebar
pg = st.navigation([home_page, interpretation, redundancy_index, interaction_type, quiz_page])

# Run the selected page
pg.run()