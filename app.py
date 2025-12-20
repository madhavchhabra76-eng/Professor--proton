import streamlit as st
from groq import Groq
import json
import time
import requests

# -----------------------------------------------------------
# PROFESSOR PROTON - GOOGLE SEARCH EDITION (Perfect Diagrams) 🔎
# -----------------------------------------------------------

st.set_page_config(page_title="Professor Proton", page_icon="⚛️", layout="centered")

# --- 1. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #ffffff; }
    p, h1, h2, h3, li, div, span, b { color: #000000 !important; font-family: 'Helvetica Neue', sans-serif; }
    
    .definition-box { background-color: #e3f2fd; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #2196f3; }
    .points-box { background-color: #f5f5f5; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #9e9e9e; }
    .formula-box { background-color: #fff3e0; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #ff9800; font-family: 'Courier New', monospace; font-weight: bold; }
    .example-box { background-color: #e8f5e9; padding: 15px; border-radius: 10px; margin-bottom: 20px; border-left: 5px solid #4caf50; }
    
    .stButton button { border-radius: 20px; width: 100%; font-weight: bold; }
    button[kind="primary"] { background-color: #4285F4 !important; border: none; color: white !important; } /* Google Blue */
</style>
""", unsafe_allow_html=True)

# --- 2. KEYS ---
if "GROQ_API_KEY" not in st.secrets: st.error("⚠️ missing GROQ_API_KEY"); st.stop()
if "GOOGLE_API_KEY" not in st.secrets: st.warning("⚠️ missing GOOGLE_API_KEY. Images won't work.")
if "GOOGLE_CX" not in st.secrets: st.warning("⚠️ missing GOOGLE_CX. Images won't work.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. GOOGLE IMAGE SEARCH FUNCTION ---
def get_google_image(search_query):
    if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CX" not in st.secrets:
        return None, "Google keys missing in secrets."
        
    api_key = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CX"]
    
    # Google Custom Search API URL endpoint
    url = "https://www.googleapis.com/customsearch/v1"
    
    params = {
        'q': search_query,      # The search term
        'key': api_key,         # Your API key
        'cx': cx,               # Your Search Engine ID
        'searchType': 'image',  # We want images
        'num': 1,               # Just get the top result
        'safe': 'active',       # Safe search on
        'imgType': 'clipart',   # Prefer clear diagrams over photos
        'fileType': 'png'       # Prefer PNG for clarity
    }
    
    try:
        response = requests.get(url, params=params)
        results = response.json()
        
        if 'items' in results and len(results['items']) > 0:
            # Get the link of the first image result
            image_url = results['items'][0]['link']
            return image_url, None
        else:
            return None, "No suitable diagram found on Google."
            
    except Exception as e:
        return None, f"Search Error: {str(e)}"

# --- 4. HELPER FOR STREAMING TEXT ---
def stream_section(placeholder, box_class, title, content):
    current_text = ""
    for word in content.split():
        current_text += word + " "
        placeholder.markdown(f"<div class='{box_class}'><b>{title}</b><br>{current_text} ▌</div>", unsafe_allow_html=True)
        time.sleep(0.02)
    final_html = f"<div class='{box_class}'><b>{title}</b><br>{current_text}</div>"
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

# --- 6. CHAT HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "image":
             st.image(msg["content"], caption="Google Search Result", use_column_width=True)
        else:
             st.markdown(msg["content"], unsafe_allow_html=True)

# --- 7. MAIN LOGIC ---
user_input = st.chat_input("Ask a question (e.g. Photosynthesis)...")

if user_input:
    st.session_state.pop("pending_search_query", None)
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"): st.write(user_input)

    with st.chat_message("assistant"):
        def_ph = st.empty()
        points_ph = st.empty()
        formula_ph = st.empty()
        ex_ph = st.empty()
        full_final_html = ""

        with st.spinner("Thinking..."):
            try:
                # Ask Groq for text content AND the best Google search query
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}. Topic: "{user_input}"
                
                1. Content: Standard JSON (definition, points, formula, example).
                2. Search Query: Create the perfect short Google Image search query to find a clear, labeled diagram for this topic.
                   - Example for 'Heart': "human heart diagram labeled clear"
                   
                Return JSON:
                {{
                    "definition": "...", "points": ["..."], "formula": "...", "example": "...",
                    "google_search_query": "..."
                }}
                
                Language: {"English" if language == "English" else "Punjabi (Gurmukhi)"}
                """
                
                completion = client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                    response_format={"type": "json_object"}
                )
                data = json.loads(completion.choices[0].message.content)
                
                # Save the search query for the button click
                st.session_state["pending_search_query"] = data.get("google_search_query", user_input + " diagram labeled")

                # Render text boxes
                full_final_html += stream_section(def_ph, "definition-box", "📖 Definition:", data['definition'])
                points_html = "<ul>" + "".join([f"<li>{p}</li>" for p in data['points']]) + "</ul>"
                full_final_html += f"<div class='points-box'><b>⚡ Key Points:</b>{points_html}</div>"
                points_ph.markdown(full_final_html, unsafe_allow_html=True)
                
                if data['formula'] and data['formula'] != "None":
                    full_final_html += stream_section(formula_ph, "formula-box", "🧮 Formula:", data['formula'])
                
                full_final_html += stream_section(ex_ph, "example-box", "🌍 Example:", data['example'])
                
                st.session_state.messages.append({"role": "assistant", "content": full_final_html})
                st.rerun()

            except Exception as e:
                st.error(f"Error: {str(e)}")

# --- 8. BUTTON ---
if "pending_search_query" in st.session_state:
    st.write("") 
    # Only show button if Google keys are present
    if "GOOGLE_API_KEY" in st.secrets and "GOOGLE_CX" in st.secrets:
        if st.button("🔎 Find Diagram on Google", type="primary"):
            with st.spinner("Searching Google for the best diagram..."):
                search_query = st.session_state["pending_search_query"]
                img_url, error = get_google_image(search_query)
                
                if img_url:
                    st.image(img_url, caption=f"Source: Google Search ('{search_query}')", use_column_width=True)
                    # Save image to history with type='image'
                    st.session_state.messages.append({"role": "assistant", "type": "image", "content": img_url})
                    del st.session_state["pending_search_query"]
                    st.rerun()
                else:
                    st.error(error)
    else:
        st.warning("Add Google API Keys to secrets to enable image search.")
