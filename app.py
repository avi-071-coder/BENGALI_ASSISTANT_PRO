import os
import io
import re
import json
import time
import base64
import requests
import numpy as np
import cv2
import pytesseract
from flask import Flask, request, jsonify, render_template, send_from_directory
from werkzeug.utils import secure_filename
from deep_translator import GoogleTranslator
from gtts import gTTS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()
_startup_key = os.getenv("GEMINI_API_KEY")
if _startup_key and _startup_key.strip() and _startup_key.strip() != "your_gemini_api_key_here":
    print(f"\n[★] SUCCESS: GEMINI_API_KEY detected (starts with: {_startup_key.strip()[:8]}...)\n")
else:
    print("\n[⚠️] WARNING: No GEMINI_API_KEY environment variable found in .env! Running in local Tesseract fallback mode.\n")

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB Limit

# Ensure Tesseract path is configured for Windows
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

def get_allowed_mime(filename):
    """Validate extensions to prevent malicious uploads."""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'webp'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def query_gemini_api(img_bytes, api_key):
    """Query Gemini API directly using HTTP POST requests for OCR & Translation."""
    models = ["gemini-2.5-flash", "gemini-1.5-flash"]
    headers = {"Content-Type": "application/json"}
    
    img_b64 = base64.b64encode(img_bytes).decode('utf-8')
    
    prompt = (
        "You are an expert Bengali OCR system. Analyze the provided image of handwritten or printed Bengali text. "
        "Extract the text and return a JSON object with the following structure:\n"
        "{\n"
        "  \"bengali\": \"the extracted Bengali text, written properly and corrected grammatically\",\n"
        "  \"english\": \"a natural English translation of that Bengali text\",\n"
        "  \"confidence\": an integer confidence score from 0 to 100 representing how sure you are of the transcription\n"
        "}\n"
        "Return ONLY the raw JSON string without any markdown formatting or surrounding code blocks."
    )
    
    payload = {
        "contents": [{
            "parts": [
                {"text": prompt},
                {
                    "inlineData": {
                        "mimeType": "image/jpeg",
                        "data": img_b64
                    }
                }
            ]
        }],
        "generationConfig": {
            "responseMimeType": "application/json"
        }
    }

    last_err = None
    for model in models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        # Retry logic with exponential backoff for each model
        max_retries = 2
        delay = 1.0
        for attempt in range(max_retries):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=12)
                if response.status_code == 200:
                    result = response.json()
                    
                    # Safe extraction of text response from Gemini schema
                    text_response = ""
                    if 'candidates' in result and result['candidates']:
                        cand = result['candidates'][0]
                        if 'content' in cand and 'parts' in cand['content'] and cand['content']['parts']:
                            text_response = cand['content']['parts'][0].get('text', '')
                    elif 'contents' in result and result['contents']:
                        cont = result['contents'][0]
                        if 'parts' in cont and cont['parts']:
                            text_response = cont['parts'][0].get('text', '')
                            
                    if not text_response:
                        raise ValueError("No text parts found in Gemini response payload")
                        
                    clean_json = re.sub(r'^```json\s*|```$', '', text_response.strip(), flags=re.MULTILINE)
                    data = json.loads(clean_json)
                    return {
                        "bengali": data.get("bengali", "").strip(),
                        "english": data.get("english", "").strip(),
                        "confidence": int(data.get("confidence", 85)),
                        "engine": "Neural Vision Engine"
                    }
                else:
                    last_err = f"HTTP {response.status_code}: {response.text}"
            except Exception as e:
                last_err = str(e)
                if attempt == max_retries - 1:
                    break
                time.sleep(delay)
                delay *= 2
                
    raise Exception(f"Failed to query Gemini API (last error: {last_err})")

