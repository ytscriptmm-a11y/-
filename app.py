import streamlit as st
from google import genai
from google.genai import types
import base64
import io
import time
import json
from PIL import Image

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & CSS
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
        font-size: clamp(1.5rem, 4vw, 2.2rem);
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.2rem;
    }
    
    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: clamp(0.75rem, 2vw, 0.9rem);
        margin-bottom: 1rem;
    }
    
    .step-container {
        display: flex;
        justify-content: center;
        gap: 0.25rem;
        margin: 0.8rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        padding: 0.35rem 0.6rem;
        border-radius: 50px;
        font-size: 0.65rem;
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
        border-radius: 14px;
        padding: 1rem;
        margin: 0.6rem 0;
    }
    
    .character-card {
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.08), rgba(118, 75, 162, 0.04));
        border: 1px solid rgba(102, 126, 234, 0.2);
        border-radius: 10px;
        padding: 0.8rem;
        margin: 0.4rem 0;
    }
    
    .scene-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.9), rgba(22, 33, 62, 0.7));
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        padding: 1rem;
        margin: 0.6rem 0;
    }
    
    .scene-preview {
        background: rgba(102, 126, 234, 0.05);
        border: 1px dashed rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        padding: 0.6rem;
        margin: 0.3rem 0;
        font-size: 0.8rem;
    }
    
    .ref-box {
        background: rgba(102, 126, 234, 0.05);
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        padding: 0.5rem;
        text-align: center;
        min-height: 80px;
    }
    
    .ref-box.has-img {
        border-style: solid;
        border-color: rgba(72, 187, 120, 0.5);
        background: rgba(72, 187, 120, 0.05);
    }
    
    .char-tag {
        display: inline-block;
        background: rgba(102, 126, 234, 0.2);
        color: #a0aec0;
        padding: 0.2rem 0.5rem;
        border-radius: 4px;
        font-size: 0.7rem;
        margin: 0.1rem;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        font-size: 0.85rem;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .small-btn {
        font-size: 0.75rem !important;
        padding: 0.3rem 0.6rem !important;
    }
    
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 8px !important;
        color: #e2e8f0 !important;
        font-size: 0.85rem !important;
    }
    
    .success-box {
        background: rgba(72, 187, 120, 0.1);
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 8px;
        padding: 0.6rem;
        color: #68d391;
        font-size: 0.8rem;
    }
    
    .info-box {
        background: rgba(102, 126, 234, 0.1);
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 8px;
        padding: 0.6rem;
        color: #a0aec0;
        font-size: 0.8rem;
    }
    
    .warn-box {
        background: rgba(236, 201, 75, 0.1);
        border: 1px solid rgba(236, 201, 75, 0.3);
        border-radius: 8px;
        padding: 0.6rem;
        color: #ecc94b;
        font-size: 0.8rem;
    }
    
    .img-container {
        border-radius: 8px;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.1);
    }
    
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 0.8rem 0;
    }
    
    .copy-btn {
        background: rgba(102, 126, 234, 0.2) !important;
        border: 1px solid rgba(102, 126, 234, 0.3) !important;
    }
    
    @media (max-width: 768px) {
        .block-container { padding: 0.5rem; }
        .glass-card, .scene-card { padding: 0.7rem; }
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
    'characters': {},  # {name: {description, prompt, image_data}}
    'scenes': [],      # [{text, characters, prompt, ref_images, generated_image, grok_video, grok_audio}]
    'image_library': {},  # {name: image_data}
}

for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v if not isinstance(v, (dict, list)) else type(v)()

# ═══════════════════════════════════════════════════════════════════
# 🔑 API
# ═══════════════════════════════════════════════════════════════════
def get_client():
    if "GEMINI_API_KEY" in st.secrets:
        return genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
    return None

