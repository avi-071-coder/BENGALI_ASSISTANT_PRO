from deep_translator import GoogleTranslator
import re

def fix_and_translate(raw_text, filename="", confidence=0):
    # Updated clean: Keep only Bengali letters (no numbers or English for chars)
    if 'char' in filename.lower():
        cleaned_ben = re.sub(r'[^\u0980-\u09FF]', '', raw_text)  # Strip everything except Bengali
        cleaned_ben = cleaned_ben[0] if cleaned_ben else ""  # Take only first char
        return cleaned_ben, None, confidence  # No English
    
    # For non-char, keep original cleaning
    cleaned_ben = re.sub(r'[^\u0980-\u09FFa-zA-Z\s।\?]', '', raw_text)
    cleaned_ben = " ".join(cleaned_ben.split())

    if not cleaned_ben:
        return "লেখা শনাক্ত করা যায়নি", None, confidence

    char_count = len(cleaned_ben.replace(" ", ""))
    has_space = " " in cleaned_ben

    if char_count == 1 and not has_space:
        return cleaned_ben, None, confidence  # Single char
    else:
        try:
            translator = GoogleTranslator(source='bn', target='en')
            translation = translator.translate(cleaned_ben)
            return cleaned_ben, translation, confidence
        except Exception as e:
            return cleaned_ben, "Translation error", confidence