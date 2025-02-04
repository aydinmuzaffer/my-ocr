import json
import time
import base64
import re
import warnings
import streamlit as st
import pytesseract
from PIL import Image
import numpy as np

warnings.filterwarnings("ignore")

st.title("📄 Image to Text App (Pytesseract)")


def putMarkdown():
    st.markdown("<hr>", unsafe_allow_html=True)


def get_download_button(data, button_text, filename):
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;charset=utf-8;base64,{b64}" download="{filename}">{button_text}</a>'
    return href


def ocr(image):
    """Extract text from an image using Pytesseract"""
    text = pytesseract.image_to_string(image, lang="tur")  # Use Turkish OCR model
    dict = pytesseract.image_to_string(image, lang="tur", output_type= pytesseract.Output.DICT)  # Use Turkish OCR model
    st.write(f"### 📌 dict: {dict}")
    return text.split("\n")  # Convert text into a list of lines


def extract_fields(text_list):
    """Extract and clean relevant fields from OCR text dynamically"""
    
    # Convert text to uppercase for easier matching
    full_text = " ".join(text_list).upper()

    # Stop processing at "TC KİMLİK NO"
    if "TC KİMLİK NO" in full_text:
        full_text = full_text.split("TC KİMLİK NO")[0]

    # Remove unwanted words
    unwanted_words = {"GELİR İDARESİ", "VERGİ LEVHASI", "BAŞKANLIĞI", "MÜKELLEFİN",
                      "ADI SOYADI", "DAİRESİ", "NO", "TİCARET ÜNVANI", "VERGİ KİMLİK"}

    cleaned_text = " ".join(word for word in full_text.split() if word not in unwanted_words)

    # Extract fields dynamically using regex
    ticari_unvan = re.search(r"TİCARET ÜNVANI\s*:?\s*([\w\sÇĞİÖŞÜ]+)", full_text)
    vergi_dairesi = re.search(r"VERGİ DAİRESİ\s*:?\s*([\w\sÇĞİÖŞÜ]+)", full_text)
    vergi_kimlik_no = re.search(r"VERGİ KİMLİK NO\s*:?\s*([\d\s]+)", full_text)

    # Clean results
    ticari_unvan = ticari_unvan.group(1).strip() if ticari_unvan else "Bilinmiyor"
    vergi_dairesi = vergi_dairesi.group(1).strip() if vergi_dairesi else "Bilinmiyor"
    vergi_kimlik_no = vergi_kimlik_no.group(1).replace(" ", "") if vergi_kimlik_no else "Bilinmiyor"

    return ticari_unvan, vergi_kimlik_no, vergi_dairesi


def display(text_list):
    """Display extracted and cleaned OCR results"""
    st.write("## 🔥 Pytesseract OCR Results 🔥")
    
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
        
        # Convert file to image
        image = Image.open(uploaded_file)

        # Extract text using Pytesseract
        text_list = ocr(image)

        st.write(f"### 📌 Raw OCR Text: {text_list}")  # Show raw extracted text

        # Process and display results
        display(text_list)

        elapsed_time = time.time() - start_time
        st.write(f"### ⏱️ OCR Completed in {elapsed_time:.2f} seconds")


if __name__ == "__main__":
    main()
