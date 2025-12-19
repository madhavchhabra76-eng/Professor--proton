import streamlit as st
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - PROTOYPE v1
# TODO: Connect to Google Gemini API later.
# Currently using manual data to test if the "Class Filter" works.
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# MY DATA
# I am writing these manually to test. 
# If the user selects Class 6, they should NEVER see Class 10 answers.
database = [
    {
        "class": 6, 
        "keywords": ["shadow", "dark", "light"],
        "answer": "According to Class 6: A shadow is formed when an opaque object blocks the path of light. Shadows are always dark."
    },
    {
        "class": 6, 
        "keywords": ["photosynthesis", "plant", "food"],
        "answer": "According to Class 6: Photosynthesis is how plants make food using sunlight, water, and carbon dioxide."
    },
    {
        "class": 10,
        "keywords": ["reflection", "law", "angle"],
        "answer": "According to Class 10: The Laws of Reflection are: 1) Angle of incidence = Angle of reflection. 2) The incident ray, normal, and reflected ray lie in the same plane."
    },
    {
        "class": 10,
        "keywords": ["carbon", "bond", "covalent"],
        "answer": "According to Class 10: Carbon forms Covalent Bonds by sharing electrons with other atoms."
    }
]

# -----------------------------------------------------------
# SIDEBAR (THE SETUP)
# -----------------------------------------------------------
st.sidebar.header("User Settings")
# User has to select class first
selected_class = st.sidebar.selectbox("Select Class", [6, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

st.sidebar.write("---")
st.sidebar.write("Dev Note: API is OFF. Using local list.")

# -----------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------
st.title("👨‍🏫 Professor Proton")
st.write("I am your strict Science teacher. I only answer from YOUR syllabus.")

# Chat history storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# Show old messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# INPUT BOX
user_input = st.chat_input("Ask a question (e.g. What is a shadow?)")

if user_input:
    # 1. Show user message
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    # 2. "Thinking" animation
    with st.spinner("Searching syllabus..."):
        time.sleep(1) # faking the delay so it looks real
        
        # 3. LOGIC: Search the database list
        found_answer = ""
        
        # print("User asked:", user_input) # debugging
        
        for item in database:
            # First, CHECK CLASS! 
            if item["class"] == selected_class:
                # Then, check for keywords
                for word in item["keywords"]:
                    if word in user_input.lower():
                        found_answer = item["answer"]
                        break # stop looking if we found it
            
            if found_answer != "":
                break

    # 4. Handle Language (Manual translation for demo)
    if found_answer != "":
        if language == "Punjabi":
            # I don't have an API yet, so I'm just adding a label
            final_response = "[PUNJABI TRANSLATION MODE]\n\n" + found_answer
        else:
            final_response = final_response = "✅ " + found_answer
            
    else:
        # If nothing found
        if language == "Punjabi":
            final_response = "ਮਾਫ ਕਰਨਾ, ਇਹ ਵਿਸ਼ਾ ਤੁਹਾਡੀ ਜਮਾਤ ਵਿੱਚ ਨਹੀਂ ਹੈ। (Topic not in syllabus)"
        else:
            final_response = "❌ I cannot answer this. It is not in the Class " + str(selected_class) + " syllabus."

    # 5. Show Answer
    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
