from extractor import pdf2formrecognizer
from chunker import split_by_sections

text = pdf2formrecognizer("sectioned_lesson.pdf")
chunks = split_by_sections(text)
for cell in chunks:
    print(cell[:300])
"""for i, chunk in enumerate(chunks):
    print(f"\n--- Section {i+1} ---\n{chunk[:300]}...")"""
