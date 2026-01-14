import streamlit as st
import google.generativeai as genai
import io

# 1. Page Configuration
st.set_page_config(page_title="Burmese Cat Story Pro", layout="wide")
st.title("🐱 Burmese Cat Story Creator (Multi-Model)")

# 2. API Key Setup
if "GEMINI_API_KEY" in st.secrets:
    api_key = st.secrets["GEMINI_API_KEY"]
else:
    api_key = st.sidebar.text_input("Gemini API Key", type="password")

# --- SIDEBAR: Model Selection ---
st.sidebar.header("⚙️ Model Settings")

# User's Custom Model List
text_model_options = [
    "gemini-1.5-flash",
    "gemini-1.5-pro",
    "gemini-2.0-flash-exp",
    "models/gemini-2.5-pro",
    "models/gemini-3-flash-preview",
    "models/gemini-3-pro-preview"
]

selected_model = st.sidebar.selectbox(
    "Story Generation Model:",
    text_model_options,
    index=0
)

st.sidebar.info(f"Using for Images: models/gemini-3-pro-image-preview")

# 3. Session State
if 'step' not in st.session_state: st.session_state.step = 1
if 'burmese_story' not in st.session_state: st.session_state.burmese_story = ""
if 'scenes_data' not in st.session_state: st.session_state.scenes_data = [] 
if 'final_data' not in st.session_state: st.session_state.final_data = []

# --- Functions ---

def generate_burmese_story(topic, model_name):
    """အဆင့် (၁) - ရွေးထားသော Model ဖြင့် ဇာတ်လမ်းရေးခြင်း"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        You are a Video Scriptwriter for a viral 'Silent Cat Movie'.
        Topic: '{topic}'

        Rules for the Script:
        1. NO Dialogue. NO Narration/Voiceover.
        2. Focus ONLY on Visual Actions: Describe the cat's body language, expressions, and interactions with the environment to tell the story.
        3. Language: Write the visual description in Burmese (So I can read and understand the flow).
        4. Length: Create enough visual scenes for a 3-minute video.
        5. Style: 'Show, Don't Tell'. (Instead of saying 'The cat was sad', write 'The cat lowered its ears and curled into a tight ball in the corner').

        Output: Just write the visual story flow in Burmese paragraphs.
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error with {model_name}: {e}")
        return None

def generate_initial_prompts(burmese_text, model_name):
    """အဆင့် (၂) - ပုံ Prompt ခွဲထုတ်ခြင်း"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Story: "{burmese_text}"
        Split this into 4 scenes. For each scene, write an English Image Prompt for a 3D Pixar-style cat.
        Output format:
        Burmese: [Text]
        English_Prompt: [Prompt]
        ###
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error: {e}")
        return None

def generate_preview_image(prompt):
    """Gemini 3 Pro Image Preview ဖြင့် ပုံထုတ်ခြင်း"""
    try:
        # User သတ်မှတ်ထားသော Image Model
        model = genai.GenerativeModel("models/gemini-3-pro-image-preview")
        result = model.generate_images(
            prompt=prompt + ", 3D render, cute cat, high quality, masterpiece",
            number_of_images=1,
        )
        return result.images[0]
    except Exception as e:
        st.warning(f"Image Preview Error (Model not available?): {e}")
        return None

def generate_final_3_prompts(image_prompt, model_name):
    """အဆင့် (၃) - 3 Prompts ခွဲထုတ်ခြင်း"""
    try:
        model = genai.GenerativeModel(model_name)
        prompt = f"""
        Based on: "{image_prompt}"
        Generate 3 prompts:
        IMAGE: Optimized for DALL-E 3
        VIDEO: Optimized for Luma
        MUSIC: Optimized for Suno
        """
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"



# --- Main Workflow ---

if not api_key:
    st.warning("Please enter Gemini API Key to start.")
    st.stop()

genai.configure(api_key=api_key)

# Progress Bar
steps = ["၁. ဇာတ်လမ်းရေး", "၂. ပုံ Prompt နှင့် အသံ", "၃. Final Output"]
current_progress = (st.session_state.step / 3)
st.progress(current_progress)
st.subheader(f"အဆင့် {st.session_state.step}: {steps[st.session_state.step-1]}")

# ----------------------------------------------------------------
# STEP 1: Story Generation (Burmese)
# ----------------------------------------------------------------
if st.session_state.step == 1:
    with st.form("step1_form"):
        topic = st.text_input("ဇာတ်လမ်းခေါင်းစဉ်", "ကျောပိုးအိတ်နဲ့ ခရီးသွားတဲ့ ကြောင်လေး")
        submitted = st.form_submit_button("ဇာတ်လမ်း ရေးသားရန်")
        
        if submitted:
            with st.spinner(f"{selected_model} ဖြင့် ဇာတ်လမ်းရေးနေပါသည်..."):
                story = generate_burmese_story(topic, selected_model)
                if story:
                    st.session_state.burmese_story = story
                    st.rerun()

    if st.session_state.burmese_story:
        edited_story = st.text_area("ဇာတ်လမ်း (မြန်မာ) - ပြင်ဆင်နိုင်သည်", st.session_state.burmese_story, height=200)
        st.session_state.burmese_story = edited_story
        
        if st.button("နောက်တစ်ဆင့်သွားမယ် >"):
            st.session_state.step = 2
            st.rerun()

