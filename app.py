import json
import time
import base64
import PyPDF2
import warnings
from threading import Timer

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from doctr.io import DocumentFile
from doctr.models import ocr_predictor

warnings.filterwarnings("ignore")

st.title("Image to Text App")


def putMarkdown():
    svg_code = """<svg width="100%" height="5"><line x1="0" y1="5" x2="100%" y2="5" stroke="black" stroke-width="1"/></svg>"""
    # st.write(svg_code, unsafe_allow_html=True)
    st.markdown("<hr>", unsafe_allow_html=True)


def get_download_button(data, button_text, filename):
    # JSON verisini dosyaya yaz
    json_str = json.dumps(data, indent=4)
    b64 = base64.b64encode(json_str.encode()).decode()
    href = f'<a href="data:application/json;charset=utf-8;base64,{b64}" download="{filename}">{button_text}</a>'
    return href


def ocr(item):
    model = ocr_predictor("db_resnet50", "crnn_vgg16_bn", pretrained=True)
    result = model(item)
    json_output = result.export()
    return result, json_output


def display(result, json_output, img):
    st.write("#### Downoad Json output")
    st.write("*⬇*" * 9)

    # Button of Download JSON
    download_button_str = get_download_button(json_output, "DOWNLOAD", "data.json")
    st.markdown(download_button_str, unsafe_allow_html=True)
    putMarkdown()

    # Show the result image
    st.image(img, caption="Original image")
    putMarkdown()

    synthetic_pages = result.synthesize()
    st.image(synthetic_pages, caption="Result of image")

    elapsed_time = time.time() - start_time
    putMarkdown()

    # Show the results
    whole_words = []
    per_line_words = []
    for block in json_output["pages"][0]["blocks"]:
        for line in block["lines"]:
            line_words = []
            for word in line["words"]:
                whole_words.append(word["value"])
                line_words.append(word["value"])
            per_line_words.append(line_words)

    # Put the whole Words
    st.write(f"## Whole Words:")
    st.write(word + " " for word in whole_words)
    putMarkdown()

    # Put the Words line by line
    st.write(f"## Line by Line:")
    for lineWords in per_line_words:
        st.write(word + " " for word in lineWords)
    putMarkdown()

    # Put the Words Word by Word
    st.write(f"## Word by Word:")
    for index, item in enumerate(whole_words):
        st.write(f"**Word {index}**:", item)
    putMarkdown()

    st.write(f"Successful! Passed Time: {elapsed_time:.2f} seconds")

    # Stop processing at "TC KIMLIK NO"
    stop_index = next((i for i, line in enumerate(per_line_words) if "TC KIMLIK NO" in " ".join(line)), None)
    if stop_index is not None:
        per_line_words = per_line_words[:stop_index]

    # Remove the first seven common headers (1-based index means remove 0-6 in 0-based)
    # per_line_words = per_line_words[7:] if len(per_line_words) > 7 else per_line_words

    # --------- SUPER OCR Section ---------
    st.write(f"## 🔥 Super OCR 🔥")

    def clean_text(text):
        """Removes common unwanted words from extracted text."""
        unwanted_words = {"Gelir idaresi", "VERGI LEVHASI", "Bagkanlign", "MUKELLEFIN",
                          "VERGI", "ADI SOYADI", "DAIRESI", "NO", "TC KIMLIK NO", "TICARET ONVANI", "VERGI KIMLIK", "ADI SOYADI"}
        return " ".join(word for word in text.split() if word not in unwanted_words).strip()

    def extract_lines(indices):
        """Extracts and cleans text from given line indices, adjusted for 0-based indexing."""
        return clean_text(" ".join(" ".join(per_line_words[i]) for i in indices if i < len(per_line_words)))

    # **Corrected Indexes (Decreased by 1 to match 0-based index)**
    vergi_dairesi = extract_lines([5, 6, 7])  # Corrected from [6, 7, 8]
    ticari_unvan = extract_lines([8, 9, 10])  # Corrected from [9, 10, 11]
    vergi_kimlik_no = extract_lines([11, 12, 13])  # Corrected from [12, 13, 14]

    # Ensure Ticari Ünvan isn't polluted with unwanted words
    ticari_unvan_filtered = [" ".join(line) for i, line in enumerate(per_line_words) if 8 <= i <= 10 and any(
        word.upper() not in {"VERGI", "NO", "KIMLIK"} for word in line)]
    ticari_unvan = " ".join(ticari_unvan_filtered).strip()

    # Remove non-numeric characters from Vergi Kimlik No and validate
    def extract_valid_number(text):
        import re
        cleaned = re.sub(r'\D', '', text)  # Remove all non-numeric characters
        return cleaned if cleaned.isdigit() else ""

    vergi_kimlik_no = extract_valid_number(vergi_kimlik_no)

    st.write(f"### 📌 Ticari Ünvan: {ticari_unvan or 'Not Found'}")
    st.write(f"### 📌 Vergi Kimlik No: {vergi_kimlik_no or 'Not Found'}")
    st.write(f"### 📌 Vergi Dairesi: {vergi_dairesi or 'Not Found'}")

    putMarkdown()


def main():
    global start_time, seconds_elapsed, stop_time

    # Uploading an image file
    uploaded_file = st.file_uploader(
        "Choose a File", type=["jpg", "jpeg", "png", "pdf"]
    )

    st.write("#### or Put an URL")
    url = st.text_input("Please type an URL:")

    if st.button("Show The URL"):
        st.write("Typed URL:", url)
        start_time = time.time()

        single_img_doc = DocumentFile.from_url(url)
        result, json_output = ocr(single_img_doc)
        display(result, json_output)

    elif uploaded_file is not None:
        # start timer
        start_time = time.time()

        if uploaded_file.type == "application/pdf":
            image = uploaded_file.read()
            single_img_doc = DocumentFile.from_pdf(image)
        else:
            image = uploaded_file.read()
            single_img_doc = DocumentFile.from_images(image)

        result, json_output = ocr(single_img_doc)
        display(result, json_output, image)


if __name__ == "__main__":
    main()
