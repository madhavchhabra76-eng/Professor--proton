import streamlit as st
import time

# -----------------------------------------------------------
# PROFESSOR PROTON - DEMO v2
# Dev Note: Added data for ALL classes (6-10).
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️")

# MY DATA (FULL SYLLABUS MOCK)
# I have added 2 topics for every class to demonstrate range.
database = [
    # --- CLASS 6 ---
    {
        "class": 6, 
        "keywords": ["shadow", "dark", "light"],
        "answer_en": "According to Class 6: A shadow is formed when an opaque object blocks the path of light. Shadows are always dark.",
        "answer_pa": "ਕਲਾਸ 6 ਦੇ ਅਨੁਸਾਰ: ਜਦੋਂ ਕੋਈ ਅਪਾਰਦਰਸ਼ੀ ਵਸਤੂ ਰੋਸ਼ਨੀ ਦੇ ਰਸਤੇ ਵਿੱਚ ਆਉਂਦੀ ਹੈ ਤਾਂ ਪਰਛਾਵਾਂ ਬਣਦਾ ਹੈ। ਪਰਛਾਵੇਂ ਹਮੇਸ਼ਾ ਕਾਲੇ ਹੁੰਦੇ ਹਨ।"
    },
    {
        "class": 6, 
        "keywords": ["photosynthesis", "plant", "food"],
        "answer_en": "According to Class 6: Photosynthesis is how plants make food using sunlight, water, and carbon dioxide.",
        "answer_pa": "ਕਲਾਸ 6 ਦੇ ਅਨੁਸਾਰ: ਪ੍ਰਕਾਸ਼ ਸੰਸ਼ਲੇਸ਼ਣ ਉਹ ਪ੍ਰਕਿਰਿਆ ਹੈ ਜਿਸ ਦੁਆਰਾ ਪੌਦੇ ਸੂਰਜ ਦੀ ਰੌਸ਼ਨੀ, ਪਾਣੀ ਅਤੇ ਕਾਰਬਨ ਡਾਈਆਕਸਾਈਡ ਦੀ ਵਰਤੋਂ ਕਰਕੇ ਭੋਜਨ ਬਣਾਉਂਦੇ ਹਨ।"
    },

    # --- CLASS 7 ---
    {
        "class": 7,
        "keywords": ["acid", "base", "taste", "sour"],
        "answer_en": "According to Class 7: Acids are substances that taste sour (like lemon). Bases are substances that taste bitter and feel soapy (like soap).",
        "answer_pa": "ਕਲਾਸ 7 ਦੇ ਅਨੁਸਾਰ: ਤੇਜ਼ਾਬ ਉਹ ਪਦਾਰਥ ਹੁੰਦੇ ਹਨ ਜੋ ਸਵਾਦ ਵਿੱਚ ਖੱਟੇ ਹੁੰਦੇ ਹਨ (ਜਿਵੇਂ ਨਿੰਬੂ)। ਖਾਰ ਉਹ ਹੁੰਦੇ ਹਨ ਜੋ ਕੌੜੇ ਹੁੰਦੇ ਹਨ ਅਤੇ ਸਾਬਣ ਵਰਗੇ ਮਹਿਸੂਸ ਹੁੰਦੇ ਹਨ।"
    },
    {
        "class": 7,
        "keywords": ["heat", "temperature", "thermometer"],
        "answer_en": "According to Class 7: Heat flows from a hotter object to a colder object. We measure temperature using a thermometer.",
        "answer_pa": "ਕਲਾਸ 7 ਦੇ ਅਨੁਸਾਰ: ਗਰਮੀ ਗਰਮ ਵਸਤੂ ਤੋਂ ਠੰਡੀ ਵਸਤੂ ਵੱਲ ਵਗਦੀ ਹੈ। ਅਸੀਂ ਥਰਮਾਮੀਟਰ ਨਾਲ ਤਾਪਮਾਨ ਮਾਪਦੇ ਹਾਂ।"
    },

    # --- CLASS 8 ---
    {
        "class": 8,
        "keywords": ["force", "push", "pull"],
        "answer_en": "According to Class 8: A push or a pull on an object is called a force. Force can change the speed or shape of an object.",
        "answer_pa": "ਕਲਾਸ 8 ਦੇ ਅਨੁਸਾਰ: ਕਿਸੇ ਵਸਤੂ ਨੂੰ ਧੱਕਾ ਦੇਣ ਜਾਂ ਖਿੱਚਣ ਨੂੰ ਬਲ ਕਹਿੰਦੇ ਹਨ। ਬਲ ਵਸਤੂ ਦੀ ਗਤੀ ਜਾਂ ਸ਼ਕਲ ਬਦਲ ਸਕਦਾ ਹੈ।"
    },
    {
        "class": 8,
        "keywords": ["cell", "structure", "unit"],
        "answer_en": "According to Class 8: The cell is the basic structural and functional unit of life. It was discovered by Robert Hooke.",
        "answer_pa": "ਕਲਾਸ 8 ਦੇ ਅਨੁਸਾਰ: ਸੈੱਲ ਜੀਵਨ ਦੀ ਮੁੱਢਲੀ ਢਾਂਚਾਗਤ ਅਤੇ ਕਾਰਜਸ਼ੀਲ ਇਕਾਈ ਹੈ। ਇਸਦੀ ਖੋਜ ਰਾਬਰਟ ਹੁੱਕ ਨੇ ਕੀਤੀ ਸੀ।"
    },

    # --- CLASS 9 ---
    {
        "class": 9,
        "keywords": ["matter", "solid", "liquid", "gas"],
        "answer_en": "According to Class 9: Matter is anything that occupies space and has mass. It exists in three states: Solid, Liquid, and Gas.",
        "answer_pa": "ਕਲਾਸ 9 ਦੇ ਅਨੁਸਾਰ: ਪਦਾਰਥ ਉਹ ਚੀਜ਼ ਹੈ ਜੋ ਥਾਂ ਘੇਰਦੀ ਹੈ ਅਤੇ ਜਿਸਦਾ ਪੁੰਜ ਹੁੰਦਾ ਹੈ। ਇਹ ਤਿੰਨ ਅਵਸਥਾਵਾਂ ਵਿੱਚ ਹੁੰਦਾ ਹੈ: ਠੋਸ, ਤਰਲ ਅਤੇ ਗੈਸ।"
    },
    {
        "class": 9,
        "keywords": ["motion", "speed", "velocity"],
        "answer_en": "According to Class 9: Motion is the change in position of an object with time. Velocity is speed with direction.",
        "answer_pa": "ਕਲਾਸ 9 ਦੇ ਅਨੁਸਾਰ: ਸਮੇਂ ਦੇ ਨਾਲ ਕਿਸੇ ਵਸਤੂ ਦੀ ਸਥਿਤੀ ਵਿੱਚ ਤਬਦੀਲੀ ਨੂੰ ਗਤੀ ਕਹਿੰਦੇ ਹਨ। ਵੇਗ ਦਿਸ਼ਾ ਦੇ ਨਾਲ ਗਤੀ ਹੈ।"
    },

    # --- CLASS 10 ---
    {
        "class": 10, 
        "keywords": ["reflection", "law", "mirror"],
        "answer_en": "According to Class 10: The Laws of Reflection are: 1) Angle of incidence = Angle of reflection. 2) The incident ray, normal, and reflected ray lie in the same plane.",
        "answer_pa": "ਕਲਾਸ 10 ਦੇ ਅਨੁਸਾਰ: ਪ੍ਰਤੀਬਿੰਬ ਦੇ ਨਿਯਮ ਹਨ: 1) ਆਪਤਣ ਕੋਣ ਪਰਾਵਰਤਣ ਕੋਣ ਦੇ ਬਰਾਬਰ ਹੁੰਦਾ ਹੈ। 2) ਆਪਤਿਤ ਕਿਰਨ, ਅਭਿਲੰਬ ਅਤੇ ਪਰਾਵਰਤਿਤ ਕਿਰਨ ਇੱਕੋ ਤਲ ਵਿੱਚ ਹੁੰਦੇ ਹਨ।"
    },
    {
        "class": 10, 
        "keywords": ["carbon", "covalent", "bond"],
        "answer_en": "According to Class 10: Carbon forms Covalent Bonds by sharing electrons with other atoms. It is tetravalent.",
        "answer_pa": "ਕਲਾਸ 10 ਦੇ ਅਨੁਸਾਰ: ਕਾਰਬਨ ਦੂਜੇ ਪਰਮਾਣੂਆਂ ਨਾਲ ਇਲੈਕਟ੍ਰੌਨਾਂ ਦੀ ਸਾਂਝ ਕਰਕੇ ਸਹਿ-ਸੰਯੋਜਕ ਬੰਧਨ ਬਣਾਉਂਦਾ ਹੈ।"
    }
]

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
st.sidebar.header("User Settings")
selected_class = st.sidebar.selectbox("Select Class", [6, 7, 8, 9, 10])
language = st.sidebar.radio("Language", ["English", "Punjabi"])

