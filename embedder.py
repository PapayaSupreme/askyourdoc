import openai
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import (
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY,
    AZURE_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX
)
import uuid

openai.api_key = AZURE_OPENAI_KEY
openai.api_base = AZURE_OPENAI_ENDPOINT
openai.api_type = 'azure'
openai.api_version = '2023-05-15'


def embed_text(text: str):
    response = openai.Embedding.create(
        input=text,
        engine=AZURE_EMBEDDING_DEPLOYMENT
    )
    return response['data'][0]['embedding']


def upload_chunks_to_search(chunks):
    client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )

    docs = []
    for i, chunk in enumerate(chunks):
        embedding = embed_text(chunk)
        docs.append({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "content_vector": embedding
        })

    result = client.upload_documents(documents=docs)
    print(f"Upload result: {result}")