# ═══════════════════════════════════════════════════════════════════
# 🛠️ UTILS
# ═══════════════════════════════════════════════════════════════════
def img_to_b64(data):
    if not data: return None
    if isinstance(data, bytes):
        return base64.b64encode(data).decode('utf-8')
    buf = io.BytesIO()
    data.save(buf, format='PNG')
    return base64.b64encode(buf.getvalue()).decode('utf-8')

def pil_from_bytes(data):
    return Image.open(io.BytesIO(data)) if isinstance(data, bytes) else data

# ═══════════════════════════════════════════════════════════════════
# 🤖 AI FUNCTIONS
# ═══════════════════════════════════════════════════════════════════
def generate_script(client, topic, model):
    prompt = f"""
You are a scriptwriter for a viral 'Silent Cat Meme Movie'.
Topic: '{topic}'

Characters are ANTHROPOMORPHIC CATS (stand upright like humans, wear clothes, use paws like hands).

Rules:
1. NO dialogue - SILENT movie (visual storytelling only)
2. Focus on actions, expressions, body language
3. Write in Burmese (Myanmar language)
4. Length: 1-3 minutes video
5. Give each character a clear, memorable NAME

Output: Burmese paragraphs describing the visual story with character names.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def extract_characters_with_details(client, script, model):
    """Extract characters with story-appropriate descriptions"""
    prompt = f"""
Analyze this Burmese script and extract ALL characters:

Script:
"{script}"

For EACH character, provide:
1. name: Character's name (as in script)
2. description: A story-appropriate character description in Burmese that includes:
   - Personality/traits (ဥပမာ: ရွှင်လန်းတဲ့၊ ဝမ်းနည်းတဲ့၊ သတ္တိရှိတဲ့)
   - Appearance (ဥပမာ: လှပတဲ့၊ ချစ်စရာကောင်းတဲ့)
   - Typical clothing style (ဥပမာ: ဟွတ်ဒီးဝတ်တဲ့၊ ဂါဝန်လှလှလေးဝတ်တဲ့)
   - Role in story (ဥပမာ: အဓိကဇာတ်ကောင်၊ သူငယ်ချင်း)

Output JSON array ONLY:
[
  {{
    "name": "မမေသဲ",
    "description": "လှပပြီး ကောက်ကျစ်ဆံပင်ရှိတဲ့ ကြောင်ကောင်မလေး။ ဂါဝန်လှလှလေးတွေ ဝတ်ဆင်တတ်တယ်။ ရွှင်လန်းပြီး သူများကိုကူညီဖို့ကြိုးစားတဲ့ စိတ်ထားရှိတယ်။ ဇာတ်လမ်းထဲမှာ အဓိကဇာတ်ကောင်ဖြစ်တယ်။"
  }}
]
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        chars = json.loads(text)
        return {c['name']: {'description': c['description'], 'prompt': '', 'image_data': None} for c in chars}
    except Exception as e:
        st.error(f"Character extraction error: {e}")
        return {}

def generate_character_prompt(client, char_name, description, model):
    prompt = f"""
Create an image generation prompt for this character:

Name: {char_name}
Description: {description}

Requirements:
- Anthropomorphic cat (stands upright on two legs like human)
- Has human-like hands (paws used like hands)
- Wears clothes as described
- Cute 3D Pixar/Disney style animation
- Expressive face with emotions
- Internet meme style, adorable
- Aspect ratio 3:4 (portrait)

Output: One detailed English prompt only. No explanations.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text.strip()
    except:
        return f"Anthropomorphic cat named {char_name}, standing upright like human, {description}, cute 3D Pixar style, expressive, portrait 3:4"

def generate_scenes_from_script(client, script, characters, num_scenes, model):
    """AI generates scene breakdown"""
    char_list = "\n".join([f"- {name} (#{i+1}): {info['description']}" for i, (name, info) in enumerate(characters.items())])
    
    prompt = f"""
Split this script into exactly {num_scenes} scenes for a silent movie:

Script:
"{script}"

CHARACTERS (with ID numbers for clarity):
{char_list}

