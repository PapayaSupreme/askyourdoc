import re
def split_by_sections(text: str) -> list:
    """
    Splits text into title/section-aware chunks based on headings.
    :param text: Full document text
    :return: List of section chunks (each as a string)
    """

    # Regex to match typical section titles (numbered or all caps)
    section_pattern = re.compile(
        r'(?:^|\n)(\d{1,2}(?:\.\d+)*\.?\s+.*|[A-Z][A-Z\s]{5,})', re.MULTILINE
    )

    matches = list(section_pattern.finditer(text))
    chunks = []

    for i in range(len(matches)):
        start = matches[i].start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunk = text[start:end].strip()
        if len(chunk) > 20:
            chunks.append(chunk)

    if not chunks:
        # fallback to paragraph splits
        print("[⚠️] No sections matched. Falling back to paragraph splits.")
        paragraphs = [p.strip() for p in text.split('\n\n') if len(p.strip()) > 20]
        chunks.extend(paragraphs)

    return chunks
