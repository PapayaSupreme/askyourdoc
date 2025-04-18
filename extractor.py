from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential
from config import (
    FORMRECOG_ENDPOINT, FORMRECOG_APIKEY
)
# Replace with your actual values

client = DocumentAnalysisClient(
    endpoint=FORMRECOG_ENDPOINT,
    credential=AzureKeyCredential(FORMRECOG_APIKEY)
)

def pdf2formrecognizer(file_path: str) -> str:
    """
    Extracts text from a PDF using Azure Form Recognizer's prebuilt-layout model.
    :param file_path: Local path to the PDF
    :return: Raw text content
    """
    with open(file_path, "rb") as f:
        poller = client.begin_analyze_document("prebuilt-layout", document=f)
        result = poller.result()

    all_text = []
    for page in result.pages:
        for line in page.lines:
            all_text.append(line.content)

    return "\n".join(all_text)
