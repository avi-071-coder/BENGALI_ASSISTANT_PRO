import os
import shutil
import sys
import re

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from pipeline.vision_ocr import extract_text
from pipeline.logic_fix import fix_and_translate
from pipeline.voice_gen import create_voice

def run_assistant():
    base_path = os.path.dirname(os.path.abspath(__file__))
    in_box = os.path.join(base_path, 'data', 'raw_scans')
    out_box = os.path.join(base_path, 'output', 'processed_images')
    os.makedirs(out_box, exist_ok=True)
    os.makedirs(in_box, exist_ok=True)

    files = [f for f in os.listdir(in_box) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    if not files:
        print("📭 Move your images back to 'raw_scans'!")
        return

    for img_name in files:
        path = os.path.join(in_box, img_name)
        
        # 1. OCR Detect
        raw_ben, confidence = extract_text(path)
        if not raw_ben:
            continue
        
        # 2. Logic Check
        fixed_ben, english_txt, confidence = fix_and_translate(raw_ben, img_name, confidence)
        
        print(f"\n--- Result: {img_name} ---")
        print(f"Bengali: {fixed_ben}")
        
        # For empty char detections, add a note
        if 'char' in img_name.lower() and not fixed_ben:
            print("Note: No character detected - image may be unclear")
        
        name = os.path.splitext(img_name)[0]
        audio_list = []
        
        # 3. Bengali Voice
        if fixed_ben and fixed_ben != "লেখা শনাক্ত করা যায়নি":
            voice_path = create_voice(fixed_ben, 'bn', f"{name}_ben.mp3")
            if voice_path:
                audio_list.append(f"{name}_ben.mp3")
        
        # 4. English Handling
        if english_txt:
            # Show "Confused word" only if text has non-Bengali chars (indicating gibberish)
            if re.search(r'[^ঀ-৿\s]', fixed_ben):  # Non-Bengali Unicode
                print(f"Confused word: {fixed_ben}")
            print(f"English: {english_txt}")
            if re.search(r'[a-zA-Z]', fixed_ben):
                print("Translation Note: May be inaccurate due to mixed languages")
            voice_path = create_voice(english_txt, 'en', f"{name}_en.mp3")
            if voice_path:
                audio_list.append(f"{name}_en.mp3")
        else:
            print("Mode: Single Character (Skipping English Translation/Voice)")
        
        if audio_list:
            print(f"Audio Generated: {' and '.join(audio_list)}")
        
        shutil.move(path, os.path.join(out_box, img_name))
        print("✅ Success.")

if __name__ == "__main__":
    run_assistant()