import json
import time
import base64
import warnings
import re
import streamlit as st
import easyocr
import re

warnings.filterwarnings("ignore")

st.title("📄 Image to Text App (EasyOCR)")

# Initialize EasyOCR reader (supports Turkish)
@st.cache_resource
def load_ocr_model():
    return easyocr.Reader(["tr"])  # Turkish language support

reader = load_ocr_model()

def putMarkdown():
    st.markdown("<hr>", unsafe_allow_html=True)

def get_download_button(data, button_text, filename):
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;charset=utf-8;base64,{b64}" download="{filename}">{button_text}</a>'
    return href

def ocr(image):
    """Extract text from an image using EasyOCR"""
    result = reader.readtext(image, detail=0)  # Get text only, ignore bounding boxes
    return [text for text in result]  # Convert all text to uppercase for better matching

import re

def extract_fields(text_list):
    """Extract Ticari Ünvan, Vergi Kimlik No, and Vergi Dairesi dynamically using indexes."""
    
    # Convert list to uppercase string for easy searching
    full_text = " ".join(text_list).upper()

    # Drop everything after "TC KİMLİK NO"
    if "TC KİMLİK NO" in text_list:
        stop_index = text_list.index("TC KİMLİK NO")
        text_list = text_list[:stop_index]

    # Define unwanted words
    unwanted_words = {
        "GELİR İDARESİ" "GELIR IDAROSI", "VERGİ LEVHASI", "VERGI LEVHASI" , "BAŞKANLIĞI", "MÜKELLEFİN", "MÜKELLEFIN",
        "ADI SOYADI", "VERGİ", "VERGI", "TICARET ÜNVANI", "NO", "VERGI KIMLIK", "DAİRESİ", "TİCARET ÜNVANI",
        "VERGİ KİMLİK", "TC KİMLİK NO", "TC KİMLIK NO", "İŞ YERİ ADRESİ"
    }

    # Find index positions of key fields
    ticaret_index = next((i for i, word in enumerate(text_list) if "TİCARET ÜNVANI" in word or "TICARET ÜNVANI" in word), None)
    vergi_dairesi_index = next((i for i, word in enumerate(text_list) if "VERGİ DAİRESİ" in word or "VERGI" in word), None)
    vergi_kimlik_no_index = next((i for i, word in enumerate(text_list) if "VERGİ KİMLİK" in word or "VERGI KIMLIK" in word), None)

    # Extract possible values
    ticari_unvan = text_list[ticaret_index + 1] if ticaret_index is not None and ticaret_index + 1 < len(text_list) else "Bilinmiyor"
    vergi_dairesi = text_list[vergi_dairesi_index + 1] if vergi_dairesi_index is not None and vergi_dairesi_index + 1 < len(text_list) else "Bilinmiyor"
    
    # Handle Vergi Kimlik No: Check if it's a valid number
    if vergi_kimlik_no_index is not None and vergi_kimlik_no_index + 1 < len(text_list):
        possible_vergi_no = text_list[vergi_kimlik_no_index + 1]
        possible_vergi_no = re.sub(r"\D", "", possible_vergi_no)  # Remove spaces and non-numeric characters
        
        if possible_vergi_no.isdigit() and 10 <= len(possible_vergi_no) <= 11:  # Ensure it's a 10-11 digit number
            vergi_kimlik_no = possible_vergi_no
        else:
            vergi_kimlik_no = "Bilinmiyor"
    else:
        vergi_kimlik_no = "Bilinmiyor"

    return ticari_unvan, vergi_kimlik_no, vergi_dairesi


def display(text_list):
    """Display extracted and cleaned OCR results"""
    st.write("## 🔥 EasyOCR Results 🔥")
    
    ticari_unvan, vergi_kimlik_no, vergi_dairesi = extract_fields(text_list)

    # Display results
    st.write(f"### 📌 Ticari Ünvan: {ticari_unvan}")
    st.write(f"### 📌 Vergi Kimlik No: {vergi_kimlik_no}")
    st.write(f"### 📌 Vergi Dairesi: {vergi_dairesi}")

    putMarkdown()

def main():
    # File uploader
    uploaded_file = st.file_uploader("Choose a File", type=["jpg", "jpeg", "png", "pdf"])
    
    if uploaded_file is not None:
        start_time = time.time()
        
        # Read image
        image = uploaded_file.read()
        text_list = ocr(image)  # Extract text
        
        st.write(f"### 📌 Raw OCR Text: {text_list}")  # Show raw extracted text
        
        # Extract Ticari Ünvan, Vergi Kimlik No, and Vergi Dairesi
        ticari_unvan, vergi_kimlik_no, vergi_dairesi = extract_fields(text_list)

        # Display extracted data
        st.write("## 🔥 EasyOCR Extracted Data 🔥")
        st.write(f"### 📌 Ticari Ünvan: {ticari_unvan}")
        st.write(f"### 📌 Vergi Kimlik No: {vergi_kimlik_no}")
        st.write(f"### 📌 Vergi Dairesi: {vergi_dairesi}")

        elapsed_time = time.time() - start_time
        st.write(f"### ⏱️ OCR Completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
