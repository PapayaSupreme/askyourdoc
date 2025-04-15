import streamlit as st
from config import *
from chunker import split_by_sections
from embedder import embed_text, upload_chunks_to_search
from index import setup_index
from extractor import pdf2formrecognizer
import openai
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.core.credentials import AzureKeyCredential

# === OpenAI Client ===
client = openai.AzureOpenAI(
    api_key=AZURE_OPENAI_KEY,
    api_version="2023-05-15",
    azure_endpoint=AZURE_OPENAI_ENDPOINT
)
index_admin = SearchIndexClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)


# === Native Vector Search ===
def native_vector_search(query_vector, top_k=3):
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name=AZURE_SEARCH_INDEX,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )
    results = search_client.search(
        search_text="*",
        vector_queries=[
            {
                "kind": "vector",
                "vector": query_vector,
                "k": top_k,
                "fields": "content_vector"
            }
        ],
        select=["content"]
    )
    return [doc["content"] for doc in results]




# === GPT Answer ===
def ask_gpt(query, context_docs):
    context = "\n\n".join(context_docs)
    prompt = f"""Answer the question using the context below.

Context:
{context}

Question: {query}
Answer:"""
    response = client.chat.completions.create(
        model=AZURE_OPENAI_DEPLOYMENT,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
# === user query handling/clearing ===
def handle_query():
    user_input = st.session_state.query_input
    if user_input:
        with st.spinner("Thinking..."):
            q_vec = embed_text(user_input)
            context = native_vector_search(q_vec)
            if not context:
                st.session_state.answer = "No relevant documents found. Try uploading a richer PDF or adjusting your question."
            else:
                st.session_state.answer = ask_gpt(user_input, context)
    st.session_state.query_input = ""  # safe to clear inside callback

# === Streamlit UI ===
if "alrScanned" not in st.session_state:
    st.session_state.alrScanned = False

if "last_uploaded_filename" not in st.session_state:
    st.session_state.last_uploaded_filename = ""

st.title("📚 AskYourDoc Assistant")

pdf_file = st.file_uploader("Upload a PDF to index:", type=["pdf"])

if pdf_file is not None:
    if pdf_file.name != st.session_state.last_uploaded_filename:
        with open("uploaded.pdf", "wb") as f:
            f.write(pdf_file.read())
        with st.spinner("Setting up index and processing..."):
            setup_index()
            text = pdf2formrecognizer("uploaded.pdf")
            chunks = split_by_sections(text)
            upload_chunks_to_search(chunks)
        st.session_state.alrScanned = True
        st.session_state.last_uploaded_filename = pdf_file.name
        st.success("✅ Document indexed and ready!")
    else:
        st.info("✅ This document was already indexed.")

if pdf_file:
    st.text_input("Ask a question about your doc:",
                  key="query_input", on_change=handle_query)
    if "answer" in st.session_state and st.session_state.answer:
        st.subheader("💡 Answer")
        st.write(st.session_state.answer)
