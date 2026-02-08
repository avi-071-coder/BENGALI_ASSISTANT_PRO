# Bengali Assistant Pro: Handwriting OCR & Voice Synthesis

An automated pipeline that converts Bengali handwriting into digital text, translates it to English, and generates bilingual audio output.

## 🛠️ Features
- **Vision:** OpenCV-based image preprocessing for stroke enhancement.
- **OCR:** Tesseract LSTM engine specifically for Bengali script.
- **Logic:** Intelligent gating to handle single characters vs. sentences.
- **Speech:** Multi-modal audio generation (Bengali & English).

## 📂 Structure
- `pipeline/`: Core modules (Vision, Logic, Voice).
- `data/`: Folder for input images.
- `output/`: Folder for generated audio/images.

## 🚀 How to Use
1. Install Tesseract OCR.
2. Run `pip install -r requirements.txt`.
3. Put images in `data/raw_scans/` and run `python main.py`.

⚠️ Known Limitations (Work in Progress)

1.While this project is functional, it is currently in active development. The following areas are being improved:

2.Single Character Recognition: The model occasionally struggles with isolated characters where context is missing.

3.Long Paragraphs: Processing large blocks of text can result in a decrease in accuracy or "drift" in the OCR alignment.

4.Handwriting Variability: Extremely cursive or stylistic Bengali handwriting may require further fine-tuning.
