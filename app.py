import streamlit as st
from openai import OpenAI
import requests
import time
from streamlit_lottie import st_lottie

# -----------------------------------------------------------
# PROFESSOR PROTON - ANIMATED AVATAR EDITION 🤖
# -----------------------------------------------------------

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
if "GITHUB_TOKEN" not in st.secrets:
    st.error("⚠️ GITHUB_TOKEN is missing.")
    st.stop()

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=st.secrets["GITHUB_TOKEN"],
)

# --- 3. ANIMATION LOADER ---
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

# Load a cute "Science Robot" animation
# You can change this URL to any Lottie file you like!
lottie_url = "https://lottie.host/64c06283-8409-4ce4-a827-0201dc486806/H7e2M7L2Kq.json"
lottie_avatar = load_lottieurl(lottie_url)

# --- 4. GOOGLE SEARCH FUNCTION ---
def get_google_images(search_query):
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

# --- 5. TEXT STREAMER ---
def stream_text(placeholder, text):
    current_text = ""
    for word in text.split():
        current_text += word + " "
        placeholder.markdown(f"<div class='tutor-box'>{current_text} ▌</div>", unsafe_allow_html=True)
        time.sleep(0.02)
    final_html = f"<div class='tutor-box'>{current_text}</div>"
    placeholder.markdown(final_html, unsafe_allow_html=True)
    return final_html

# --- 6. UI HEADER & AVATAR ---
col1, col2 = st.columns([1, 4])

with col1:
    if lottie_avatar:
        st_lottie(lottie_avatar, height=100, key="avatar")
    else:
        st.write("🤖")

with col2:
    st.title("Professor Proton")
    st.caption("Your Friendly Science AI Tutor")

with st.expander("⚙️ Settings", expanded=False):
    selected_class = st.selectbox("Class", [6, 7, 8, 9, 10])
    language = st.radio("Language", ["English", "Punjabi"])
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# --- 7. HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "images":
             cols = st.columns(len(msg["content"]))
             for i, img_url in enumerate(msg["content"]):
                 cols[i].image(img_url, use_column_width=True)
        else:
             st.markdown(msg["content"], unsafe_allow_html=True)

# --- 8. MAIN LOGIC ---
user_input = st.chat_input("Ask a question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        answer_ph = st.empty()
        
        with st.spinner("Thinking..."):
            try:
                # ----------------------------------------------------
                # 🚨 NO STARS PROMPT (Mini Model)
                # ----------------------------------------------------
                
                if language == "Punjabi":
                    system_message = (
                        f"You are 'Professor Proton', a Science teacher for Class {selected_class}."
                        "\n\nSTRICT RULES:\n"
                        "1. Use simple, daily spoken Punjabi (Gurmukhi).\n"
                        "2. DO NOT translate technical terms. Write them in Gurmukhi. "
                        "   (e.g., 'Force' -> 'ਫੋਰਸ', 'Gravity' -> 'ਗ੍ਰੈਵਿਟੀ').\n"
                        "3. NO HINDI WORDS.\n"
                        "4. STRICTLY FORBIDDEN: Do NOT use asterisks (**), bold text, or markdown formatting. Use plain text only.\n"
                        "5. Keep it brief and point-wise."
                    )
                    user_prompt = f"Explain this topic simply: {user_input}"
                else:
                    system_message = (
                        f"You are a professional Science Tutor for Class {selected_class}. "
                        "STRICTLY FORBIDDEN: Do NOT use asterisks (**) or bold text."
                    )
                    user_prompt = f"Question: '{user_input}'. Write a brief, precise answer for exam notes."

                # Using Mini Model
                completion = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {"role": "system", "content": system_message},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.7 
                )
                
                answer_text = completion.choices[0].message.content
                final_html = stream_text(answer_ph, answer_text)
                
                st.session_state.messages.append({"role": "assistant", "content": final_html})
                
                # Search Query Generation
                st.session_state["pending_search_query"] = user_input + " scientific diagram"
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 9. BUTTON ---
if "pending_search_query" in st.session_state:
    st.write("") 
    if "GOOGLE_API_KEY" in st.secrets:
        query = st.session_state["pending_search_query"]
        if st.button(f"🔎 Find Diagrams for: '{user_input}'", type="primary"):
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