st.sidebar.write("---")
st.sidebar.caption("Status: All Classes Active")

# -----------------------------------------------------------
# MAIN APP
# -----------------------------------------------------------
st.title("👨‍🏫 Professor Proton")
st.write(f"I am your strict Science teacher for **Class {selected_class}**. I only answer from YOUR syllabus.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["text"])

# INPUT
user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.messages.append({"role": "user", "text": user_input})
    with st.chat_message("user"):
        st.write(user_input)

    with st.spinner("Searching syllabus..."):
        time.sleep(1) 
        
        found_answer = ""
        
        # Search logic
        for item in database:
            # 1. Strict Class Filter
            if item["class"] == selected_class:
                # 2. Keyword Match
                for word in item["keywords"]:
                    if word in user_input.lower():
                        # 3. Language Selection
                        if language == "Punjabi":
                            found_answer = item["answer_pa"]
                        else:
                            found_answer = item["answer_en"]
                        break 
            if found_answer != "":
                break

    # Handle Output
    final_response = ""
    
    if found_answer != "":
        final_response = "✅ " + found_answer   
    else:
        # Not found in syllabus
        if language == "Punjabi":
            final_response = f"ਮਾਫ ਕਰਨਾ, ਇਹ ਵਿਸ਼ਾ ਕਲਾਸ {selected_class} ਦੇ ਸਿਲੇਬਸ ਵਿੱਚ ਨਹੀਂ ਹੈ।"
        else:
            final_response = f"❌ I cannot answer this. It is not in the Class {selected_class} syllabus."

    st.session_state.messages.append({"role": "assistant", "text": final_response})
    with st.chat_message("assistant"):
        st.write(final_response)
