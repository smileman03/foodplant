# Import the module
from docx import *
from docx import Document
from docx.shared import Inches

# Open the .docx file
document = Document('ex.docx')
for paragraph in document.paragraphs:
    if '123' in paragraph.text:
        print('Yes')
    else:
        print('No')
# Search returns true if found



