import PyPDF2, os, re

def pdf2text(file_path: str) -> str:
    """
    Extracts all text from a PDF file using PyPDF2.
    :param file_path: Path to the PDF file
    :return: Extracted text as a single string
    """
    text = ""
    try:
        with open(file_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page_num, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
    except Exception as e:
        print(f"[!] Failed to extract PDF text: {e}")
    return text

test = pdf2text(os.getcwd()+"/sectioned_lesson.pdf")
def split_by_sections(text: str) -> list:
    """
    Splits text into title/section-aware chunks based on headings.
    :param text: Full document text
    :return: List of section chunks (each as a string)
    """

    # Regex to match typical section titles (numbered or all caps)
    section_pattern = re.compile(
        r'(?=\n*(?:\d{1,2}(?:\.\d+)*\.?\s+|[A-Z][A-Z\s]{5,}))', re.MULTILINE
    )

    # Split text at section headings
    raw_sections = section_pattern.split(text)

    # Filter out tiny or empty sections
    sections = [s.strip() for s in raw_sections if len(s.strip()) > 20]

    return sections

for cell in split_by_sections(test):
    print(cell)
