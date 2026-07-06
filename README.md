# BongLipi | Authentic Translation

**BongLipi** is a premium, immersive web platform that seamlessly bridges physical Bengali handwriting with digital intelligence. It leverages advanced multimodal vision AI to decode cursive Bengali script, translate its semantic meaning to English, and synthesize bilingual audio—all wrapped in an Awwwards-inspired, cinematic editorial interface.

---

## 🎨 The Aesthetic
We believe language is an art form. The platform departs from traditional "tech/sci-fi" dashboards in favor of a warm, human-centric design:
- **Immersive WebGL:** A custom organic liquid shader responds to scroll and cursor movements.
- **Cinematic Pacing:** Powered by **GSAP** and **Lenis**, the scroll experience is heavy, buttery-smooth, and deliberately paced.
- **Authentic Asset Integration:** Features raw 35mm-film style photography highlighting the rich cultural heritage of Bengal.
- **Massive Typography:** An asymmetric layout blending high-end serifs (*Cormorant Garamond*) with modern sans-serifs (*Outfit*).

## 🚀 Core Features
- **Neural Decoding (OCR):** Uses Google's Gemini Multimodal API as the primary engine for highly accurate cursive recognition, with a seamless fallback to local Tesseract OCR.
- **Cultural Translation:** Translates decoded Bengali into natural English, prioritizing semantic meaning over rigid word-to-word swapping.
- **Bilingual Synthesis (TTS):** Instantly generates audio dictation for both the Bengali transcription and the English translation.
- **Zero-Disk Architecture:** Absolute privacy. Uploaded manuscripts are processed entirely in volatile RAM using `io.BytesIO`. Files are never saved to the server's disk.

---

## 🛠️ How It Works (The Methodology)

1. **Visual Ingestion:** You drop an image of a manuscript into the browser. The image is passed to the Flask backend via a lightweight FormData fetch.
2. **Analysis Pipeline:** The backend routes the image payload to the `Gemini 1.5` model (or Tesseract fallback), which identifies loops and curves to extract unicode Bengali text.
3. **Translation & Speech:** The text is passed through `deep_translator` and converted to MP3 buffers via `gTTS`, streamed directly back to the client.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.9+
- A Google Gemini API Key

### 1. Clone & Install
```bash
git clone https://github.com/avi-071-coder/BENGALI_ASSISTANT_PRO.git
cd BENGALI_ASSISTANT_PRO
pip install -r requirements.txt
```

### 2. Environment Variables
Create a `.env` file in the root directory and add your API key:
```env
GEMINI_API_KEY=your_actual_key_here
```
*(If no key is provided, BongLipi will gracefully degrade to use local Tesseract OCR, though accuracy for handwriting may drop).*

### 3. Run the Platform
Start the Flask application:
```bash
python app.py
```
Open your browser and navigate to `http://127.0.0.1:5000` to experience the platform.

---

## 🔒 Privacy Note
BongLipi respects the intimacy of handwriting. The application is built with a strictly "Zero-Disk" processing pipeline. Images and generated audio files are buffered directly in memory and destroyed once the HTTP request completes. No user data is ever permanently retained.
