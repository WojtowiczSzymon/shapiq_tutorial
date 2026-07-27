import streamlit as st

st.set_page_config(page_title="Pop Quiz", page_icon="❓")
st.title("Pop Quiz")
st.write("Answer the questions below. Press **Enter** on any text input or click **Submit Quiz** at the bottom to check your score.")

# Initialize session state for tracking submission status
if "submitted" not in st.session_state:
    st.session_state.submitted = False


questions = [
    {
        "id": "q1",
        "question": "1. What is the Shapley value for f1 (first input) in OR gate with inputs [0,1]?",
        "type": "input",
        "answer": ["-0.25", "-1/4"]
    },
    {
        "id": "q2",
        "question": "2. What type of interaction in an OR gate with inputs [1,1]?",
        "type": "mc",
        "options": ["Synergy, because both inputs contribute positively to the output", "Redundancy, because we need only one input to determine the output", "Antagonism, because the inputs are working against each other"],
        "answer": ["Redundancy, because we need only one input to determine the output"]
    },
    {
        "id": "q3",
        "question": "3. What is the Shapley value for coalition (f1,f2) in AND gate with inputs [1,1]?",
        "type": "input",
        "answer": ["0.25", "1/4"]
    },
    {
        "id": "q4",
        "question": "4. Redundancy index for a certain pair of inputs is 0.5. Is the interaction type redundancy?",
        "type": "mc",
        "options": ["Yes, because it greater than 0", "No, it could be syngery too", "No, redundancy is indicated by negative redundancy index"],
        "answer": ["No, it could be syngery too"]
    },
    {
        "id": "q5",
        "question": "5. For a XOR gate with inputs [1,1], what is the interaction type?",
        "type": "mc",
        "options": ["Synergy", "Redundancy", "Antagonism"],
        "answer": ["Antagonism"]
    },
    {
        "id": "q6",
        "question": "6. What does the Shapley value measure?",
        "type": "mc",
        "options": ["The contribution of each variable or coalition to the total value of the output", "The probability of each player winning", "The average value of the coalition"],
        "answer": ["The contribution of each variable or coalition to the total value of the output"]
    }
    ]

score = 0
total = len(questions)

# Display Questions
for q in questions:
    user_ans = ""
    
    if q["type"] == "mc":
        # st.radio displays all choices on the page by default
        # index=None ensures no option is selected initially
        user_ans = st.radio(
            q["question"], 
            q["options"], 
            key=q["id"],
            index=None
        )
    elif q["type"] == "input":
        with st.form(key="form"+str(q["id"])):
            user_ans = st.text_input(
                q["question"], 
                key=q["id"],
                help="Press enter to submit"
            )
            submitted = st.form_submit_button("Confirm")
        

    # Evaluate answer on submission
    if st.session_state.submitted:
        clean_user_ans = (user_ans or "").strip().lower()
        
        # Clean and convert all accepted answers to lowercase
        valid_answers = [ans.strip().lower() for ans in q["answer"]]
        
        # Check if the user's input matches ANY of the valid answers
        is_correct = clean_user_ans in valid_answers and clean_user_ans != ""
        
        if is_correct:
            score += 1
            st.success("✅ Correct")
        else:
            st.error("❌ Incorrect")
            
    st.markdown("---")

# Submit Button at the bottom


# Score Card section at the bottom
if st.session_state.submitted:
    percentage = round((score / total) * 100, 1)
    
    st.subheader("📊 Final Score")
    if percentage == 100:
        st.balloons()
        st.success(f"🎉 Excellent work! You scored **{score}/{total}** ({percentage}%)")
    elif percentage >= 50:
        st.info(f"👍 Good effort! You scored **{score}/{total}** ({percentage}%)")
    else:
        st.warning(f"📚 Keep practicing! You scored **{score}/{total}** ({percentage}%)")
        
    if st.button("Retake Quiz"):
        # Reset submitted state and clear selection keys
        st.session_state.submitted = False
        for q in questions:
            if q["id"] in st.session_state:
                del st.session_state[q["id"]]
        st.rerun()
else:
    if st.button("Submit Quiz", type="primary"):
        st.session_state.submitted = True
        st.rerun()