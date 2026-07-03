# core/pdf_reader.py
# This file handles reading text from PDF and plain text files

import PyPDF2
import os

def read_pdf(file_path: str) -> str:
    """
    Reads a PDF file and returns all the text as a single string.
    """
    text = ""

    with open(file_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)

        # Loop through every page and extract text
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            text += page.extract_text() + "\n"

    return text.strip()


def read_txt(file_path: str) -> str:
    """
    Reads a plain .txt file and returns the content as a string.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read().strip()


def extract_text(file_path: str) -> str:
    """
    Auto-detects file type (PDF or TXT) and returns the text.
    This is the main function app.py will call.
    """
    extension = os.path.splitext(file_path)[1].lower()

    if extension == ".pdf":
        return read_pdf(file_path)
    elif extension == ".txt":
        return read_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {extension}. Please upload a PDF or TXT file.")