For EACH scene provide:
1. scene_text: Visual action description in Burmese (1-2 sentences)
2. characters: List of character NAMES who appear in this scene

IMPORTANT: 
- Use EXACT character names from the list above
- Be precise about which characters are in each scene
- If multiple characters interact, list ALL of them

Output JSON array ONLY:
[
  {{"scene_text": "...", "characters": ["name1", "name2"]}}
]
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1].replace("json", "").strip()
        return json.loads(text)
    except Exception as e:
        st.error(f"Scene generation error: {e}")
        return []

def generate_scene_prompt(client, scene_text, char_names, char_descriptions, model):
    """Generate image prompt with clear character identification"""
    
    # Build detailed character reference
    char_details = []
    for i, name in enumerate(char_names):
        desc = char_descriptions.get(name, "anthropomorphic cat")
        char_details.append(f"Character {i+1} ({name}): {desc}")
    
    char_info = "\n".join(char_details)
    
    prompt = f"""
Create an image generation prompt for this scene:

Scene Action: {scene_text}

Characters in this scene:
{char_info}

Requirements:
- Focus on ACTION, POSE, EMOTION, and SETTING
- Do NOT describe character appearance in detail (we have reference images)
- Include: "maintain exact appearance from reference image"
- If multiple characters: clearly describe their positions and interactions
- Style: cute 3D Pixar animation, soft lighting
- Aspect ratio: 3:4 (portrait orientation)
- Add: "Character 1 is [name], Character 2 is [name]" for clarity

Output: One detailed English prompt only.
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        return resp.text.strip()
    except:
        return f"Scene: {scene_text}, characters in action, cute 3D Pixar style, 3:4 aspect ratio"

def generate_image(client, prompt, ref_images=None, model="gemini-2.5-flash-image"):
    """Generate image with reference and 3:4 aspect ratio"""
    try:
        contents = []
        
        # Add reference images with clear labeling
        if ref_images:
            contents.append("REFERENCE IMAGES - Generate new image keeping these exact character appearances:\n\n")
            for i, (char_name, img) in enumerate(ref_images.items()):
                if img:
                    pil_img = pil_from_bytes(img)
                    contents.append(f"CHARACTER {i+1} ({char_name}):\n")
                    contents.append(pil_img)
                    contents.append("\n\n")
        
        full_prompt = f"""
{prompt}

CRITICAL REQUIREMENTS:
- Aspect ratio: 3:4 (portrait orientation)
- Style: cute 3D Pixar animation, soft lighting, detailed fur, expressive faces
- Characters MUST look exactly like their reference images
- Internet meme style, adorable, high quality
{"- Each character must be clearly distinguishable and match their reference" if ref_images and len(ref_images) > 1 else ""}
"""
        contents.append(full_prompt)
        
        resp = client.models.generate_content(
            model=model,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
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

Generate Grok AI prompts:
1. VIDEO_PROMPT: Motion/camera movement description (3-5 seconds)
2. AUDIO_PROMPT: Background music and sound effects (no dialogue)

Format exactly:
VIDEO_PROMPT: [text]
AUDIO_PROMPT: [text]
"""
    try:
        resp = client.models.generate_content(model=model, contents=[prompt])
        result = {"video": "", "audio": ""}
        for line in resp.text.split('\n'):
            if "VIDEO_PROMPT:" in line:
                result["video"] = line.split("VIDEO_PROMPT:")[1].strip()
            if "AUDIO_PROMPT:" in line:
                result["audio"] = line.split("AUDIO_PROMPT:")[1].strip()
        return result
    except:
        return {"video": "", "audio": ""}

