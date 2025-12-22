import streamlit as st
from groq import Groq
import json
import time
import requests

# -----------------------------------------------------------
# PROFESSOR PROTON - FRIENDLY TUTOR EDITION 👨‍🏫
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS (Clean & Readable) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span, b, strong { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* TUTOR ANSWER BOX */
    .tutor-box { 
        background-color: #f0f7ff; 
        padding: 25px; 
        border-radius: 12px; 
        margin-bottom: 20px; 
        border: 1px solid #dbeafe;
        font-size: 19px; /* Bigger text for easy reading */
        line-height: 1.8; 
        color: #1e293b;
    }
    
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #4F46E5 !important; border: none; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. KEYS ---
if "GROQ_API_KEY" not in st.secrets: st.error("⚠️ missing GROQ_API_KEY"); st.stop()

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. GOOGLE SEARCH ---
def get_google_images(search_query):
    if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CX" not in st.secrets:
        return [], "Google keys missing."
        
    api_key = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CX"]
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': search_query, 'key': api_key, 'cx': cx,
        'searchType': 'image', 'num': 3, 'safe': 'active', 'imgType': 'clipart'
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

# --- 7. MAIN LOGIC (TUTOR MODE) ---
user_input = st.chat_input("Ask a question (e.g. Why is sodium kept in kerosene?)...")

if user_input:
    st.session_state.pop("pending_search_query", None)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        answer_ph = st.empty()
        
        with st.spinner("Writing..."):
            try:
                # ----------------------------------------------------
                # 🚨 THE "FRIENDLY TUTOR" PROMPT
                # ----------------------------------------------------
                
                lang_instruction = "English"
                if language == "Punjabi":
                    lang_instruction = """
                    Punjabi (Gurmukhi Script). 
                    CRITICAL: Write like a friendly teacher explaining to a student.
                    1. Use simple, conversational Punjabi words (avoid complex formal translation).
                    2. Explain the 'Why' clearly.
                    3. Highlight key terms in **bold** (e.g. **Sodium**, **Kerosene**).
                    """

                prompt = f"""
                You are a Friendly Science Tutor for Class {selected_class}. 
                Topic: "{user_input}"
                Language: {lang_instruction}

                INSTRUCTIONS:
                1. **Goal**: Write a clear, simple explanation that a student can copy for homework.
                2. **Style**: 
                   - Be direct but helpful. 
                   - Use bolding for important scientific terms.
                   - If asking "Why", start with the reason.
                3. **Format**: ONE single paragraph. No bullet points.
                4. **Keys**: JSON keys must be "answer" and "google_search_query".

                JSON Structure:
                {{
                    "answer": "Sodium is a very reactive metal... (Write full explanation here)", 
                    "google_search_query": "concise english query for google images"
                }}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                st.session_state["pending_search_query"] = data.get("google_search_query", user_input + " diagram")

                # Stream the Tutor Answer
                final_html = stream_text(answer_ph, data['answer'])
                
                st.session_state.messages.append({"role": "assistant", "content": final_html})
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 8. BUTTON ---
if "pending_search_query" in st.session_state:
    st.write("") 
    if "GOOGLE_API_KEY" in st.secrets:
        query = st.session_state["pending_search_query"]
        if st.button(f"🔎 Find Diagrams for: '{query}'", type="primary"):
            with st.spinner("Searching Google..."):
                img_links, error = get_google_images(query)
                
                if img_links:
                    cols = st.columns(3)
                    for i, link in enumerate(img_links):
                        cols[i].image(link, caption=f"Result {i+1}", use_column_width=True)
                    st.session_state.messages.append({"role": "assistant", "type": "images", "content": img_links})
                    del st.session_state["pending_search_query"]
                    st.rerun()
                else:
                    st.error(error)