# ----------------------------------------------------------------
# STEP 2: Generate Draft Prompts (No Audio)
# ----------------------------------------------------------------
elif st.session_state.step == 2:
    if not st.session_state.scenes_data:
        # Generate Raw Data
        with st.spinner(f"ဗီဒီယို Script ကို Scene {num_scenes_input} ခုခွဲ၍ Prompt များထုတ်နေပါသည်..."):
            raw_data = generate_initial_prompts(st.session_state.burmese_story, selected_model, num_scenes_input)
            if raw_data:
                scenes = raw_data.split('###')
                parsed_scenes = []
                for scene in scenes:
                    if "Burmese:" in scene:
                        lines = scene.strip().split('\n')
                        burmese_text = ""
                        eng_prompt = ""
                        for line in lines:
                            if "Burmese:" in line: burmese_text = line.replace("Burmese:", "").strip()
                            if "English_Prompt:" in line: eng_prompt = line.replace("English_Prompt:", "").strip()
                        
                        if burmese_text:
                            # Audio generation removed
                            parsed_scenes.append({"text": burmese_text, "prompt": eng_prompt, "preview_img": None})
                st.session_state.scenes_data = parsed_scenes
                st.rerun()

    st.info("Visual Script နှင့် Prompt များကို စစ်ဆေးပြင်ဆင်ပါ။")

    for i, scene in enumerate(st.session_state.scenes_data):
        with st.expander(f"Scene {i+1}", expanded=True):
            c1, c2 = st.columns([1, 2])
            with c1:
                st.markdown(f"**Action/Visual:**")
                st.write(f"_{scene['text']}_") # Just text, no audio player
                
                # Test Image Button
                if st.button(f"Generate Preview 🖼️", key=f"btn_img_{i}"):
                    with st.spinner("Generating..."):
                        img = generate_preview_image(scene['prompt'])
                        if img:
                            st.session_state.scenes_data[i]['preview_img'] = img
                            st.rerun()
                
                if scene['preview_img']:
                    st.image(scene['preview_img'], use_container_width=True)

            with c2:
                new_p = st.text_area(f"Visual Prompt", scene['prompt'], key=f"p_{i}", height=100)
                st.session_state.scenes_data[i]['prompt'] = new_p

    c1, c2 = st.columns(2)
    with c1:
        if st.button("< Back to Script"):
            st.session_state.step = 1
            st.session_state.scenes_data = [] 
            st.rerun()
    with c2:
        if st.button("Final Output ထုတ်မယ် >"):
            st.session_state.step = 3
            st.rerun()

# ----------------------------------------------------------------
# STEP 3: Final 3-Prompt Generation
# ----------------------------------------------------------------
elif st.session_state.step == 3:
    if not st.session_state.final_data:
        with st.spinner("Final Prompts (Image, Video, Music) များ ခွဲထုတ်နေပါသည်..."):
            final_results = []
            for scene in st.session_state.scenes_data:
                res = generate_final_3_prompts(scene['prompt'], selected_model)
                p_img, p_vid, p_mus = "", "", ""
                if res:
                    for line in res.split('\n'):
                        if "IMAGE:" in line: p_img = line.replace("IMAGE:", "").strip()
                        if "VIDEO:" in line: p_vid = line.replace("VIDEO:", "").strip()
                        if "MUSIC:" in line: p_mus = line.replace("MUSIC:", "").strip()
                final_results.append({**scene, "p_img": p_img, "p_vid": p_vid, "p_mus": p_mus})
            st.session_state.final_data = final_results
            st.rerun()

    for i, item in enumerate(st.session_state.final_data):
        st.divider()
        st.subheader(f"Scene {i+1}")
        
        c_left, c_right = st.columns([1,2])
        with c_left:
             st.markdown("**Visual Action:**")
             st.info(item['text'])
             if item.get('preview_img'):
                 st.image(item['preview_img'], width=200)

        with c_right:
            st.text_area("Image Prompt (Midjourney/DALL-E)", item['p_img'], key=f"img_{i}")
            st.text_area("Video Prompt (Luma/Runway)", item['p_vid'], key=f"vid_{i}")
            st.text_area("Music Prompt (Suno)", item['p_mus'], key=f"mus_{i}")

    if st.button("Start Over"):
        st.session_state.clear()
        st.rerun()


