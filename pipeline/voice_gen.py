from gtts import gTTS
import os

def create_voice(text, lang, filename):
    if not text or not text.strip() or "শনাক্ত করা যায়নি" in text:
        return None
    
    # Validate lang
    if lang not in ['bn', 'en']:
        lang = 'en'
    
    try:
        base_path = os.path.dirname(os.path.dirname(__file__))
        output_dir = os.path.join(base_path, 'output', 'audio')
        os.makedirs(output_dir, exist_ok=True)
        save_path = os.path.join(output_dir, filename)
        
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.save(save_path)
        return save_path
    except Exception as e:
        print(f"Voice error: {e}")  # Quiet debug for failures
        return None



