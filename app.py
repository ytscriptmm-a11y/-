import streamlit as st
from google import genai
from google.genai import types
import base64
import io
import time
import json
from PIL import Image

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Silent Cat Movie Maker",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Myanmar:wght@400;500;600&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Outfit', 'Noto Sans Myanmar', sans-serif;
    }
    
    #MainMenu, footer, header {visibility: hidden;}
    .block-container { padding: 1rem 1rem 3rem 1rem; max-width: 1400px; }
    
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: clamp(1.6rem, 4vw, 2.5rem);
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: clamp(0.8rem, 2vw, 0.95rem);
        margin-bottom: 1.2rem;
    }
    
    .step-container {
        display: flex;
        justify-content: center;
        gap: 0.3rem;
        margin: 1rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        padding: 0.4rem 0.7rem;
        border-radius: 50px;
        font-size: 0.7rem;
        font-weight: 500;
    }
    
    .step-active {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .step-completed {
        background: rgba(72, 187, 120, 0.2);
        color: #68d391;
        border: 1px solid rgba(72, 187, 120, 0.3);
    }
    
    .step-pending {
        background: rgba(255, 255, 255, 0.05);
        color: #718096;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    
    .character-card {
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.04));
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .scene-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.7));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    
    .ref-upload-box {
        background: rgba(102, 126, 234, 0.05);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.3rem 0;
        text-align: center;
    }
    
    .ref-upload-box.has-image {
        border-style: solid;
        border-color: rgba(72, 187, 120, 0.5);
        background: rgba(72, 187, 120, 0.05);
    }
    
    .char-label {
        font-size: 0.75rem;
        color: #a0aec0;
        margin-bottom: 0.3rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.9rem;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 10px !important;
        color: #e2e8f0 !important;
    }
    
    .success-alert {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(72, 187, 120, 0.05));
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 10px;
        padding: 0.8rem;
        color: #68d391;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .info-alert {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 10px;
        padding: 0.8rem;
        color: #a0aec0;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .warning-alert {
        background: linear-gradient(135deg, rgba(236, 201, 75, 0.1), rgba(236, 201, 75, 0.05));
        border: 1px solid rgba(236, 201, 75, 0.3);
        border-radius: 10px;
        padding: 0.8rem;
        color: #ecc94b;
        margin: 0.5rem 0;
        font-size: 0.85rem;
    }
    
    .image-container {
        border-radius: 10px;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 1rem 0;
    }
    
    .char-thumb {
        width: 60px;
        height: 60px;
        border-radius: 8px;
        object-fit: cover;
        border: 2px solid rgba(102, 126, 234, 0.3);
    }
    
    @media (max-width: 768px) {
        .block-container { padding: 0.5rem; }
        .glass-card { padding: 0.8rem; }
        .scene-card { padding: 0.8rem; }
    }
    
    .viewerBadge_container__r5tak {display: none;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🔧 SESSION STATE
# ═══════════════════════════════════════════════════════════════════
defaults = {
    'step': 1,
    'script': "",
    'characters': {},  # {name: {prompt, image_data, description}}
    'scenes': [],  # [{text, characters: [name], prompt, ref_images: {char_name: image_data}, generated_image, grok_video, grok_audio}]
    'image_library': {},  # {name: image_data} - ယခင်သုံးခဲ့တဲ့ပုံများ
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# ═══════════════════════════════════════════════════════════════════
# 🔑 API CONFIG
# ═══════════════════════════════════════════════════════════════════
def get_client():
    if "GEMINI_API_KEY" in st.secrets:
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    return None

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILITY FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def img_to_b64(data):
    if not data:
        return None
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    buf = io.BytesIO()
    data.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def pil_from_bytes(data):
    if isinstance(data, bytes):
        return Image.open(io.BytesIO(data))
    return data

# ═══════════════════════════════════════════════════════════════════
# 🤖 AI FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def generate_script(client, topic, model):
    prompt = f"""
You are a scriptwriter for a viral 'Silent Cat Meme Movie'.
Topic: '{topic}'

Characters are ANTHROPOMORPHIC CATS (stand upright, wear clothes, use paws like hands).

Rules:
1. NO dialogue/narration - SILENT movie
2. Focus on visual actions, expressions, body language
3. Write in Burmese (Myanmar)
4. Length: 1-3 minutes video
5. Give characters clear NAMES

Output: Burmese paragraphs with character names.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def extract_characters_ai(client, script, model):
    prompt = f"""
Analyze this script and list ALL character names:
"{script}"

Output JSON array only:
["Character1", "Character2"]

Return ONLY the JSON array.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except:
        return []

def generate_character_prompt(client, char_name, description, model):
    prompt = f"""
Create an image generation prompt for this character:
Name: {char_name}
Description: {description}

Requirements:
- Anthropomorphic cat (stands upright like human)
- Wears clothes
- Cute 3D Pixar style
- Expressive face
- Internet meme style

Output: Single detailed English prompt only.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text.strip()
    except Exception as e:
        return f"Anthropomorphic cat character named {char_name}, {description}, standing upright, wearing clothes, cute 3D Pixar style"

def generate_scene_prompt(client, scene_text, char_names, model):
    prompt = f"""
Create an image generation prompt for this scene:
Scene: {scene_text}
Characters: {', '.join(char_names)}

Requirements:
- Focus on ACTION and SETTING (not character appearance - we have reference images)
- Include pose, emotion, background, lighting
- Add: "maintain exact character appearance from reference"
- Style: cute 3D Pixar animation

Output: Single detailed English prompt only.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text.strip()
    except Exception as e:
        return f"Scene: {scene_text}, characters in action, cute 3D Pixar style"

def generate_image(client, prompt, ref_images=None, model="gemini-2.5-flash-image"):
    try:
        contents = []
        
        if ref_images:
            contents.append("Reference image(s) of the character(s). Generate new image keeping their exact appearance:\n")
            for i, img in enumerate(ref_images):
                if img:
                    pil_img = pil_from_bytes(img)
                    contents.append(pil_img)
                    contents.append(f"\n[Reference {i+1}]\n")
        
        full_prompt = f"""
{prompt}

Style: cute 3D Pixar animation, soft lighting, detailed, expressive, internet meme style, masterpiece
{"CRITICAL: Character must look exactly like reference image(s)." if ref_images else ""}
"""
        contents.append(full_prompt)
        
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(response_modalities=['IMAGE', 'TEXT'])
        )
        
        for part in resp.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data:
                return part.inline_data.data
        return None
    except Exception as e:
        st.error(f"Image error: {e}")
        return None

def generate_grok_prompts(client, scene_prompt, model):
    prompt = f"""
Scene: "{scene_prompt}"

Generate for Grok AI:
1. VIDEO_PROMPT: Motion, camera movement (3-5 sec)
2. AUDIO_PROMPT: Music/sound (no dialogue)

Format:
VIDEO_PROMPT: [text]
AUDIO_PROMPT: [text]
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        result = {"video": "", "audio": ""}
        for line in resp.text.split('\n'):
            if "VIDEO_PROMPT:" in line:
                result["video"] = line.replace("VIDEO_PROMPT:", "").strip()
            if "AUDIO_PROMPT:" in line:
                result["audio"] = line.replace("AUDIO_PROMPT:", "").strip()
        return result
    except:
        return {"video": "", "audio": ""}

# ═══════════════════════════════════════════════════════════════════
# 🎨 UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════
def render_header():
    st.markdown('<h1 class="main-header">🐱 Silent Cat Movie Maker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Character Consistency + Manual Scene Control</p>', unsafe_allow_html=True)

def render_steps(current):
    steps = [("📝", "Script"), ("👤", "Characters"), ("🎬", "Scenes"), ("🖼️", "Generate"), ("🎥", "Export")]
    html = '<div class="step-container">'
    for i, (icon, label) in enumerate(steps, 1):
        cls = "step-completed" if i < current else ("step-active" if i == current else "step-pending")
        html += f'<div class="step-item {cls}">{"✓" if i < current else icon} {label}</div>'
    html += '</div>'
    st.markdown(html, unsafe_allow_html=True)

def render_sidebar():
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        model = st.selectbox("Text Model:", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"], index=0)
        img_model = st.selectbox("Image Model:", ["gemini-2.5-flash-image"], index=0)
        st.markdown("---")
        st.markdown("""
        <div class="info-alert">
        <b>💡 Tips</b><br>
        • Character ပုံ - Upload သို့ Generate<br>
        • Scene - ကိုယ်တိုင်ခွဲနိုင်တယ်<br>
        • Reference - Scene တိုင်းမှာထည့်
        </div>
        """, unsafe_allow_html=True)
        return model, img_model

# ═══════════════════════════════════════════════════════════════════
# 🚀 MAIN APP
# ═══════════════════════════════════════════════════════════════════
def main():
    render_header()
    model, img_model = render_sidebar()
    client = get_client()
    
    if not client:
        st.markdown('<div class="glass-card"><h3>🔑 API Key လိုအပ်ပါတယ်</h3></div>', unsafe_allow_html=True)
        st.stop()
    
    render_steps(st.session_state.step)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: SCRIPT
    # ═══════════════════════════════════════════════════════════════
    if st.session_state.step == 1:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 📝 Step 1: Script ရေးမယ်")
        
        topic = st.text_input("Topic:", "မိုးရွာနေတဲ့ညမှာ ဝမ်းနည်းစွာလမ်းလျှောက်နေတဲ့ကြောင်လေး၊ သူငယ်ချင်းကထီးလာဖြင့်ပေးတယ်")
        
        if st.button("✨ Script ထုတ်မယ်"):
            with st.spinner("ရေးနေပါတယ်..."):
                result = generate_script(client, topic, model)
                if result:
                    st.session_state.script = result
                    st.rerun()
        
        if st.session_state.script:
            st.markdown("---")
            st.session_state.script = st.text_area("Script (ပြင်ဆင်နိုင်ပါတယ်):", st.session_state.script, height=250)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 အသစ်ထုတ်"):
                    st.session_state.script = ""
                    st.rerun()
            with c2:
                if st.button("➡️ Characters", type="primary"):
                    # Auto-extract character names
                    chars = extract_characters_ai(client, st.session_state.script, model)
                    st.session_state.characters = {name: {"prompt": "", "image_data": None, "description": ""} for name in chars}
                    st.session_state.step = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: CHARACTERS (Optional Generate/Upload)
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Step 2: Characters (Optional)")
        
        st.markdown("""
        <div class="info-alert">
        📌 Character ပုံတွေကို Upload လုပ်လည်းရ၊ Prompt နဲ့ Generate လုပ်လည်းရ၊ ကျော်သွားလည်းရပါတယ်။
        </div>
        """, unsafe_allow_html=True)
        
        # Add new character
        with st.expander("➕ Character အသစ်ထည့်မယ်", expanded=False):
            new_name = st.text_input("Character Name:", key="new_char_name")
            if st.button("ထည့်မယ်") and new_name:
                if new_name not in st.session_state.characters:
                    st.session_state.characters[new_name] = {"prompt": "", "image_data": None, "description": ""}
                    st.rerun()
        
        # Display characters
        if st.session_state.characters:
            for char_name in list(st.session_state.characters.keys()):
                char = st.session_state.characters[char_name]
                
                st.markdown(f'<div class="character-card">', unsafe_allow_html=True)
                
                col1, col2, col3 = st.columns([2, 2, 1])
                
                with col1:
                    st.markdown(f"**🐱 {char_name}**")
                    
                    # Description input
                    desc = st.text_input(
                        "Description:",
                        value=char.get('description', ''),
                        key=f"desc_{char_name}",
                        placeholder="ဥပမာ: ဝမ်းနည်းနေတဲ့ကြောင်လေး၊ အပြာရောင်ဟွတ်ဒီးဝတ်ထားတယ်"
                    )
                    st.session_state.characters[char_name]['description'] = desc
                    
                    # Generate prompt button
                    if st.button(f"📝 Prompt ထုတ်", key=f"gen_prompt_{char_name}"):
                        with st.spinner("Prompt ထုတ်နေပါတယ်..."):
                            prompt = generate_character_prompt(client, char_name, desc, model)
                            st.session_state.characters[char_name]['prompt'] = prompt
                            st.rerun()
                    
                    # Editable prompt
                    if char.get('prompt'):
                        st.session_state.characters[char_name]['prompt'] = st.text_area(
                            "Image Prompt:",
                            value=char['prompt'],
                            height=100,
                            key=f"prompt_{char_name}"
                        )
                        
                        # Generate image button
                        if st.button(f"🖼️ ပုံထုတ်", key=f"gen_img_{char_name}"):
                            with st.spinner("ပုံထုတ်နေပါတယ်..."):
                                img = generate_image(client, char['prompt'], model=img_model)
                                if img:
                                    st.session_state.characters[char_name]['image_data'] = img
                                    st.session_state.image_library[char_name] = img
                                    st.rerun()
                
                with col2:
                    # Upload option
                    st.markdown("**သို့ Upload:**")
                    uploaded = st.file_uploader(
                        "ပုံတင်ပါ",
                        type=['png', 'jpg', 'jpeg', 'webp'],
                        key=f"upload_{char_name}",
                        label_visibility="collapsed"
                    )
                    if uploaded:
                        img_data = uploaded.read()
                        st.session_state.characters[char_name]['image_data'] = img_data
                        st.session_state.image_library[char_name] = img_data
                        st.rerun()
                    
                    # Show image if exists
                    if char.get('image_data'):
                        b64 = img_to_b64(char['image_data'])
                        st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:150px;border-radius:8px;">', unsafe_allow_html=True)
                        
                        # Download button
                        st.download_button(
                            "⬇️ Download",
                            data=char['image_data'],
                            file_name=f"{char_name}.png",
                            mime="image/png",
                            key=f"dl_char_{char_name}"
                        )
                
                with col3:
                    if st.button("🗑️", key=f"del_{char_name}"):
                        del st.session_state.characters[char_name]
                        st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="warning-alert">Character မရှိသေးပါ။ ထည့်ပါ သို့ ကျော်သွားပါ။</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Script"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("➡️ Scenes ခွဲမယ်", type="primary"):
                st.session_state.step = 3
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: MANUAL SCENE SPLITTING
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎬 Step 3: Scene ခွဲမယ် (ကိုယ်တိုင်)")
        
        st.markdown("""
        <div class="info-alert">
        📌 Scene တစ်ခုစီကို ကိုယ်တိုင်ထည့်ပါ။ Scene တစ်ခုစီမှာ ပါဝင်မယ့် Characters ကိုလည်း ရွေးပါ။
        </div>
        """, unsafe_allow_html=True)
        
        # Show script for reference
        with st.expander("📄 Script ကြည့်မယ်"):
            st.text(st.session_state.script)
        
        # Add new scene
        st.markdown("#### ➕ Scene အသစ်ထည့်")
        
        new_scene_text = st.text_area(
            "Scene Description (Burmese):",
            placeholder="ဥပမာ: ကြောင်လေးက မိုးထဲမှာ ဝမ်းနည်းစွာ လမ်းလျှောက်နေတယ်။",
            key="new_scene_text",
            height=80
        )
        
        # Character selection for new scene
        char_names = list(st.session_state.characters.keys())
        if char_names:
            selected_chars = st.multiselect(
                "ဒီ Scene မှာပါတဲ့ Characters:",
                options=char_names,
                key="new_scene_chars"
            )
        else:
            selected_chars = []
            st.markdown('<div class="warning-alert">Character မရှိသေးပါ။ Step 2 မှာထည့်ပါ သို့ ဆက်သွားပါ။</div>', unsafe_allow_html=True)
        
        if st.button("➕ Scene ထည့်မယ်"):
            if new_scene_text.strip():
                st.session_state.scenes.append({
                    "text": new_scene_text.strip(),
                    "characters": selected_chars,
                    "prompt": "",
                    "ref_images": {},
                    "generated_image": None,
                    "grok_video": "",
                    "grok_audio": ""
                })
                st.rerun()
        
        st.markdown("---")
        
        # Display existing scenes
        if st.session_state.scenes:
            st.markdown(f"#### 📋 Scenes ({len(st.session_state.scenes)} ခု)")
            
            for i, scene in enumerate(st.session_state.scenes):
                with st.expander(f"Scene {i+1}: {scene['text'][:50]}...", expanded=False):
                    # Edit scene text
                    st.session_state.scenes[i]['text'] = st.text_area(
                        "Description:",
                        value=scene['text'],
                        key=f"scene_text_{i}",
                        height=80
                    )
                    
                    # Edit characters
                    st.session_state.scenes[i]['characters'] = st.multiselect(
                        "Characters:",
                        options=char_names if char_names else [],
                        default=scene.get('characters', []),
                        key=f"scene_chars_{i}"
                    )
                    
                    # Delete button
                    if st.button(f"🗑️ ဖျက်မယ်", key=f"del_scene_{i}"):
                        st.session_state.scenes.pop(i)
                        st.rerun()
        else:
            st.markdown('<div class="warning-alert">Scene မရှိသေးပါ။ အထက်မှာထည့်ပါ။</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Characters"):
                st.session_state.step = 2
                st.rerun()
        with c2:
            if st.button("➡️ Prompts & Generate", type="primary", disabled=len(st.session_state.scenes) == 0):
                st.session_state.step = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 4: GENERATE IMAGES WITH PER-SCENE REFERENCES
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Step 4: ပုံထုတ်မယ် (Reference နဲ့)")
        
        st.markdown("""
        <div class="info-alert">
        📌 Scene တစ်ခုစီအတွက် Prompt စစ်ပြီး Reference ပုံထည့်ပါ။ ပြီးမှပုံထုတ်ပါ။
        </div>
        """, unsafe_allow_html=True)
        
        for i, scene in enumerate(st.session_state.scenes):
            st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
            st.markdown(f"#### Scene {i+1}")
            st.markdown(f"**Action:** {scene['text']}")
            
            scene_chars = scene.get('characters', [])
            if scene_chars:
                st.markdown(f"**Characters:** {', '.join(scene_chars)}")
            
            # Generate prompt button
            col_prompt, col_gen = st.columns([3, 1])
            
            with col_prompt:
                if not scene.get('prompt'):
                    if st.button(f"📝 Prompt ထုတ်", key=f"gen_scene_prompt_{i}"):
                        with st.spinner("Prompt ထုတ်နေပါတယ်..."):
                            prompt = generate_scene_prompt(client, scene['text'], scene_chars, model)
                            st.session_state.scenes[i]['prompt'] = prompt
                            st.rerun()
                
                # Editable prompt
                if scene.get('prompt'):
                    st.session_state.scenes[i]['prompt'] = st.text_area(
                        "Image Prompt:",
                        value=scene['prompt'],
                        key=f"scene_prompt_{i}",
                        height=120
                    )
            
            # Reference images section
            if scene_chars and scene.get('prompt'):
                st.markdown("**🖼️ Reference ပုံများ:**")
                
                ref_cols = st.columns(len(scene_chars))
                
                for j, char_name in enumerate(scene_chars):
                    with ref_cols[j]:
                        st.markdown(f'<div class="ref-upload-box {"has-image" if scene.get("ref_images", {}).get(char_name) else ""}">', unsafe_allow_html=True)
                        st.markdown(f'<div class="char-label">🐱 {char_name}</div>', unsafe_allow_html=True)
                        
                        # Check if image exists in library
                        has_lib_image = char_name in st.session_state.image_library
                        current_ref = scene.get('ref_images', {}).get(char_name)
                        
                        # Show current reference if exists
                        if current_ref:
                            b64 = img_to_b64(current_ref)
                            st.markdown(f'<img src="data:image/png;base64,{b64}" class="char-thumb">', unsafe_allow_html=True)
                        
                        # Option 1: Use from library
                        if has_lib_image:
                            if st.button(f"📚 Library", key=f"use_lib_{i}_{j}", help="Character ပုံမှသုံးမယ်"):
                                if 'ref_images' not in st.session_state.scenes[i]:
                                    st.session_state.scenes[i]['ref_images'] = {}
                                st.session_state.scenes[i]['ref_images'][char_name] = st.session_state.image_library[char_name]
                                st.rerun()
                        
                        # Option 2: Upload new
                        uploaded = st.file_uploader(
                            "Upload",
                            type=['png', 'jpg', 'jpeg'],
                            key=f"ref_upload_{i}_{j}",
                            label_visibility="collapsed"
                        )
                        if uploaded:
                            if 'ref_images' not in st.session_state.scenes[i]:
                                st.session_state.scenes[i]['ref_images'] = {}
                            img_data = uploaded.read()
                            st.session_state.scenes[i]['ref_images'][char_name] = img_data
                            st.session_state.image_library[f"{char_name}_scene{i+1}"] = img_data
                            st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            # Generate image section
            col_btn, col_img = st.columns([1, 2])
            
            with col_btn:
                if scene.get('prompt'):
                    if st.button(f"🖼️ ပုံထုတ်မယ်", key=f"gen_img_{i}", use_container_width=True):
                        with st.spinner("ပုံထုတ်နေပါတယ်..."):
                            # Collect reference images
                            ref_imgs = list(scene.get('ref_images', {}).values())
                            
                            img = generate_image(client, scene['prompt'], ref_imgs if ref_imgs else None, img_model)
                            if img:
                                st.session_state.scenes[i]['generated_image'] = img
                                st.rerun()
            
            with col_img:
                if scene.get('generated_image'):
                    b64 = img_to_b64(scene['generated_image'])
                    st.markdown(f'<div class="image-container"><img src="data:image/png;base64,{b64}" style="width:100%;border-radius:8px;"></div>', unsafe_allow_html=True)
                    
                    c1, c2 = st.columns(2)
                    with c1:
                        st.download_button(
                            "⬇️ Download",
                            data=scene['generated_image'],
                            file_name=f"scene_{i+1}.png",
                            mime="image/png",
                            key=f"dl_scene_{i}"
                        )
                    with c2:
                        if st.button(f"🎥 Grok Export", key=f"grok_{i}"):
                            with st.spinner("Grok prompts..."):
                                grok = generate_grok_prompts(client, scene['prompt'], model)
                                st.session_state.scenes[i]['grok_video'] = grok['video']
                                st.session_state.scenes[i]['grok_audio'] = grok['audio']
                                st.rerun()
                    
                    # Show Grok prompts if generated
                    if scene.get('grok_video') or scene.get('grok_audio'):
                        st.markdown("**🎥 Grok Prompts:**")
                        st.text_area("Video:", scene.get('grok_video', ''), height=60, key=f"grok_v_{i}")
                        st.text_area("Audio:", scene.get('grok_audio', ''), height=60, key=f"grok_a_{i}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Generate all button
        if st.button("🖼️ အားလုံးထုတ်မယ်", use_container_width=True):
            progress = st.progress(0)
            for i, scene in enumerate(st.session_state.scenes):
                if scene.get('prompt') and not scene.get('generated_image'):
                    ref_imgs = list(scene.get('ref_images', {}).values())
                    img = generate_image(client, scene['prompt'], ref_imgs if ref_imgs else None, img_model)
                    if img:
                        st.session_state.scenes[i]['generated_image'] = img
                    time.sleep(1.5)
                progress.progress((i + 1) / len(st.session_state.scenes))
            st.rerun()
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Scenes ပြင်မယ်"):
                st.session_state.step = 3
                st.rerun()
        with c2:
            if st.button("➡️ Final Export", type="primary"):
                st.session_state.step = 5
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 5: FINAL EXPORT
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 5:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎥 Step 5: Final Export")
        
        st.markdown('<div class="success-alert">✅ Export အဆင်သင့်ဖြစ်ပါပြီ!</div>', unsafe_allow_html=True)
        
        # Generate all Grok prompts if not done
        for i, scene in enumerate(st.session_state.scenes):
            if scene.get('generated_image') and not scene.get('grok_video'):
                grok = generate_grok_prompts(client, scene.get('prompt', ''), model)
                st.session_state.scenes[i]['grok_video'] = grok['video']
                st.session_state.scenes[i]['grok_audio'] = grok['audio']
        
        for i, scene in enumerate(st.session_state.scenes):
            st.markdown(f"#### Scene {i+1}")
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                if scene.get('generated_image'):
                    b64 = img_to_b64(scene['generated_image'])
                    st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;border-radius:8px;">', unsafe_allow_html=True)
                    st.download_button(
                        "⬇️ Download",
                        data=scene['generated_image'],
                        file_name=f"final_scene_{i+1}.png",
                        mime="image/png",
                        key=f"final_dl_{i}"
                    )
                else:
                    st.warning("ပုံမထုတ်ရသေးပါ")
            
            with c2:
                st.text_area("🎥 Video Prompt:", scene.get('grok_video', ''), height=70, key=f"exp_v_{i}")
                st.text_area("🔊 Audio Prompt:", scene.get('grok_audio', ''), height=70, key=f"exp_a_{i}")
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ ပြင်ဆင်မယ်"):
                st.session_state.step = 4
                st.rerun()
        with c2:
            if st.button("🔄 အစကနေပြန်စမယ်"):
                for key in defaults:
                    st.session_state[key] = defaults[key] if not isinstance(defaults[key], (dict, list)) else type(defaults[key])()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
