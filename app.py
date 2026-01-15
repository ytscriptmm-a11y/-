import streamlit as st
from google import genai
from google.genai import types
import base64
import io
import time
import json
import re
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

# Modern Dark Theme CSS with Mobile Responsiveness
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+Myanmar:wght@400;500;600&display=swap');
    
    /* ═══ GLOBAL STYLES ═══ */
    .stApp {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Outfit', 'Noto Sans Myanmar', sans-serif;
    }
    
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
        gap: 0.4rem;
        margin: 1.5rem 0;
        flex-wrap: wrap;
    }
    
    .step-item {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        padding: 0.4rem 0.8rem;
        border-radius: 50px;
        font-size: 0.75rem;
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
    
    .character-card {
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.1), rgba(118, 75, 162, 0.05));
        border: 2px dashed rgba(102, 126, 234, 0.3);
        border-radius: 16px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .character-card:hover {
        border-color: rgba(102, 126, 234, 0.6);
        background: linear-gradient(145deg, rgba(102, 126, 234, 0.15), rgba(118, 75, 162, 0.1));
    }
    
    .character-card.uploaded {
        border-style: solid;
        border-color: rgba(72, 187, 120, 0.5);
        background: linear-gradient(145deg, rgba(72, 187, 120, 0.1), rgba(72, 187, 120, 0.05));
    }
    
    .character-name {
        font-size: 1rem;
        font-weight: 600;
        color: #e2e8f0;
        margin-bottom: 0.5rem;
    }
    
    .character-desc {
        font-size: 0.8rem;
        color: #a0aec0;
        margin-bottom: 1rem;
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
    
    /* ═══ FILE UPLOADER ═══ */
    .stFileUploader > div {
        background: rgba(255, 255, 255, 0.03) !important;
        border: 2px dashed rgba(102, 126, 234, 0.3) !important;
        border-radius: 12px !important;
    }
    
    .stFileUploader > div:hover {
        border-color: rgba(102, 126, 234, 0.6) !important;
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
    
    .warning-alert {
        background: linear-gradient(135deg, rgba(236, 201, 75, 0.1), rgba(236, 201, 75, 0.05));
        border: 1px solid rgba(236, 201, 75, 0.3);
        border-radius: 12px;
        padding: 1rem;
        color: #ecc94b;
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
    
    .character-preview {
        width: 120px;
        height: 120px;
        border-radius: 12px;
        object-fit: cover;
        border: 2px solid rgba(72, 187, 120, 0.5);
        margin: 0.5rem auto;
        display: block;
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
            padding: 0.3rem 0.6rem;
            font-size: 0.7rem;
        }
        
        .character-card {
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
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    /* ═══ CUSTOM DIVIDER ═══ */
    .custom-divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        margin: 1.5rem 0;
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
if 'characters' not in st.session_state:
    st.session_state.characters = []  # List of {name, description, image_data}
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
    """Step 1: Generate Silent Movie Script"""
    try:
        prompt = f"""
You are a Video Scriptwriter for a viral 'Silent Cat Meme Movie'.
Topic: '{topic}'

KEY CHARACTER SETTING: 
The characters are ANTHROPOMORPHIC CATS. 
- They stand upright on two legs like humans.
- They wear human clothes (hoodies, backpacks, shirts, pants).
- They use their front paws like human hands.
- They live in a human-like world and do human activities.
- Expressions are exaggerated and cute, like internet meme cats.

Rules for the Script:
1. NO Dialogue. NO Narration/Voiceover. This is a SILENT movie.
2. Focus ONLY on Visual Actions (body language, facial expressions, interactions).
3. Language: Write ALL descriptions in Burmese (Myanmar language).
4. Length: Create enough scenes for a 1-3 minute video.
5. Characters: Give each character a clear NAME and distinct personality/appearance.

IMPORTANT: Be clear about which characters appear in each scene.

Output Format: 
Write the visual story in Burmese paragraphs. Include character names when they appear.
"""
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        return response.text
    except Exception as e:
        st.error(f"Script Generation Error: {e}")
        return None


def extract_characters(client, script_text: str, model_name: str) -> list:
    """Step 2: Extract characters from the script"""
    try:
        prompt = f"""
Analyze this Burmese script and extract ALL characters that appear in the story.

Script:
"{script_text}"

For each character, provide:
1. name: The character's name (in Burmese or English as used in the script)
2. description: A brief description of the character's appearance and role (in Burmese)
3. appearance_traits: Key visual traits for image generation (in English)

Output ONLY valid JSON array format like this:
[
  {{
    "name": "ကြောင်ပျင်းလေး",
    "description": "ဆင်းရဲသော ကြောင်လေး၊ ဝမ်းနည်းနေတယ်",
    "appearance_traits": "sad looking cat, wearing worn clothes, droopy ears"
  }},
  {{
    "name": "သူငယ်ချင်းကြောင်",
    "description": "ပျော်ရွှင်သော ကြောင်လေး၊ အကူအညီပေးတယ်",
    "appearance_traits": "happy cheerful cat, colorful clothes, bright eyes"
  }}
]

If there is only ONE main character, still return it as an array with one item.
Return ONLY the JSON array, no other text.
"""
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )
        
        # Parse JSON from response
        response_text = response.text.strip()
        
        # Clean up response - remove markdown code blocks if present
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]
        
        response_text = response_text.strip()
        
        try:
            characters = json.loads(response_text)
            # Add image_data field to each character
            for char in characters:
                char['image_data'] = None
            return characters
        except json.JSONDecodeError:
            # Fallback: try to extract with regex
            st.warning("JSON parsing failed, using fallback method...")
            return [{
                "name": "Main Character",
                "description": "ဇာတ်လမ်းထဲက အဓိကဇာတ်ကောင်",
                "appearance_traits": "anthropomorphic cat character",
                "image_data": None
            }]
            
    except Exception as e:
        st.error(f"Character Extraction Error: {e}")
        return []


def generate_scene_breakdown(client, script_text: str, characters: list, model_name: str, scene_count: int) -> str:
    """Step 3: Breakdown into scenes with character references"""
    
    # Create character reference string
    char_info = "\n".join([
        f"- {c['name']}: {c['description']} ({c['appearance_traits']})"
        for c in characters
    ])
    
    try:
        prompt = f"""
Visual Script (in Burmese): 
"{script_text}"

CHARACTERS IN THIS STORY:
{char_info}

TASK:
Split this script into exactly {scene_count} distinct scenes for image generation.

For EACH scene, provide:
1. **Burmese**: A short visual action description in Burmese (1-2 sentences)
2. **Characters**: List which characters appear in this scene (comma-separated names)
3. **English_Prompt**: A detailed image generation prompt in English

CRITICAL REQUIREMENTS for English_Prompt:
- Describe the ACTION and EMOTION, NOT the character's appearance (we have reference images)
- Include: setting/background, lighting, mood
- Include: specific pose and action
- Include: "maintain exact character appearance from reference image"
- Style: "cute 3D Pixar-style animation, soft lighting, internet meme style"
- DO NOT describe the character's physical features - just reference them by role

OUTPUT FORMAT (repeat for each scene):
Burmese: [Burmese action text here]
Characters: [Character names appearing in this scene]
English_Prompt: [Action-focused prompt that references the character]
###

Example:
Burmese: ကြောင်လေးက မိုးရွာနေတဲ့အထဲ ဝမ်းနည်းစွာ လမ်းလျှောက်နေတယ်။
Characters: ကြောင်ပျင်းလေး
English_Prompt: The character from the reference image walking sadly in heavy rain, hunched posture, looking down at puddles, wet fur, rainy city street background with neon lights reflecting on wet pavement, dramatic lighting, emotional atmosphere, maintain exact character appearance from reference image, cute 3D Pixar-style animation, cinematic composition
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


def generate_image_with_reference(client, prompt: str, reference_images: list, model_name: str = "gemini-2.5-flash-image"):
    """Generate image using reference images for character consistency"""
    
    try:
        # Build content with reference images
        contents = []
        
        # Add reference images first
        if reference_images:
            ref_intro = "Here are reference images of the character(s). Generate a new image maintaining their exact appearance:\n\n"
            contents.append(ref_intro)
            
            for i, img_data in enumerate(reference_images):
                if img_data:
                    # Convert to PIL Image if needed
                    if isinstance(img_data, bytes):
                        img = Image.open(io.BytesIO(img_data))
                    else:
                        img = img_data
                    contents.append(img)
                    contents.append(f"\n[Reference Image {i+1}]\n")
        
        # Add the generation prompt
        full_prompt = f"""
Based on the reference image(s) above, generate a new image:

{prompt}

CRITICAL: The character MUST look exactly like the reference image(s) - same face, same body type, same fur color/pattern. Only change the pose, action, clothing details as needed, and background as specified in the prompt.

Style: cute 3D Pixar-style animation, soft lighting, detailed fur texture, expressive face, internet meme style, masterpiece quality
"""
        contents.append(full_prompt)
        
        response = client.models.generate_content(
            model=model_name,
            contents=contents,
            config=types.GenerateContentConfig(
                response_modalities=['IMAGE', 'TEXT']
            )
        )
        
        # Extract image from response
        for part in response.candidates[0].content.parts:
            if hasattr(part, 'inline_data') and part.inline_data is not None:
                return part.inline_data.data
        
        return None
        
    except Exception as e:
        st.warning(f"Image generation error: {e}")
        
        # Fallback: try without reference (text-only prompt)
        try:
            fallback_prompt = f"Generate an image: {prompt}, cute 3D Pixar-style animation, anthropomorphic cat character"
            response = client.models.generate_content(
                model="gemini-2.5-flash-image",
                contents=[fallback_prompt],
                config=types.GenerateContentConfig(
                    response_modalities=['IMAGE', 'TEXT']
                )
            )
            
            for part in response.candidates[0].content.parts:
                if hasattr(part, 'inline_data') and part.inline_data is not None:
                    return part.inline_data.data
            return None
        except Exception as e2:
            st.error(f"Fallback also failed: {e2}")
            return None


def generate_grok_prompts(client, scene_prompt: str, model_name: str) -> dict:
    """Generate Video & Audio Prompts for Grok AI"""
    try:
        prompt = f"""
Based on this scene description: "{scene_prompt}"

Generate prompts for video and audio:

1. VIDEO_PROMPT: Describe motion, camera movement, animation (3-5 seconds)
2. AUDIO_PROMPT: Describe background music and sound effects (no dialogue)

OUTPUT FORMAT:
VIDEO_PROMPT: [motion description]
AUDIO_PROMPT: [sound/music description]
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


def parse_scenes_with_characters(raw_text: str) -> list:
    """Parse scene breakdown text into structured data with character info"""
    scenes = []
    blocks = raw_text.split('###')
    
    for block in blocks:
        if "Burmese:" in block:
            scene = {
                "text": "",
                "characters": [],
                "prompt": "",
                "image_data": None
            }
            
            lines = block.strip().split('\n')
            current_field = None
            
            for line in lines:
                line = line.strip()
                if line.startswith("Burmese:"):
                    current_field = "text"
                    scene["text"] = line.replace("Burmese:", "").strip()
                elif line.startswith("Characters:"):
                    current_field = "characters"
                    chars = line.replace("Characters:", "").strip()
                    scene["characters"] = [c.strip() for c in chars.split(",") if c.strip()]
                elif line.startswith("English_Prompt:"):
                    current_field = "prompt"
                    scene["prompt"] = line.replace("English_Prompt:", "").strip()
                elif current_field == "prompt" and line:
                    scene["prompt"] += " " + line
            
            if scene["text"] or scene["prompt"]:
                scenes.append(scene)
    
    return scenes


def image_to_base64(image_data):
    """Convert image bytes to base64 string"""
    if image_data:
        if isinstance(image_data, bytes):
            return base64.b64encode(image_data).decode('utf-8')
        else:
            # PIL Image
            buffer = io.BytesIO()
            image_data.save(buffer, format='PNG')
            return base64.b64encode(buffer.getvalue()).decode('utf-8')
    return None


def get_character_images_for_scene(scene_characters: list, all_characters: list) -> list:
    """Get reference images for characters appearing in a scene"""
    images = []
    for char_name in scene_characters:
        for char in all_characters:
            if char['name'] == char_name and char.get('image_data'):
                images.append(char['image_data'])
                break
    return images


# ═══════════════════════════════════════════════════════════════════
# 🎨 UI COMPONENTS
# ═══════════════════════════════════════════════════════════════════

def render_header():
    """Render the main header"""
    st.markdown('<h1 class="main-header">🐱 Silent Cat Movie Maker</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Character Consistency နဲ့ Silent Movie Script & Image Generator</p>', unsafe_allow_html=True)


def render_step_indicator(current_step: int):
    """Render the step progress indicator"""
    steps = [
        ("📝", "Script"),
        ("👤", "Characters"),
        ("🎬", "Scenes"),
        ("🖼️", "Images"),
        ("🎥", "Export")
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
            index=0
        )
        
        image_model_options = [
            "gemini-2.5-flash-image",
            "gemini-2.0-flash-exp",
        ]
        selected_image_model = st.selectbox(
            "Image Model:",
            image_model_options,
            index=0
        )
        
        num_scenes = st.slider(
            "Scene အရေအတွက်:",
            min_value=4,
            max_value=15,
            value=8
        )
        
        st.markdown("---")
        st.markdown("""
        <div class="info-alert">
        <strong>💡 Workflow</strong><br>
        1. Script ရေးမယ်<br>
        2. Characters ခွဲထုတ်မယ်<br>
        3. Character ပုံတွေ Upload<br>
        4. Scene ပုံတွေထုတ်မယ်<br>
        5. Grok Prompts Export
        </div>
        """, unsafe_allow_html=True)
        
        return selected_model, selected_image_model, num_scenes


# ═══════════════════════════════════════════════════════════════════
# 🚀 MAIN APPLICATION
# ═══════════════════════════════════════════════════════════════════

def main():
    render_header()
    selected_model, selected_image_model, num_scenes = render_settings_sidebar()
    
    client = configure_api()
    
    if not client:
        st.markdown("""
        <div class="glass-card" style="text-align: center;">
            <h3>🔑 API Key လိုအပ်ပါတယ်</h3>
            <p style="color: #a0aec0;">Streamlit Secrets မှာ GEMINI_API_KEY ထည့်ပေးပါ</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    render_step_indicator(st.session_state.step)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 1: SCRIPT GENERATION
    # ═══════════════════════════════════════════════════════════════
    if st.session_state.step == 1:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 📝 Step 1: Visual Script ရေးမယ်")
        
        topic = st.text_input(
            "Story Topic:",
            value="ကျောပိုးအိတ်လွယ်ပြီး မိုးထဲ ငိုရင်းလမ်းလျှောက်နေတဲ့ ကြောင်လေး၊ သူငယ်ချင်းကြောင်တကောင်က ထီးလာဖြင့်ပေးတယ်",
            placeholder="ဇာတ်လမ်း topic ရိုက်ထည့်ပါ..."
        )
        
        if st.button("✨ Script ထုတ်မယ်", use_container_width=True):
            with st.spinner("Script ရေးနေပါတယ်... 🐱"):
                result = generate_visual_script(client, topic, selected_model)
                if result:
                    st.session_state.burmese_story = result
                    st.rerun()
        
        if st.session_state.burmese_story:
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            st.markdown("#### 📄 Generated Script")
            st.session_state.burmese_story = st.text_area(
                "Script:",
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
                if st.button("➡️ Characters ခွဲထုတ်မယ်", use_container_width=True, type="primary"):
                    st.session_state.step = 2
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 2: CHARACTER EXTRACTION & UPLOAD
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 2:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 👤 Step 2: Characters ပုံတွေ Upload လုပ်ပါ")
        
        # Extract characters if not done
        if not st.session_state.characters:
            with st.spinner("Script ထဲက Characters တွေ ခွဲထုတ်နေပါတယ်..."):
                characters = extract_characters(client, st.session_state.burmese_story, selected_model)
                if characters:
                    st.session_state.characters = characters
                    st.rerun()
        
        if st.session_state.characters:
            st.markdown("""
            <div class="info-alert">
                <strong>📌 လိုအပ်ချက်</strong><br>
                Scene တိုင်းမှာ Character ပုံတူညီဖို့ Reference ပုံတွေ Upload လုပ်ပေးပါ။<br>
                ပုံတွေက Anthropomorphic Cat (လူလိုရပ်နေတဲ့ကြောင်) ပုံဖြစ်ရပါမယ်။
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"*ဇာတ်လမ်းထဲမှာ Character {len(st.session_state.characters)} ခု တွေ့ပါတယ်*")
            
            # Display character upload cards
            cols = st.columns(min(len(st.session_state.characters), 3))
            
            all_uploaded = True
            
            for i, char in enumerate(st.session_state.characters):
                col_idx = i % len(cols)
                with cols[col_idx]:
                    uploaded = char.get('image_data') is not None
                    card_class = "character-card uploaded" if uploaded else "character-card"
                    
                    st.markdown(f"""
                    <div class="{card_class}">
                        <div class="character-name">🐱 {char['name']}</div>
                        <div class="character-desc">{char['description']}</div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Show uploaded image or upload button
                    if uploaded:
                        b64_img = image_to_base64(char['image_data'])
                        st.markdown(f"""
                        <img src="data:image/png;base64,{b64_img}" class="character-preview">
                        """, unsafe_allow_html=True)
                        if st.button(f"🔄 ပြောင်းမယ်", key=f"change_{i}"):
                            st.session_state.characters[i]['image_data'] = None
                            st.rerun()
                    else:
                        all_uploaded = False
                        uploaded_file = st.file_uploader(
                            f"ပုံတင်ပါ",
                            type=['png', 'jpg', 'jpeg', 'webp'],
                            key=f"upload_{i}",
                            label_visibility="collapsed"
                        )
                        if uploaded_file:
                            image_data = uploaded_file.read()
                            st.session_state.characters[i]['image_data'] = image_data
                            st.rerun()
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
            
            # Upload status
            uploaded_count = sum(1 for c in st.session_state.characters if c.get('image_data'))
            total_count = len(st.session_state.characters)
            
            if uploaded_count < total_count:
                st.markdown(f"""
                <div class="warning-alert">
                    ⚠️ {uploaded_count}/{total_count} Characters Upload ပြီးပါပြီ။ အားလုံး Upload မှ ရှေ့ဆက်နိုင်ပါမယ်။
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="success-alert">
                    ✅ Characters အားလုံး Upload ပြီးပါပြီ!
                </div>
                """, unsafe_allow_html=True)
            
            # Navigation
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Script ပြင်မယ်", use_container_width=True):
                    st.session_state.step = 1
                    st.session_state.characters = []
                    st.rerun()
            with col2:
                if st.button("➡️ Scene ခွဲမယ်", use_container_width=True, type="primary", disabled=not all_uploaded):
                    st.session_state.step = 3
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 3: SCENE BREAKDOWN
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 3:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 🎬 Step 3: Scene ခွဲခြင်း")
        
        if not st.session_state.scenes_data:
            with st.spinner(f"Scene {num_scenes} ခု ခွဲနေပါတယ်..."):
                raw_result = generate_scene_breakdown(
                    client,
                    st.session_state.burmese_story,
                    st.session_state.characters,
                    selected_model,
                    num_scenes
                )
                if raw_result:
                    scenes = parse_scenes_with_characters(raw_result)
                    st.session_state.scenes_data = scenes
                    st.rerun()
        
        if st.session_state.scenes_data:
            st.markdown(f"*Scene {len(st.session_state.scenes_data)} ခု ရပါတယ်*")
            
            # Show character reference summary
            st.markdown("""
            <div class="info-alert">
                <strong>📌 Reference Characters</strong><br>
                Scene တိုင်းမှာ Upload ထားတဲ့ Character ပုံတွေကို Reference အဖြစ် သုံးပြီး ပုံထုတ်ပါမယ်။
            </div>
            """, unsafe_allow_html=True)
            
            for i, scene in enumerate(st.session_state.scenes_data):
                with st.expander(f"🎬 Scene {i + 1} - {', '.join(scene.get('characters', ['Unknown']))}"):
                    st.markdown(f"**Action:** *{scene['text']}*")
                    st.markdown(f"**Characters:** {', '.join(scene.get('characters', []))}")
                    
                    st.session_state.scenes_data[i]['prompt'] = st.text_area(
                        "Image Prompt:",
                        value=scene['prompt'],
                        height=150,
                        key=f"scene_prompt_{i}"
                    )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("⬅️ Characters ပြင်မယ်", use_container_width=True):
                    st.session_state.step = 2
                    st.session_state.scenes_data = []
                    st.rerun()
            with col2:
                if st.button("➡️ ပုံတွေထုတ်မယ်", use_container_width=True, type="primary"):
                    st.session_state.step = 4
                    st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 4: IMAGE GENERATION WITH REFERENCE
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 4:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 🖼️ Step 4: ပုံထုတ်ခြင်း (Reference နဲ့)")
        
        st.markdown("""
        <div class="info-alert">
            <strong>🎯 Character Consistency</strong><br>
            Upload ထားတဲ့ Character ပုံတွေကို Reference အဖြစ်သုံးပြီး Scene ပုံတွေထုတ်ပါမယ်။
        </div>
        """, unsafe_allow_html=True)
        
        # Generate all images button
        if st.button("🖼️ ပုံအားလုံး ထုတ်မယ်", use_container_width=True):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            for i, scene in enumerate(st.session_state.scenes_data):
                status_text.text(f"Scene {i + 1}/{len(st.session_state.scenes_data)} ထုတ်နေပါတယ်...")
                
                # Get reference images for characters in this scene
                ref_images = get_character_images_for_scene(
                    scene.get('characters', []),
                    st.session_state.characters
                )
                
                # If no specific characters, use all character images
                if not ref_images:
                    ref_images = [c['image_data'] for c in st.session_state.characters if c.get('image_data')]
                
                image_data = generate_image_with_reference(
                    client,
                    scene['prompt'],
                    ref_images,
                    selected_image_model
                )
                
                if image_data:
                    st.session_state.scenes_data[i]['image_data'] = image_data
                
                progress_bar.progress((i + 1) / len(st.session_state.scenes_data))
                time.sleep(1.5)  # Rate limiting
            
            status_text.text("✅ ပုံအားလုံး ထုတ်ပြီးပါပြီ!")
            st.rerun()
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Display scenes with images
        for i, scene in enumerate(st.session_state.scenes_data):
            st.markdown(f"""
            <div class="scene-card">
                <div class="scene-number">{i + 1}</div>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.markdown(f"**Action:** *{scene['text']}*")
                st.markdown(f"**Characters:** {', '.join(scene.get('characters', []))}")
                
                # Single scene generate button
                if st.button(f"🖼️ ပုံထုတ်", key=f"gen_{i}", use_container_width=True):
                    with st.spinner("ထုတ်နေပါတယ်..."):
                        ref_images = get_character_images_for_scene(
                            scene.get('characters', []),
                            st.session_state.characters
                        )
                        if not ref_images:
                            ref_images = [c['image_data'] for c in st.session_state.characters if c.get('image_data')]
                        
                        image_data = generate_image_with_reference(
                            client,
                            scene['prompt'],
                            ref_images,
                            selected_image_model
                        )
                        if image_data:
                            st.session_state.scenes_data[i]['image_data'] = image_data
                            st.rerun()
            
            with col2:
                if scene.get('image_data'):
                    b64_img = image_to_base64(scene['image_data'])
                    st.markdown(f"""
                    <div class="image-container">
                        <img src="data:image/png;base64,{b64_img}" style="width: 100%; border-radius: 10px;">
                    </div>
                    """, unsafe_allow_html=True)
                    
                    st.download_button(
                        "⬇️ Download",
                        data=scene['image_data'],
                        file_name=f"scene_{i+1}.png",
                        mime="image/png",
                        key=f"dl_{i}",
                        use_container_width=True
                    )
                else:
                    st.markdown("""
                    <div style="background: rgba(255,255,255,0.05); border-radius: 12px; padding: 3rem; text-align: center; color: #718096;">
                        🖼️ ပုံမထုတ်ရသေးပါ
                    </div>
                    """, unsafe_allow_html=True)
        
        st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ Scene ပြင်မယ်", use_container_width=True):
                st.session_state.step = 3
                st.rerun()
        with col2:
            # Check if any images generated
            has_images = any(s.get('image_data') for s in st.session_state.scenes_data)
            if st.button("➡️ Export", use_container_width=True, type="primary", disabled=not has_images):
                st.session_state.step = 5
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # ═══════════════════════════════════════════════════════════════
    # STEP 5: FINAL EXPORT
    # ═══════════════════════════════════════════════════════════════
    elif st.session_state.step == 5:
        st.markdown('<div class="glass-card animate-in">', unsafe_allow_html=True)
        st.markdown("### 🎥 Step 5: Final Export")
        
        # Generate Grok prompts
        if not st.session_state.final_data:
            with st.spinner("Grok prompts ထုတ်နေပါတယ်..."):
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
        
        st.markdown("""
        <div class="success-alert">
            ✅ <strong>Export အဆင်သင့်!</strong> ပုံတွေ Download လုပ်ပြီး Grok AI မှာ video လုပ်နိုင်ပါပြီ။
        </div>
        """, unsafe_allow_html=True)
        
        for i, item in enumerate(st.session_state.final_data):
            st.markdown(f"#### Scene {i + 1}")
            
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
                        "⬇️ Download",
                        data=item['image_data'],
                        file_name=f"final_scene_{i+1}.png",
                        mime="image/png",
                        key=f"final_dl_{i}",
                        use_container_width=True
                    )
            
            with col2:
                st.text_area("🎥 Video Prompt", item.get('video_prompt', ''), height=80, key=f"vid_{i}")
                st.text_area("🔊 Audio Prompt", item.get('audio_prompt', ''), height=80, key=f"aud_{i}")
            
            st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
        
        # Navigation
        col1, col2 = st.columns(2)
        with col1:
            if st.button("⬅️ ပုံတွေပြင်မယ်", use_container_width=True):
                st.session_state.step = 4
                st.session_state.final_data = []
                st.rerun()
        with col2:
            if st.button("🔄 အစကနေပြန်စမယ်", use_container_width=True):
                st.session_state.clear()
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
# 🏃 RUN APPLICATION
# ═══════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    main()
