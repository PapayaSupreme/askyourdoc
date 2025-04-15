import openai, uuid
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
    for i, chunk in enumerate(chunks):
        print(f"[EMBED] Processing chunk {i + 1} / {len(chunks)}")
        print(chunk[:200])  # peek at the beginning
        embedding = embed_text(chunk)
        docs.append({
            "id": str(uuid.uuid4()),
            "content": chunk,
            "content_vector": embedding
        })
    print(f"[DEBUG] Uploading {len(docs)} documents")
    print(f"[DEBUG] Sample chunk: {chunks[0][:100] if chunks else 'No chunks'}")
    result = client.upload_documents(documents=docs)
    for r in result:
        print(f"✅ Uploaded doc ID: {r.key} | Succeeded: {r.succeeded}")