# ═══════════════════════════════════════════════════════════════════
# 🎨 UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════
def render_header():
    st.markdown('<h1 class="main-header">🐱 Silent Cat Movie Maker v4</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Character Consistency + AI/Manual Scene Control + Batch Generate</p>', unsafe_allow_html=True)

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
        model = st.selectbox("Text Model:", ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-1.5-flash"])
        img_model = st.selectbox("Image Model:", ["gemini-2.5-flash-image"])
        num_scenes = st.slider("AI Scene Count:", 4, 15, 8)
        
        st.markdown("---")
        st.markdown("""
        <div class="info-box">
        <b>💡 Features</b><br>
        • AI + Manual scene split<br>
        • Per-scene reference images<br>
        • Batch generate all<br>
        • 3:4 aspect ratio<br>
        • Copy prompts for Grok
        </div>
        """, unsafe_allow_html=True)
        
        return model, img_model, num_scenes

# ═══════════════════════════════════════════════════════════════════
# 🚀 MAIN APP
# ═══════════════════════════════════════════════════════════════════
def main():
    render_header()
    model, img_model, num_scenes = render_sidebar()
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
        
        topic = st.text_input("Topic:", "မိုးရွာနေတဲ့ညမှာ ဝမ်းနည်းစွာလမ်းလျှောက်နေတဲ့ မမေသဲ၊ သူ့သူငယ်ချင်း ကိုမျိုးက ထီးလာဖြင့်ပေးတယ်")
        
        if st.button("✨ Script ထုတ်မယ်"):
            with st.spinner("Script ရေးနေပါတယ်..."):
                result = generate_script(client, topic, model)
                if result:
                    st.session_state.script = result
                    st.rerun()
        
        if st.session_state.script:
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            st.session_state.script = st.text_area("Script (ပြင်ဆင်နိုင်ပါတယ်):", st.session_state.script, height=220)
            
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🔄 အသစ်ထုတ်"):
                    st.session_state.script = ""
                    st.rerun()
            with c2:
                if st.button("➡️ Characters", type="primary"):
                    with st.spinner("Characters ခွဲထုတ်နေပါတယ်..."):
                        chars = extract_characters_with_details(client, st.session_state.script, model)
                        st.session_state.characters = chars
                    st.session_state.step = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: CHARACTERS
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 2:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 👤 Step 2: Characters (Optional)")
        
        st.markdown('<div class="info-box">📌 Character ပုံတွေကို Upload/Generate လုပ်လည်းရ၊ ကျော်သွားလည်းရပါတယ်။</div>', unsafe_allow_html=True)
        
        # Add new character
        with st.expander("➕ Character အသစ်ထည့်", expanded=False):
            nc1, nc2 = st.columns(2)
            with nc1:
                new_name = st.text_input("Name:", key="new_char")
            with nc2:
                new_desc = st.text_input("Description:", key="new_desc")
            if st.button("ထည့်မယ်") and new_name:
                st.session_state.characters[new_name] = {'description': new_desc, 'prompt': '', 'image_data': None}
                st.rerun()
        
        # Display characters
        for idx, (char_name, char_info) in enumerate(list(st.session_state.characters.items())):
            st.markdown(f'<div class="character-card">', unsafe_allow_html=True)
            
            c1, c2, c3 = st.columns([2, 2, 0.5])
            
            with c1:
                st.markdown(f"**🐱 #{idx+1} {char_name}**")
                
                # Description (AI generated, editable)
                st.session_state.characters[char_name]['description'] = st.text_area(
                    "Description:",
                    value=char_info.get('description', ''),
                    key=f"desc_{idx}",
                    height=80
                )
                
                # Generate prompt
                if st.button(f"📝 Prompt ထုတ်", key=f"gp_{idx}"):
                    with st.spinner("..."):
                        p = generate_character_prompt(client, char_name, char_info['description'], model)
                        st.session_state.characters[char_name]['prompt'] = p
                        st.rerun()
                
                # Show/edit prompt
                if char_info.get('prompt'):
                    st.session_state.characters[char_name]['prompt'] = st.text_area(
                        "Image Prompt:",
                        value=char_info['prompt'],
                        key=f"prompt_{idx}",
                        height=80
                    )
                    
                    if st.button(f"🖼️ ပုံထုတ်", key=f"gi_{idx}"):
                        with st.spinner("ပုံထုတ်နေပါတယ်..."):
                            img = generate_image(client, char_info['prompt'], model=img_model)
                            if img:
                                st.session_state.characters[char_name]['image_data'] = img
                                st.session_state.image_library[char_name] = img
                                st.rerun()
            
            with c2:
                st.markdown("**📤 Upload:**")
                uploaded = st.file_uploader("ပုံတင်ပါ", type=['png','jpg','jpeg','webp'], key=f"up_{idx}", label_visibility="collapsed")
                if uploaded:
                    img_data = uploaded.read()
                    st.session_state.characters[char_name]['image_data'] = img_data
                    st.session_state.image_library[char_name] = img_data
                    st.rerun()
                
                # Show image
                if char_info.get('image_data'):
                    b64 = img_to_b64(char_info['image_data'])
                    st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;max-width:140px;border-radius:8px;">', unsafe_allow_html=True)
                    st.download_button("⬇️", data=char_info['image_data'], file_name=f"{char_name}.png", mime="image/png", key=f"dl_{idx}")
            
            with c3:
                if st.button("🗑️", key=f"del_{idx}"):
                    del st.session_state.characters[char_name]
                    if char_name in st.session_state.image_library:
                        del st.session_state.image_library[char_name]
                    st.rerun()
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        if not st.session_state.characters:
            st.markdown('<div class="warn-box">Character မရှိသေးပါ။ ထည့်ပါ သို့ ကျော်သွားပါ။</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Script"):
                st.session_state.step = 1
                st.rerun()
        with c2:
            if st.button("➡️ Scenes", type="primary"):
                st.session_state.step = 3
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: SCENES (AI + Manual)
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 3:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎬 Step 3: Scene ခွဲမယ်")
        
        st.markdown('<div class="info-box">📌 AI နဲ့ခွဲလည်းရ၊ ကိုယ်တိုင်ခွဲလည်းရ၊ AI ခွဲထားတာကို ပြင်လည်းရပါတယ်။</div>', unsafe_allow_html=True)
        
        # Script reference
        with st.expander("📄 Script ကြည့်မယ်"):
            st.text(st.session_state.script)
        
        # AI Generate Scenes
        st.markdown("#### 🤖 AI နဲ့ Scene ခွဲမယ်")
        c1, c2 = st.columns([3, 1])
        with c2:
            if st.button("🤖 AI ခွဲမယ်", use_container_width=True):
                with st.spinner(f"{num_scenes} scenes ခွဲနေပါတယ်..."):
                    scenes = generate_scenes_from_script(client, st.session_state.script, st.session_state.characters, num_scenes, model)
                    st.session_state.scenes = [
                        {'text': s['scene_text'], 'characters': s['characters'], 'prompt': '', 'ref_images': {}, 'generated_image': None, 'grok_video': '', 'grok_audio': ''}
                        for s in scenes
                    ]
                    st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Manual Add Scene
        st.markdown("#### ✏️ ကိုယ်တိုင် Scene ထည့်မယ်")
        
        new_text = st.text_area("Scene Description:", placeholder="ဥပမာ: မမေသဲက မိုးထဲမှာ ဝမ်းနည်းစွာ လမ်းလျှောက်နေတယ်။", key="new_scene", height=60)
        
        char_names = list(st.session_state.characters.keys())
        if char_names:
            selected = st.multiselect("Characters:", char_names, key="new_chars")
        else:
            selected = []
        
        if st.button("➕ Scene ထည့်"):
            if new_text.strip():
                st.session_state.scenes.append({
                    'text': new_text.strip(),
                    'characters': selected,
                    'prompt': '',
                    'ref_images': {},
                    'generated_image': None,
                    'grok_video': '',
                    'grok_audio': ''
                })
                st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # Display/Edit Scenes
        if st.session_state.scenes:
            st.markdown(f"#### 📋 Scenes ({len(st.session_state.scenes)} ခု)")
            
            for i, scene in enumerate(st.session_state.scenes):
                with st.expander(f"Scene {i+1}: {scene['text'][:40]}...", expanded=False):
                    # Edit text
                    st.session_state.scenes[i]['text'] = st.text_area(
                        "Description:",
                        value=scene['text'],
                        key=f"st_{i}",
                        height=60
                    )
                    
                    # Edit characters
                    st.session_state.scenes[i]['characters'] = st.multiselect(
                        "Characters:",
                        options=char_names if char_names else [],
                        default=[c for c in scene.get('characters', []) if c in char_names],
                        key=f"sc_{i}"
                    )
                    
                    # Preview
                    chars_preview = ", ".join([f"#{char_names.index(c)+1 if c in char_names else '?'} {c}" for c in scene['characters']]) if scene['characters'] else "No characters"
                    st.markdown(f'<div class="scene-preview">👥 {chars_preview}</div>', unsafe_allow_html=True)
                    
                    # Delete
                    if st.button(f"🗑️ ဖျက်မယ်", key=f"ds_{i}"):
                        st.session_state.scenes.pop(i)
                        st.rerun()
        else:
            st.markdown('<div class="warn-box">Scene မရှိသေးပါ။ AI နဲ့ခွဲပါ သို့ ကိုယ်တိုင်ထည့်ပါ။</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Characters"):
                st.session_state.step = 2
                st.rerun()
        with c2:
            if st.button("➡️ Generate", type="primary", disabled=len(st.session_state.scenes) == 0):
                st.session_state.step = 4
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 4: GENERATE WITH REFERENCES
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 4:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Step 4: ပုံထုတ်မယ်")
        
        st.markdown('<div class="info-box">📌 Scene တစ်ခုစီအတွက် Reference ပုံထည့်ပြီး ပုံထုတ်ပါ။ (3:4 Aspect Ratio)</div>', unsafe_allow_html=True)
        
        char_names = list(st.session_state.characters.keys())
        char_descs = {name: info['description'] for name, info in st.session_state.characters.items()}
        
        # ═══ BATCH GENERATE ALL ═══
        st.markdown("#### ⚡ Batch Generate")
        
        if st.button("🖼️ ပုံအားလုံး ထုတ်မယ် (Library References နဲ့)", use_container_width=True):
            progress = st.progress(0)
            status = st.empty()
            
            for i, scene in enumerate(st.session_state.scenes):
                status.text(f"Scene {i+1}/{len(st.session_state.scenes)} ထုတ်နေပါတယ်...")
                
                # Generate prompt if not exists
                if not scene.get('prompt'):
                    prompt = generate_scene_prompt(client, scene['text'], scene['characters'], char_descs, model)
                    st.session_state.scenes[i]['prompt'] = prompt
                
                # Use library images as references
                ref_imgs = {}
                for char in scene['characters']:
                    if char in st.session_state.image_library:
                        ref_imgs[char] = st.session_state.image_library[char]
                
                # Generate image
                img = generate_image(client, st.session_state.scenes[i]['prompt'], ref_imgs if ref_imgs else None, img_model)
                if img:
                    st.session_state.scenes[i]['generated_image'] = img
                
                progress.progress((i + 1) / len(st.session_state.scenes))
                time.sleep(1.5)
            
            status.text("✅ ပုံအားလုံး ထုတ်ပြီးပါပြီ!")
            st.rerun()
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        # ═══ INDIVIDUAL SCENES ═══
        for i, scene in enumerate(st.session_state.scenes):
            st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
            st.markdown(f"#### Scene {i+1}")
            st.markdown(f"**Action:** {scene['text']}")
            
            # Characters in scene
            if scene['characters']:
                chars_html = " ".join([f'<span class="char-tag">#{char_names.index(c)+1 if c in char_names else "?"} {c}</span>' for c in scene['characters']])
                st.markdown(f"**Characters:** {chars_html}", unsafe_allow_html=True)
            
            # Generate prompt
            col_p, col_b = st.columns([4, 1])
            with col_b:
                if st.button("📝 Prompt", key=f"gsp_{i}"):
                    with st.spinner("..."):
                        p = generate_scene_prompt(client, scene['text'], scene['characters'], char_descs, model)
                        st.session_state.scenes[i]['prompt'] = p
                        st.rerun()
            
            # Prompt textarea
            if scene.get('prompt') or True:
                st.session_state.scenes[i]['prompt'] = st.text_area(
                    "Image Prompt:",
                    value=scene.get('prompt', ''),
                    key=f"sp_{i}",
                    height=80
                )
            
            # Reference images per character
            if scene['characters']:
                st.markdown("**🖼️ Reference Images:**")
                ref_cols = st.columns(min(len(scene['characters']), 4))
                
                for j, char in enumerate(scene['characters']):
                    with ref_cols[j % len(ref_cols)]:
                        has_ref = char in scene.get('ref_images', {}) and scene['ref_images'][char]
                        has_lib = char in st.session_state.image_library
                        
                        st.markdown(f'<div class="ref-box {"has-img" if has_ref else ""}">', unsafe_allow_html=True)
                        st.markdown(f"**#{char_names.index(char)+1 if char in char_names else '?'} {char}**")
                        
                        # Show current ref
                        if has_ref:
                            b64 = img_to_b64(scene['ref_images'][char])
                            st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:60px;height:60px;border-radius:6px;object-fit:cover;">', unsafe_allow_html=True)
                            
                            # Remove button
                            if st.button("❌ ဖယ်မယ်", key=f"rem_{i}_{j}"):
                                del st.session_state.scenes[i]['ref_images'][char]
                                st.rerun()
                        else:
                            # Use from library
                            if has_lib:
                                if st.button("📚 Library", key=f"lib_{i}_{j}"):
                                    if 'ref_images' not in st.session_state.scenes[i]:
                                        st.session_state.scenes[i]['ref_images'] = {}
                                    st.session_state.scenes[i]['ref_images'][char] = st.session_state.image_library[char]
                                    st.rerun()
                            
                            # Upload
                            up = st.file_uploader("Upload", type=['png','jpg','jpeg'], key=f"ref_{i}_{j}", label_visibility="collapsed")
                            if up:
                                if 'ref_images' not in st.session_state.scenes[i]:
                                    st.session_state.scenes[i]['ref_images'] = {}
                                st.session_state.scenes[i]['ref_images'][char] = up.read()
                                st.rerun()
                        
                        st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
            
            # Generate / Regenerate buttons and result
            col_gen, col_img = st.columns([1, 2])
            
            with col_gen:
                if st.button("🖼️ ပုံထုတ်", key=f"gen_{i}", use_container_width=True):
                    with st.spinner("ထုတ်နေပါတယ်..."):
                        ref_imgs = scene.get('ref_images', {})
                        img = generate_image(client, scene['prompt'], ref_imgs if ref_imgs else None, img_model)
                        if img:
                            st.session_state.scenes[i]['generated_image'] = img
                            st.rerun()
                
                if scene.get('generated_image'):
                    if st.button("🔄 အသစ်ထုတ်", key=f"regen_{i}", use_container_width=True):
                        with st.spinner("..."):
                            ref_imgs = scene.get('ref_images', {})
                            img = generate_image(client, scene['prompt'], ref_imgs if ref_imgs else None, img_model)
                            if img:
                                st.session_state.scenes[i]['generated_image'] = img
                                st.rerun()
            
            with col_img:
                if scene.get('generated_image'):
                    b64 = img_to_b64(scene['generated_image'])
                    st.markdown(f'<div class="img-container"><img src="data:image/png;base64,{b64}" style="width:100%;border-radius:6px;"></div>', unsafe_allow_html=True)
                    
                    dc1, dc2 = st.columns(2)
                    with dc1:
                        st.download_button("⬇️ Download", data=scene['generated_image'], file_name=f"scene_{i+1}.png", mime="image/png", key=f"dl_{i}")
                    with dc2:
                        if st.button("🎥 Grok", key=f"grok_{i}"):
                            with st.spinner("..."):
                                g = generate_grok_prompts(client, scene['prompt'], model)
                                st.session_state.scenes[i]['grok_video'] = g['video']
                                st.session_state.scenes[i]['grok_audio'] = g['audio']
                                st.rerun()
                    
                    # Grok prompts
                    if scene.get('grok_video'):
                        st.text_area("🎥 Video:", scene['grok_video'], height=50, key=f"gv_{i}")
                        st.text_area("🔊 Audio:", scene['grok_audio'], height=50, key=f"ga_{i}")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ Scenes"):
                st.session_state.step = 3
                st.rerun()
        with c2:
            if st.button("➡️ Export", type="primary"):
                st.session_state.step = 5
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 5: FINAL EXPORT
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 5:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🎥 Step 5: Final Export")
        
        st.markdown('<div class="success-box">✅ Export အဆင်သင့်! ပုံတွေ Download လုပ်ပြီး Grok မှာ video လုပ်ပါ။</div>', unsafe_allow_html=True)
        
        # Generate all Grok prompts if missing
        for i, scene in enumerate(st.session_state.scenes):
            if scene.get('generated_image') and not scene.get('grok_video'):
                g = generate_grok_prompts(client, scene.get('prompt', ''), model)
                st.session_state.scenes[i]['grok_video'] = g['video']
                st.session_state.scenes[i]['grok_audio'] = g['audio']
        
        for i, scene in enumerate(st.session_state.scenes):
            st.markdown(f'<div class="scene-card">', unsafe_allow_html=True)
            st.markdown(f"#### Scene {i+1}")
            
            c1, c2 = st.columns([1, 2])
            
            with c1:
                if scene.get('generated_image'):
                    b64 = img_to_b64(scene['generated_image'])
                    st.markdown(f'<img src="data:image/png;base64,{b64}" style="width:100%;border-radius:8px;">', unsafe_allow_html=True)
                    st.download_button("⬇️ Download", data=scene['generated_image'], file_name=f"final_{i+1}.png", mime="image/png", key=f"fdl_{i}")
                    
                    # Replace image option
                    st.markdown("**🔄 ပုံပြောင်းမယ်:**")
                    replace = st.file_uploader("ပုံအသစ်တင်", type=['png','jpg','jpeg'], key=f"replace_{i}", label_visibility="collapsed")
                    if replace:
                        st.session_state.scenes[i]['generated_image'] = replace.read()
                        st.rerun()
                else:
                    st.markdown('<div class="warn-box">ပုံမရှိပါ</div>', unsafe_allow_html=True)
            
            with c2:
                v_prompt = scene.get('grok_video', '')
                a_prompt = scene.get('grok_audio', '')
                
                st.text_area("🎥 Video Prompt:", v_prompt, height=60, key=f"ev_{i}")
                st.text_area("🔊 Audio Prompt:", a_prompt, height=60, key=f"ea_{i}")
                
                # Copy button (combines both prompts)
                combined = f"VIDEO PROMPT:\n{v_prompt}\n\nAUDIO PROMPT:\n{a_prompt}"
                
                # Use Streamlit's native copy functionality via code block
                if st.button(f"📋 Copy Prompts", key=f"copy_{i}"):
                    st.code(combined, language=None)
                    st.success("အပေါ်က text ကို select လုပ်ပြီး copy ယူပါ!")
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button("⬅️ ပြင်ဆင်မယ်"):
                st.session_state.step = 4
                st.rerun()
        with c2:
            if st.button("🔄 အစကနေပြန်စ"):
                for k in defaults:
                    st.session_state[k] = defaults[k] if not isinstance(defaults[k], (dict, list)) else type(defaults[k])()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
