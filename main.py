import os
import pdfplumber
import re
from tqdm import tqdm

def should_combine(line1, line2):
    return not re.search(r'[.?!;:\-–—]$', line1.strip())

def clean_extracted_text(text):
    lines = text.split('\n')
    cleaned_lines = []

    for i, line in enumerate(lines):
        if i > 0 and should_combine(lines[i - 1], line):
            cleaned_lines[-1] += ' ' + line.strip()
        else:
            cleaned_lines.append(line.strip())

    return '\n\n'.join(cleaned_lines)

def validate_pdf(pdf_path):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            pass
        return True
    except FileNotFoundError:
        print(f"{pdf_path} does not exist.")
        return False
    except pdfplumber.PDFSyntaxError:
        print(f"Could not open {pdf_path} as a PDF file.")
        return False

def pdf_to_markdown(pdf_path, markdown_path):
    # Check if the markdown file already exists
    if os.path.exists(markdown_path):
        overwrite = input(f"{markdown_path} already exists. Do you want to overwrite it? (y/n): ")
        if overwrite.lower() != 'y':
            print("Skipping conversion.")
            return

    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = ""
        for page in tqdm(pdf.pages, desc="Extracting text from pages"):
            extracted_text += page.extract_text()

        cleaned_text = clean_extracted_text(extracted_text)

        with open(markdown_path, 'w', encoding='utf-8') as markdown_file:
            markdown_file.write(cleaned_text)

# List files in the 'pdfs' directory
pdf_directory = "pdfs"
pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith(".pdf")]

# Prompt user to choose a file
print("Choose a PDF file to convert:")
valid_pdf_files = []
for i, pdf_file in enumerate(pdf_files):
    pdf_path = os.path.join(pdf_directory, pdf_file)
    if validate_pdf(pdf_path):
        valid_pdf_files.append(pdf_file)
        print(f"{len(valid_pdf_files)}. {pdf_file}")

# Validate user input
while True:
    try:
        file_index = int(input("Enter the file number: ")) - 1
        if 0 <= file_index < len(valid_pdf_files):
            break
        else:
            print("Invalid input. Please enter a number corresponding to the listed files.")
    except ValueError:
        print("Invalid input. Please enter a number.")

selected_pdf = valid_pdf_files[file_index]

pdf_path = os.path.join(pdf_directory, selected_pdf)
markdown_path = selected_pdf.replace(".pdf", ".md")

pdf_to_markdown(pdf_path, markdown_path)
