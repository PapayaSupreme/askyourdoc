from azure.ai.formrecognizer import DocumentAnalysisClient
from azure.core.credentials import AzureKeyCredential

# Replace with your actual values
endpoint = "https://formrecog-grp8.cognitiveservices.azure.com/"
key = "DwrP53PErRePcQJwRPsSeumTlTxpCaOcGGFhg1ZG5KXxRpky6keKJQQJ99BDAC5T7U2XJ3w3AAALACOGftp1"

client = DocumentAnalysisClient(
    endpoint=endpoint,
    credential=AzureKeyCredential(key)
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
