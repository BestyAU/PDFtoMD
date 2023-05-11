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

def format_table_as_markdown(table):
    markdown_table = []
    for row in table:
        # Convert None to an empty string
        row = [str(cell) if cell is not None else '' for cell in row]
        markdown_table.append('| ' + ' | '.join(row) + ' |')
    
    header_separator = '| ' + ' | '.join(['---'] * len(table[0])) + ' |'
    return header_separator + '\n' + '\n'.join(markdown_table)

def pdf_to_markdown(pdf_path, markdown_path):
    with pdfplumber.open(pdf_path) as pdf:
        extracted_text = ""
        for page in tqdm(pdf.pages, desc="Extracting text and tables from pages"):
            extracted_text += page.extract_text()

            # Extract and format tables
            for table in page.extract_tables():
                table_md = format_table_as_markdown(table)
                extracted_text += '\n\n' + table_md

        cleaned_text = clean_extracted_text(extracted_text)

        with open(markdown_path, 'w', encoding='utf-8') as markdown_file:
            markdown_file.write(cleaned_text)

# List files in the 'pdfs' directory
pdf_directory = "pdfs"
pdf_files = [f for f in os.listdir(pdf_directory) if f.lower().endswith(".pdf")]

# Prompt user to choose a file
print("Choose a PDF file to convert:")
for i, pdf_file in enumerate(pdf_files):
    print(f"{i + 1}. {pdf_file}")

file_index = int(input("Enter the file number: ")) - 1
selected_pdf = pdf_files[file_index]

pdf_path = os.path.join(pdf_directory, selected_pdf)
markdown_path = selected_pdf.replace(".pdf", ".md")

pdf_to_markdown(pdf_path, markdown_path)
