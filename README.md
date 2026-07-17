# BongLipi | Authentic Translation

BongLipi is a privacy-first, multimodal AI pipeline designed to decode cursive Bengali handwriting, translate its semantic meaning into English, and synthesize bilingual audio output. The platform operates entirely without persistent storage, ensuring the absolute privacy of user data.

---

## Core Architecture & Features

- **Neural Vision Decoding:** Utilizes the Google Gemini Multimodal API as the primary engine for analyzing and transcribing complex cursive Bengali script.
- **Local OCR Fallback:** Implements Tesseract OCR as a robust local fallback mechanism for environments lacking API connectivity.
- **Semantic Translation Pipeline:** Integrates with the `deep_translator` module to translate decoded Bengali into natural English, prioritizing semantic and cultural meaning over rigid word-to-word translation.
- **Bilingual Speech Synthesis (TTS):** Dynamically generates MP3 audio streams for both the transcribed Bengali text and the translated English output using `gTTS`.
- **Zero-Disk Volatile Processing:** The entire inference and synthesis pipeline operates exclusively in RAM using `io.BytesIO` buffers. Uploaded manuscripts and generated audio artifacts are never written to the server's physical disk.

---

## Technical Workflow

1. **Ingestion:** The frontend transmits image data via a lightweight FormData payload.
2. **Analysis:** The Flask backend routes the image buffer to the active vision model (Gemini or Tesseract) for Unicode extraction.
3. **Synthesis:** The extracted text is processed through the translation engine, and audio buffers are generated simultaneously.
4. **Delivery:** The structured JSON response, including text and base64 audio streams, is returned to the client and immediately purged from server memory.

---

## Setup & Installation

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 1. Clone & Install
```bash
git clone https://github.com/avi-071-coder/BENGALI_ASSISTANT_PRO.git
cd BENGALI_ASSISTANT_PRO
pip install -r requirements.txt
```

### 2. Environment Configuration
Create a `.env` file in the root directory and configure your API key:
```env
GEMINI_API_KEY=your_actual_key_here
```


### 3. Execution
Start the Flask application server:
```bash
python app.py
```
