import streamlit as st
from groq import Groq
import json
import time
import requests

# -----------------------------------------------------------
# PROFESSOR PROTON - GALLERY EDITION (3 Images) 🖼️
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
    button[kind="primary"] { background-color: #4285F4 !important; border: none; color: white !important; }
</style>
""", unsafe_allow_html=True)

# --- 2. KEYS ---
if "GROQ_API_KEY" not in st.secrets: st.error("⚠️ missing GROQ_API_KEY"); st.stop()
if "GOOGLE_API_KEY" not in st.secrets: st.warning("⚠️ missing GOOGLE_API_KEY. Images won't work.")
if "GOOGLE_CX" not in st.secrets: st.warning("⚠️ missing GOOGLE_CX. Images won't work.")

client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# --- 3. GOOGLE SEARCH (Fetch 3 Images) ---
def get_google_images(search_query):
    if "GOOGLE_API_KEY" not in st.secrets or "GOOGLE_CX" not in st.secrets:
        return [], "Google keys missing."
        
    api_key = st.secrets["GOOGLE_API_KEY"]
    cx = st.secrets["GOOGLE_CX"]
    url = "https://www.googleapis.com/customsearch/v1"
    
    # Updated Params: Fetch 3 results, Removed 'png' restriction for more results
    params = {
        'q': search_query,
        'key': api_key,
        'cx': cx,
        'searchType': 'image',
        'num': 3,              # <--- GET 3 IMAGES
        'safe': 'active',
        'imgType': 'clipart'   # Prefer illustrations over photos
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

# --- 4. HELPER ---
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

# --- 6. HISTORY ---
if "messages" not in st.session_state: st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("type") == "images":
             # Display saved images in a row
             cols = st.columns(len(msg["content"]))
             for i, img_url in enumerate(msg["content"]):
                 cols[i].image(img_url, use_column_width=True)
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
                # Ask Groq to create a specific search query
                prompt = f"""
                Act as a Science Teacher for Class {selected_class}. Topic: "{user_input}"
                
                1. Content: Standard JSON.
                2. Search Query: Create a specific Google Images search query for a diagram.
                   - GOOD: "diagram of photosynthesis process labeled for kids"
                   - BAD: "photosynthesis"
                   
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
                
                st.session_state["pending_search_query"] = data.get("google_search_query", user_input + " diagram")

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
    if "GOOGLE_API_KEY" in st.secrets:
        # Show the user what we are searching for (Transparency!)
        query = st.session_state["pending_search_query"]
        if st.button(f"🔎 Find Diagrams for: '{query}'", type="primary"):
            with st.spinner("Searching Google..."):
                img_links, error = get_google_images(query)
                
                if img_links:
                    # Display 3 images in a row
                    cols = st.columns(3)
                    for i, link in enumerate(img_links):
                        cols[i].image(link, caption=f"Result {i+1}", use_column_width=True)
                    
                    # Save to history
                    st.session_state.messages.append({"role": "assistant", "type": "images", "content": img_links})
                    del st.session_state["pending_search_query"]
                    st.rerun()
                else:
                    st.error(error)
