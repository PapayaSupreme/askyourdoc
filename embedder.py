import openai
from math import ceil
from concurrent.futures import ThreadPoolExecutor, as_completed
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from config import (
    AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY,
    AZURE_EMBEDDING_DEPLOYMENT,
    AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX
)

client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2023-05-15",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)

def embed_chunk(i, chunk):
    return {
        "id": f"chunk-{i}",
        "content": chunk,
        "content_vector": embed_text(chunk)
    }

def embed_text(text: str):
    response = client.embeddings.create(
        input=text,
        model=AZURE_EMBEDDING_DEPLOYMENT
    )
    return response.data[0].embedding


def upload_chunks_to_search(chunks):
    client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )

    docs = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(embed_chunk, i, chunk) for i, chunk in enumerate(chunks)]
        for future in as_completed(futures):
            docs.append(future.result())
    print(f"[DEBUG] Uploading {len(docs)} documents")
    print(f"[DEBUG] Sample chunk: {chunks[0][:100] if chunks else 'No chunks'}")
    batch_size = 100
    for i in range(ceil(len(docs) / batch_size)):
        batch = docs[i * batch_size:(i + 1) * batch_size]
        client.upload_documents(documents=batch)