def run_local_ocr(img):
    """Fallback local OCR using OpenCV and Tesseract."""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Preprocessing pipeline
    gray = cv2.GaussianBlur(gray, (3, 3), 0)
    gray = cv2.equalizeHist(gray)
    
    # High quality resize using Lanczos interpolation
    resized = cv2.resize(gray, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LANCZOS4)
    
    # OCR config
    config = '--oem 3 --psm 6'
    lang = 'ben'
    
    raw_text = pytesseract.image_to_string(resized, lang=lang, config=config).strip()
    
    # Clean OCR text (keep Bengali letters, spaces, and punctuation)
    cleaned_ben = re.sub(r'[^\u0980-\u09FF\s।\?]', '', raw_text)
    cleaned_ben = " ".join(cleaned_ben.split())
    
    if not cleaned_ben:
        return {
            "bengali": "লেখা শনাক্ত করা যায়নি",
            "english": "Could not identify any Bengali text.",
            "confidence": 0,
            "engine": "Local Tesseract OCR (No text detected)"
        }
    
    # Calculate confidence from Tesseract word details
    try:
        data = pytesseract.image_to_data(resized, lang=lang, config=config, output_type=pytesseract.Output.DICT)
        conf_list = [int(c) for c in data['conf'] if c != '-1']
        avg_conf = int(np.mean(conf_list)) if conf_list else 50
    except:
        avg_conf = 60  # Default fallback confidence
        
    # Translate
    try:
        translator = GoogleTranslator(source='bn', target='en')
        translation = translator.translate(cleaned_ben)
    except Exception as e:
        translation = f"Translation error: {str(e)}"
        
    return {
        "bengali": cleaned_ben,
        "english": translation,
        "confidence": avg_conf,
        "engine": "Local OCR Engine"
    }

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    # File check
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
        
    if not get_allowed_mime(file.filename):
        return jsonify({'error': 'Unsupported file format'}), 400
        
    # Check for backend API key in environment
    api_key = os.getenv("GEMINI_API_KEY")
    
    try:
        # Read file entirely in-memory
        img_bytes = file.read()
        nparr = np.frombuffer(img_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            return jsonify({'error': 'Failed to decode image data'}), 400
            
        # Select Engine: Gemini or local fallback
        if api_key and api_key.strip() and api_key.strip() != "your_gemini_api_key_here":
            try:
                results = query_gemini_api(img_bytes, api_key.strip())
                return jsonify(results)
            except Exception as gemini_err:
                # Log backend failure details
                app.logger.warning(f"Inference API failed: {gemini_err}. Falling back to local OCR.")
                results = run_local_ocr(img)
                results['warning'] = "Inference connection offline. Running in CPU local mode (decreased accuracy for handwritten inputs)."
                return jsonify(results)
        else:
            # No API key configured, use local OCR
            results = run_local_ocr(img)
            results['warning'] = "Running in CPU local mode (decreased accuracy for handwritten inputs)."
            return jsonify(results)
            
    except Exception as e:
        return jsonify({'error': f"Internal server error during processing: {str(e)}"}), 500

@app.route('/synthesize', methods=['POST'])
def synthesize():
    """Generates audio for a given string in-memory and returns base64 string."""
    data = request.get_json()
    if not data or 'text' not in data or 'lang' not in data:
        return jsonify({'error': 'Invalid request parameters'}), 400
        
    text = data['text'].strip()
    lang = data['lang'].strip()
    
    if not text or "শনাক্ত করা যায়নি" in text or "Could not identify" in text:
        return jsonify({'error': 'No speakable text provided'}), 400
        
    if lang not in ['bn', 'en']:
        return jsonify({'error': 'Unsupported language code'}), 400
        
    try:
        # Generate synthesis directly to memory stream
        fp = io.BytesIO()
        tts = gTTS(text=text, lang=lang, slow=False)
        tts.write_to_fp(fp)
        fp.seek(0)
        
        audio_b64 = base64.b64encode(fp.read()).decode('utf-8')
        audio_uri = f"data:audio/mp3;base64,{audio_b64}"
        
        return jsonify({'audio_url': audio_uri})
    except Exception as e:
        return jsonify({'error': f"Audio synthesis failed: {str(e)}"}), 500

@app.route('/<path:path>')
def catch_all_prompts(path):
    import urllib.parse
    decoded_path = urllib.parse.unquote(path)
    if "VIDEO PROMPT: A dramatic" in decoded_path or "black ink slowly bleeding" in decoded_path:
        return send_from_directory('static', 'hero_bg.png')
    elif "VIDEO PROMPT: Minimalist" in decoded_path or "metallic silk ripples" in decoded_path:
        return send_from_directory('static', 'app_bg.png')
    elif "IMAGE PROMPT: High-end" in decoded_path or "smartphone interface showing" in decoded_path:
        return send_from_directory('static', 'feature_flow.png')
    elif "IMAGE PROMPT: Abstract luxury" in decoded_path or "finely milled dark titanium" in decoded_path:
        return send_from_directory('static', 'confidence_texture.png')
    return "Not Found", 404

if __name__ == '__main__':
    # Run securely on localhost
    app.run(debug=True, host='127.0.0.1', port=5000)
