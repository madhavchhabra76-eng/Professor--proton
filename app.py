import streamlit as st
import time
import requests
import json
from groq import Groq

# -----------------------------------------------------------
# PROFESSOR PROTON - SAFETY & DETAIL EDITION 🛡️
# -----------------------------------------------------------

try:
    st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

    # --- 1. CSS ---
    st.markdown("""
    <style>
        .stApp { background-color: #ffffff; }
        p, h1, h2, h3, li, div, span, b, strong { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
        
        .tutor-box { 
            background-color: #f3f0ff; 
            padding: 25px; 
            border-radius: 15px; 
            margin-bottom: 20px; 
            border-left: 6px solid #7c3aed; 
            font-size: 18px; 
            line-height: 1.8; 
            color: #1f2937;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }
        
        .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
        button[kind="primary"] { background-color: #7c3aed !important; border: none; color: white !important; }
    </style>
    """, unsafe_allow_html=True)

    # --- 2. KEYS CHECK ---
    if "GROQ_API_KEY" not in st.secrets:
        st.error("⚠️ GROQ_API_KEY is missing in Secrets.")
        st.stop()
        
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])

    # --- 3. GOOGLE SEARCH FUNCTION ---
    def get_google_images(search_query):
        # Safety check for keys
        if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CX" not in st.secrets:
            return [], "Google keys missing."
        
        api_key = st.secrets["GOOGLE_API_KEY"]
        cx = st.secrets["GOOGLE_CX"]
        url = "https://www.googleapis.com/customsearch/v1"
        
        params = { 
            'q': search_query, 
            'key': api_key, 
            'cx': cx, 
            'searchType': 'image', 
            'num': 3, 
            'safe': 'active', 
            'imgType': 'clipart' 
        }
        
        try:
            response = requests.get(url, params=params)
            results = response.json()
            image_links = []
            
            if 'items' in results:
                for item in results['items']:
                    image_links.append(item['link'])
                return image_links, None
            else:
                return [], "No images found."
                
        except Exception as e:
            return [], f"Error: {str(e)}"

    # --- 4. TEXT STREAMER ---
    def stream_text(placeholder, text):
        current_text = ""
        for word in text.split():
            current_text += word + " "
            placeholder.markdown(f"<div class='tutor-box'>{current_text} ▌</div>", unsafe_allow_html=True)
            time.sleep(0.02)
        final_html = f"<div class='tutor-box'>{current_text}</div>"
        placeholder.markdown(final_html, unsafe_allow_html=True)
        return final_html

    # --- 5. UI HEADER ---
    st.title("Professor Proton ⚛️")
    with st.expander("⚙️ Settings", expanded=False):
        selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
        language = st.radio("Language", ["English", "Punjabi"])
        if st.button("🧹 Clear Chat"):
            st.session_state.messages = []
            st.session_state.pop("pending_search_query", None)
            st.rerun()

    # --- 6. HISTORY ---
    if "messages" not in st.session_state: st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg.get("type") == "images":
                 cols = st.columns(len(msg["content"]))
                 for i, img_url in enumerate(msg["content"]):
                     cols[i].image(img_url, use_column_width=True)
            else:
                 st.markdown(msg["content"], unsafe_allow_html=True)

    # --- 7. MAIN LOGIC ---
    user_input = st.chat_input("Ask a question...")

    if user_input:
        st.session_state.pop("pending_search_query", None)
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"): st.write(user_input)

        with st.chat_message("assistant"):
            answer_ph = st.empty()
            
            with st.spinner("Writing detailed explanation..."):
                try:
                    # PROMPT LOGIC
                    lang_instruction = """
                    English. Write a long, enthusiastic explanation (approx 150 words). 
                    Start with 'Hello there, young scientist!'.
                    Explain the reaction, the heat produced, and the safety role of kerosene.
                    """
                    
                    if language == "Punjabi":
                        lang_instruction = """
                        Punjabi (GURMUKHI SCRIPT ONLY).
                        
                        CRITICAL INSTRUCTION: You must provide a LONG, STORY-LIKE explanation (Equal length to the English version).
                        
                        STRUCTURE:
                        1. Greeting: "ਸਤ ਸ੍ਰੀ ਅਕਾਲ! ਆਓ ਇਸ ਬਾਰੇ ਵਿਸਥਾਰ ਵਿੱਚ ਜਾਣੀਏ।"
                        2. Paragraph 1 (The Problem): Explain DETAILED science. Mention how Sodium reacts with Moisture (ਨਮੀ) and Oxygen violently. Mention Exothermic reaction (ਤਾਪ-ਨਿਕਾਸ).
                        3. Paragraph 2 (The Danger): Explain that this heat causes the hydrogen gas to catch Fire (ਅੱਗ). It acts like a small explosion.
                        4. Paragraph 3 (The Solution): Explain deeply how Kerosene creates a barrier layer that cuts off contact with air.
                        
                        Do NOT summarize. Write at least 150-200 words in pure Punjabi.
                        """

                    prompt = f"""
                    Act as an Expert Science Teacher for Class {selected_class}. 
                    Topic: "{user_input}"
                    Language Instructions: {lang_instruction}

                    TASK:
                    Write a detailed, high-quality textbook answer. 
                    Do not be brief. Be thorough.
                    
                    JSON KEYS: "answer", "google_search_query"

                    JSON Example:
                    {{
                        "answer": "(Full detailed paragraph here...)", 
                        "google_search_query": "english query for diagram"
                    }}
                    """
                    
                    completion = client.chat.completions.create(
                        messages=[{"role": "user", "content": prompt}],
                        model="llama-3.3-70b-versatile",
                        response_format={"type": "json_object"}
                    )
                    data = json.loads(completion.choices[0].message.content)
                    
                    st.session_state["pending_search_query"] = data.get("google_search_query", user_input + " diagram")

                    # Stream the Answer
                    final_html
                    
