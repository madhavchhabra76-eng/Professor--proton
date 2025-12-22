import streamlit as st
from groq import Groq
import json
import time
import requests

# -----------------------------------------------------------
# PROFESSOR PROTON - NOTEBOOK MODE (Direct Copy) 📓
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS (Notebook Style) ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span, b { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    /* THE NOTEBOOK BOX */
    .notebook-box { 
        background-color: #ffffff; 
        padding: 25px; 
        border-radius: 5px; 
        margin-bottom: 20px; 
        border: 1px solid #d1d1d1;
        border-left: 8px solid #4285F4; 
        font-size: 18px;
        line-height: 1.8; /* More spacing for reading */
        font-family: 'Georgia', serif; /* Looks like book text */
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
    }
    
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #4285F4 !important; border: none; color: white !important; }
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
        placeholder.markdown(f"<div class='notebook-box'>{current_text} ▌</div>", unsafe_allow_html=True)
        time.sleep(0.02)
    final_html = f"<div class='notebook-box'>{current_text}</div>"
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

# --- 7. MAIN LOGIC (NOTEBOOK MODE) ---
user_input = st.chat_input("Ask a question (e.g. Photosynthesis)...")

if user_input:
    st.session_state.pop("pending_search_query", None)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        answer_ph = st.empty()
        
        with st.spinner("Writing Answer..."):
            try:
                # ----------------------------------------------------
                # 🚨 THE "DIRECT COPY" PROMPT
                # ----------------------------------------------------
                
                lang_instruction = "English"
                if language == "Punjabi":
                    lang_instruction = "Punjabi (Gurmukhi). Use standard textbook language. Do NOT use poetic or complex words. Just clear, simple sentences."

                prompt = f"""
                Act as a Textbook Answer Key for Class {selected_class}. 
                Topic: "{user_input}"
                Language: {lang_instruction}

                INSTRUCTIONS:
                1. **Goal**: Write a paragraph that a student can COPY DIRECTLY into their notebook.
                2. **No Chatting**: Do NOT write "Here is the answer" or "Sure". Start directly with the answer.
                3. **Structure**: 
                   - Start with a clear definition.
                   - Explain how it works in 1-2 sentences.
                   - End with a real-world example.
                   - Keep it all in ONE paragraph.
                4. **Keys**: JSON keys must be "answer" and "google_search_query".

                JSON Structure:
                {{
                    "answer": "Photosynthesis is the process...", 
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

                # Stream the Notebook Answer
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
