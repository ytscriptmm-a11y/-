import streamlit as st
from google import genai
from google.genai import types
import base64
import io
import time
from datetime import datetime

# ═══════════════════════════════════════════════════════════════════
# 🎨 PAGE CONFIG & CUSTOM CSS
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Silent Cat Movie Maker",
    page_icon="🐱",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern Dark Theme CSS with Mobile Responsiveness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Myanmar:wght@400;500;600&display=swap');
    
    /* ═══ GLOBAL STYLES ═══ */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Outfit', 'Noto Sans Myanmar', sans-serif;
    }
    
    /* Hide default elements */
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {
        padding: 1rem 1rem 3rem 1rem;
        max-width: 1200px;
    }
    
    /* ═══ HEADER STYLES ═══ */
    .main-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        font-size: clamp(1.8rem, 5vw, 3rem);
        font-weight: 700;
        text-align: center;
        margin-bottom: 0.3rem;
        letter-spacing: -0.02em;
    }
    
    .sub-header {
        color: #a0aec0;
        text-align: center;
        font-size: clamp(0.85rem, 2.5vw, 1rem);
        margin-bottom: 1.5rem;
        font-weight: 400;
    }
    
    /* ═══ STEP INDICATOR ═══ */
    .step-container {
        display: flex;
        justify-content: center;
        gap: 0.5rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-size: 0.85rem;
        font-weight: 500;
        transition: all 0.3s ease;
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
    
    /* ═══ CARD STYLES ═══ */
    .glass-card {
        background: rgba(255, 255, 255, 0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 1.5rem;
        margin: 1rem 0;
        transition: all 0.3s ease;
    }
    
    .glass-card:hover {
        border-color: rgba(102, 126, 234, 0.3);
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.1);
    }
    
    .scene-card {
        background: linear-gradient(145deg, rgba(26, 26, 46, 0.8), rgba(22, 33, 62, 0.6));
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.8rem 0;
    }
    
    .scene-number {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 600;
        font-size: 0.9rem;
        margin-bottom: 0.8rem;
    }
    
    /* ═══ BUTTON STYLES ═══ */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
    }
    
    /* Secondary button style */
    .secondary-btn > button {
        background: rgba(255, 255, 255, 0.08) !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    /* ═══ INPUT STYLES ═══ */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        color: #e2e8f0 !important;
        font-family: 'Outfit', 'Noto Sans Myanmar', sans-serif !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea > div > div > textarea:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* ═══ SLIDER STYLES ═══ */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2) !important;
    }
    
    /* ═══ EXPANDER STYLES ═══ */
    .streamlit-expanderHeader {
        background: rgba(255, 255, 255, 0.03) !important;
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
    }
    
    /* ═══ ALERT STYLES ═══ */
    .success-alert {
        background: linear-gradient(135deg, rgba(72, 187, 120, 0.1), rgba(72, 187, 120, 0.05));
        border: 1px solid rgba(72, 187, 120, 0.3);
        border-radius: 12px;
        padding: 1rem;
        color: #68d391;
        margin: 1rem 0;
    }
    
    .info-alert {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
        border: 1px solid rgba(102, 126, 234, 0.3);
        border-radius: 12px;
        padding: 1rem;
        color: #a0aec0;
        margin: 1rem 0;
    }
    
    /* ═══ IMAGE CONTAINER ═══ */
    .image-container {
        border-radius: 12px;
        overflow: hidden;
        border: 2px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .image-container:hover {
        border-color: rgba(102, 126, 234, 0.5);
    }
    
    /* ═══ MOBILE RESPONSIVE ═══ */
    @media (max-width: 768px) {
        .block-container {
            padding: 0.8rem 0.8rem 2rem 0.8rem;
        }
        
        .glass-card {
            padding: 1rem;
            border-radius: 16px;
        }
        
        .step-item {
            padding: 0.4rem 0.8rem;
            font-size: 0.75rem;
        }
        
        .scene-card {
            padding: 1rem;
        }
    }
    
    /* ═══ ANIMATION ═══ */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .animate-in {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* ═══ SCROLLBAR ═══ */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(102, 126, 234, 0.3);
        border-radius: 3px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(102, 126, 234, 0.5);
    }
    
    /* ═══ DIVIDER ═══ */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 1.5rem 0;
    }
    
    /* ═══ PROMPT BOX ═══ */
    .prompt-box {
        background: rgba(0, 0, 0, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        padding: 0.8rem;
        font-family: 'Monaco', 'Consolas', monospace;
        font-size: 0.8rem;
        color: #a0aec0;
        margin-top: 0.5rem;
    }
    
    /* Hide Streamlit branding */
    .viewerBadge_container__r5tak {display: none;}
</style>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# 🔧 SESSION STATE INITIALIZATION
# ═══════════════════════════════════════════════════════════════════
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'burmese_story' not in st.session_state:
    st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state:
    st.session_state.scenes_data = []
if 'final_data' not in st.session_state:
    st.session_state.final_data = []
if 'api_configured' not in st.session_state:
    st.session_state.api_configured = False

# ═══════════════════════════════════════════════════════════════════
# 🔑 API CONFIGURATION
# ═══════════════════════════════════════════════════════════════════
def configure_api():
    """Configure Gemini API with key from secrets or user input"""
    if "GEMINI_API_KEY" in st.secrets:
        api_key = st.secrets["GEMINI_API_KEY"]
    else:
        api_key = None
    
    if api_key:
        try:
            client = genai.Client(api_key=api_key)
            st.session_state.api_configured = True
            return client
        except Exception as e:
            st.error(f"API Configuration Error: {e}")
            return None
    return None

# ═══════════════════════════════════════════════════════════════════
# 🎬 CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════════

def generate_visual_script(client, topic: str, model_name: str) -> str:
    """Step 1: Generate Silent Movie Script (Anthropomorphic Style)"""
    try:
        prompt = f"""
You are a Video Scriptwriter for a viral 'Silent Cat Meme Movie'.
Topic: '{topic}'

KEY CHARACTER SETTING: 
The main character is an ANTHROPOMORPHIC CAT. 
- It stands upright on two legs like a human.
- It wears human clothes (hoodies, tiny backpacks, shirts, pants).
- It uses its front paws like human hands (holding phones, cups, bags).
- It lives in a human-like world and does human activities (cooking, working, traveling, shopping).
- Expressions are exaggerated and cute, like internet meme cats.

Rules for the Script:
1. NO Dialogue. NO Narration/Voiceover. This is a SILENT movie.
2. Focus ONLY on Visual Actions:
   - Body language and posture
   - Facial expressions (surprise, sadness, joy, confusion)
   - Physical interactions with objects and environment
   - Movement and gestures
3. Language: Write ALL visual action descriptions in Burmese (Myanmar language).
4. Length: Create enough scenes for a 1-3 minute video (approximately 8-12 key moments).
5. Style: Internet meme style - cute, relatable, slightly dramatic, emotional.

Output Format: 
Write the visual story flow in Burmese paragraphs. Describe what the cat does, how it moves, its expressions, and the setting. Make it emotional and engaging.
"""
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        st.error(f"Script Generation Error: {e}")
        return None


def generate_scene_breakdown(client, script_text: str, model_name: str, scene_count: int) -> str:
    """Step 2: Breakdown into Individual Scenes"""
    try:
        prompt = f"""
Visual Script (in Burmese): 
"{script_text}"

TASK:
Split this script into exactly {scene_count} distinct scenes for image generation.

For EACH scene, provide:
1. **Burmese**: A short visual action description in Burmese (1-2 sentences)
2. **English_Prompt**: A detailed image generation prompt in English

CRITICAL REQUIREMENTS for English_Prompt:
- MUST include: "anthropomorphic cat character, standing upright on two legs like a human"
- MUST include: clothing description (hoodie, backpack, shirt, etc.)
- MUST include: "cute 3D Pixar-style animation, soft lighting, detailed fur texture"
- MUST include: the specific action/pose
- MUST include: setting/background description
- MUST include: emotional expression (sad eyes, surprised face, happy smile, etc.)
- Style keywords: "internet meme style, adorable, expressive, high quality, masterpiece"

OUTPUT FORMAT (repeat for each scene):
Burmese: [Burmese action text here]
English_Prompt: [Detailed English prompt here]
###

Example:
Burmese: ကြောင်လေးက မိုးရွာနေတဲ့အထဲ ကျောပိုးအိတ်လွယ်ပြီး ဝမ်းနည်းစွာ လမ်းလျှောက်နေတယ်။
English_Prompt: An anthropomorphic cat character standing upright on two legs like a human, wearing a blue hoodie and small backpack, walking sadly in the rain, wet fur, droopy ears, tearful eyes, city street background with puddles, rainy atmosphere, cute 3D Pixar-style animation, soft lighting, detailed fur texture, internet meme style, adorable, expressive, high quality, masterpiece
###
"""
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        st.error(f"Scene Breakdown Error: {e}")
        return None


def generate_image(client, prompt: str, model_name: str = "gemini-2.5-flash-image"):
    """Generate image using Gemini's native image generation"""
    
    # Add style suffix to ensure consistent anthropomorphic cat style
    style_suffix = ", 3D animated character, anthropomorphic cute cat wearing clothes, standing upright on two legs, human-like poses, Pixar style render, expressive face, detailed fur, soft lighting, internet meme style, adorable, masterpiece quality"
    
    full_prompt = f"Generate an image: {prompt}{style_suffix}"
    
    try:
        response = client.models.generate_content(
            model=model_name,
            contents=[full_prompt],
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                image_data = part.inline_data.data
                return image_data
        
        return None
        
    except Exception as e:
        # Try fallback model
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[full_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT']
                )
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    return part.inline_data.data
            
            return None
        except Exception as e2:
            st.warning(f"Image generation failed: {e2}")
            return None


def generate_grok_prompts(client, image_prompt: str, model_name: str) -> dict:
    """Step 3: Generate Video & Audio Prompts for Grok AI"""
    try:
        prompt = f"""
Based on this scene description: "{image_prompt}"

I have generated a still image of this scene. Now I need to:
1. Turn it into a short video clip using Grok AI
2. Add appropriate sound/music

Generate specific prompts for both:

1. VIDEO_PROMPT: Describe the motion, camera movement, and animation.
   - What movement does the cat make?
   - Any camera effects (zoom, pan, tilt)?
   - Atmospheric effects (rain falling, wind, etc.)?
   - Keep it 3-5 seconds of motion.

2. AUDIO_PROMPT: Describe the sound design and music.
   - Background music mood (sad piano, upbeat, dramatic, etc.)
   - Sound effects (rain, footsteps, wind, etc.)
   - No dialogue - this is a silent film with music only.

OUTPUT FORMAT:
VIDEO_PROMPT: [Your video motion prompt here]
AUDIO_PROMPT: [Your audio/music prompt here]
"""
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        
        result = {"video": "", "audio": ""}
        for line in response.text.split('\n'):
            if "VIDEO_PROMPT:" in line:
                result["video"] = line.replace("VIDEO_PROMPT:", "").strip()
            if "AUDIO_PROMPT:" in line:
                result["audio"] = line.replace("AUDIO_PROMPT:", "").strip()
        
        return result
    except Exception as e:
        return {"video": f"Error: {e}", "audio": f"Error: {e}"}


def parse_scenes(raw_text: str) -> list:
    """Parse the scene breakdown text into structured data"""
    scenes = []
    blocks = raw_text.split('###')
    
    for block in blocks:
        if "Burmese:" in block and "English_Prompt:" in block:
            scene = {"text": "", "prompt": "", "image_data": None}
            
            lines = block.strip().split('\n')
            current_field = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("Burmese:"):
                    current_field = "text"
                    scene["text"] = line.replace("Burmese:", "").strip()
                elif line.startswith("English_Prompt:"):
                    current_field = "prompt"
                    scene["prompt"] = line.replace("English_Prompt:", "").strip()
                elif current_field == "prompt" and line:
                    scene["prompt"] += " " + line
            
            if scene["text"] or scene["prompt"]:
                scenes.append(scene)
    
    return scenes


def image_to_base64(image_data):
    """Convert image bytes to base64 string for display"""
    if image_data:
        return base64.b64encode(image_data).decode('utf-8')
    return None


# ═══════════════════════════════════════════════════════════════════
# 🎨 UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">🐱 Silent Cat Movie Maker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">လူလိုအဝတ်အစားဝတ်တဲ့ ကြောင်လေးတွေရဲ့ Silent Movie Script & Image Generator</p>', unsafe_allow_html=True)


def render_step_indicator(current_step: int):
    """Render the step progress indicator"""
    steps = [
        ("📝", "Script ရေးမယ်"),
        ("🎬", "Scene ခွဲမယ်"),
        ("🎥", "Export မယ်")
    ]
    
    step_html = '<div class="step-container">'
    for i, (icon, label) in enumerate(steps, 1):
        if i < current_step:
            css_class = "step-completed"
            status = "✓"
        elif i == current_step:
            css_class = "step-active"
            status = icon
        else:
            css_class = "step-pending"
            status = icon
        
        step_html += f'<div class="step-item {css_class}">{status} {label}</div>'
    step_html += '</div>'
    
    st.markdown(step_html, unsafe_allow_html=True)


def render_settings_sidebar():
    """Render settings in sidebar"""
    with st.sidebar:
        st.markdown("### ⚙️ Settings")
        
        model_options = [
            "gemini-2.5-flash",
            "gemini-2.0-flash",
            "gemini-1.5-flash",
            "gemini-1.5-pro",
        ]
        selected_model = st.selectbox(
            "Text Model:",
            model_options,
            index=0,
            help="Script နဲ့ Scene ခွဲဖို့ သုံးမယ့် model"
        )
        
        image_model_options = [
            "gemini-2.5-flash-image",
            "gemini-2.5-flash-preview-image",
        ]
        selected_image_model = st.selectbox(
            "Image Model:",
            image_model_options,
            index=0,
            help="ပုံထုတ်ဖို့ သုံးမယ့် model"
        )
        
        num_scenes = st.slider(
            "Scene အရေအတွက်:",
            min_value=4,
            max_value=15,
            value=8,
            help="Video အတွက် scene ဘယ်နှစ်ခု လိုချင်လဲ"
        )
        
        st.markdown("---")
        st.markdown("""
        <div class="info-alert">
        <strong>💡 အသုံးပြုနည်း</strong><br>
        1. Topic ရိုက်ထည့်ပါ<br>
        2. Script ထုတ်ပါ<br>
        3. Scene တွေခွဲပါ<br>
        4. ပုံတွေထုတ်ပါ<br>
        5. Grok AI မှာ video လုပ်ပါ
        </div>
        """, unsafe_allow_html=True)
        
        return selected_model, selected_image_model, num_scenes


# ═══════════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

def main():
    # Render header
    render_header()
    
    # Get settings from sidebar
    selected_model, selected_image_model, num_scenes = render_settings_sidebar()
    
    # Configure API
    client = configure_api()
    
    if not client:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3>🔑 API Key လိုအပ်ပါတယ်</h3>
            <p style="color: #a0aec0;">Streamlit Secrets မှာ GEMINI_API_KEY ထည့်ပေးပါ</p>
            <code style="background: rgba(0,0,0,0.3); padding: 0.5rem 1rem; border-radius: 8px;">
            GEMINI_API_KEY = "your-api-key-here"
            </code>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    # Render step indicator
    render_step_indicator(st.session_state.step)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: SCRIPT GENERATION
    # ═══════════════════════════════════════════════════════════════
    if st.session_state.step == 1:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 📝 Visual Script ရေးမယ်")
        st.markdown("*ကြောင်လေးရဲ့ ဇာတ်လမ်း topic ကို ရိုက်ထည့်ပါ*")
        
        topic = st.text_input(
            "Story Topic:",
            value="ကျောပိုးအိတ်လွယ်ပြီး မိုးထဲ ငိုရင်းလမ်းလျှောက်နေတဲ့ ကြောင်လေး",
            placeholder="ဥပမာ - အလုပ်ပင်ပန်းပြီး အိမ်ပြန်လာတဲ့ ကြောင်လေး..."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            generate_btn = st.button("✨ Script ထုတ်မယ်", use_container_width=True)
        
        if generate_btn:
            with st.spinner("Script ရေးနေပါတယ်... 🐱"):
                result = generate_visual_script(client, topic, selected_model)
                if result:
                    st.session_state.burmese_story = result
                    st.rerun()
        
        if st.session_state.burmese_story:
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 📄 Generated Script")
            st.session_state.burmese_story = st.text_area(
                "Script ကို ပြင်ဆင်နိုင်ပါတယ်:",
                value=st.session_state.burmese_story,
                height=300,
                label_visibility="collapsed"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🔄 အသစ်ထုတ်မယ်", use_container_width=True):
                    st.session_state.burmese_story = ""
                    st.rerun()
            with col2:
                if st.button("➡️ နောက်တဆင့်", use_container_width=True, type="primary"):
                    st.session_state.step = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: SCENE BREAKDOWN & IMAGE GENERATION
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 2:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 🎬 Scene ခွဲခြင်း & ပုံထုတ်ခြင်း")
        
        # Generate scenes if not already done
        if not st.session_state.scenes_data:
            with st.spinner(f"Scene {num_scenes} ခု ခွဲနေပါတယ်... 🎬"):
                raw_result = generate_scene_breakdown(
                    client,
                    st.session_state.burmese_story,
                    selected_model,
                    num_scenes
                )
                if raw_result:
                    scenes = parse_scenes(raw_result)
                    st.session_state.scenes_data = scenes
                    st.rerun()
        
        # Display scenes
        if st.session_state.scenes_data:
            st.markdown(f"*Scene {len(st.session_state.scenes_data)} ခု ရပါတယ်*")
            
            for i, scene in enumerate(st.session_state.scenes_data):
                with st.expander(f"🎬 Scene {i + 1}", expanded=(i == 0)):
                    col1, col2 = st.columns([1, 1])
                    
                    with col1:
                        st.markdown(f"**Action:** *{scene['text']}*")
                        
                        # Image generation button
                        if st.button(f"🖼️ ပုံထုတ်မယ်", key=f"gen_img_{i}", use_container_width=True):
                            with st.spinner("ပုံထုတ်နေပါတယ်..."):
                                image_data = generate_image(
                                    client,
                                    scene['prompt'],
                                    selected_image_model
                                )
                                if image_data:
                                    st.session_state.scenes_data[i]['image_data'] = image_data
                                    st.rerun()
                        
                        # Display generated image
                        if scene.get('image_data'):
                            b64_img = image_to_base64(scene['image_data'])
                            st.markdown(f"""
                            <div class="image-container">
                                <img src="data:image/png;base64,{b64_img}" style="width: 100%; border-radius: 10px;">
                            </div>
                            """, unsafe_allow_html=True)
                            
                            # Download button
                            st.download_button(
                                "⬇️ Download",
                                data=scene['image_data'],
                                file_name=f"scene_{i+1}.png",
                                mime="image/png",
                                key=f"dl_{i}",
                                use_container_width=True
                            )
                    
                    with col2:
                        st.markdown("**Image Prompt:**")
                        st.session_state.scenes_data[i]['prompt'] = st.text_area(
                            "Prompt",
                            value=scene['prompt'],
                            height=200,
                            key=f"prompt_{i}",
                            label_visibility="collapsed"
                        )
            
            # Generate all images button
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            if st.button("🖼️ ပုံအားလုံး တစ်ခါတည်းထုတ်မယ်", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()
                
                for i, scene in enumerate(st.session_state.scenes_data):
                    if not scene.get('image_data'):
                        status_text.text(f"Scene {i + 1}/{len(st.session_state.scenes_data)} ထုတ်နေပါတယ်...")
                        image_data = generate_image(client, scene['prompt'], selected_image_model)
                        if image_data:
                            st.session_state.scenes_data[i]['image_data'] = image_data
                        time.sleep(1)  # Rate limiting
                    progress_bar.progress((i + 1) / len(st.session_state.scenes_data))
                
                status_text.text("✅ ပုံအားလုံး ထုတ်ပြီးပါပြီ!")
                st.rerun()
            
            # Navigation buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ နောက်ပြန်", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.scenes_data = []
                    st.rerun()
            with col2:
                if st.button("➡️ Final Export", use_container_width=True, type="primary"):
                    st.session_state.step = 3
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: FINAL EXPORT WITH GROK PROMPTS
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 3:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 🎥 Final Export - Grok AI Prompts")
        
        # Generate Grok prompts if not already done
        if not st.session_state.final_data:
            with st.spinner("Video & Audio prompts ထုတ်နေပါတယ်..."):
                finals = []
                for scene in st.session_state.scenes_data:
                    grok_prompts = generate_grok_prompts(client, scene['prompt'], selected_model)
                    finals.append({
                        **scene,
                        "video_prompt": grok_prompts.get("video", ""),
                        "audio_prompt": grok_prompts.get("audio", "")
                    })
                st.session_state.final_data = finals
                st.rerun()
        
        # Display final data
        st.markdown("""
        <div class="success-alert">
            ✅ <strong>Export အဆင်သင့်ဖြစ်ပါပြီ!</strong><br>
            ပုံတွေကို Download လုပ်ပြီး Grok AI မှာ video/audio prompts တွေနဲ့ video လုပ်နိုင်ပါပြီ။
        </div>
        """, unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state.final_data):
            st.markdown(f"""
            <div class="scene-card">
                <div class="scene-number">{i + 1}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                if item.get('image_data'):
                    b64_img = image_to_base64(item['image_data'])
                    st.markdown(f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{b64_img}" style="width: 100%; border-radius: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button(
                        "⬇️ ပုံ Download",
                        data=item['image_data'],
                        file_name=f"scene_{i+1}_final.png",
                        mime="image/png",
                        key=f"final_dl_{i}",
                        use_container_width=True
                    )
                else:
                    st.warning("⚠️ ပုံမထုတ်ရသေးပါ")
            
            with col2:
                st.markdown("**🎥 Video Motion Prompt (Grok):**")
                st.text_area(
                    "Video Prompt",
                    value=item.get('video_prompt', ''),
                    height=100,
                    key=f"vid_{i}",
                    label_visibility="collapsed"
                )
                
                st.markdown("**🔊 Audio/Music Prompt (Grok):**")
                st.text_area(
                    "Audio Prompt",
                    value=item.get('audio_prompt', ''),
                    height=100,
                    key=f"aud_{i}",
                    label_visibility="collapsed"
                )
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Scene ပြင်ဆင်မယ်", use_container_width=True):
                st.session_state.step = 2
                st.session_state.final_data = []
                st.rerun()
        with col2:
            if st.button("🔄 အစကနေ ပြန်စမယ်", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🏃 RUN APPLICATION
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
