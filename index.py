from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex,
    SimpleField,
    SearchField,
    SearchFieldDataType,
    HnswAlgorithmConfiguration,
    VectorSearch,
    AzureOpenAIVectorizer,
    VectorSearchProfile
)
from azure.core.exceptions import ResourceNotFoundError


# Create the client
def setup_index():
    """
    Sets up the Azure Search index with vector search capabilities.
    """
    from config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX, AZURE_OPENAI_ENDPOINT, \
        AZURE_EMBEDDING_DEPLOYMENT
    # Create a SearchIndexClient
    client = SearchIndexClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        credential=AzureKeyCredential(AZURE_SEARCH_KEY)
    )

    # Define vector search configuration + profile
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="hnsw-config",
                kind="hnsw",
                parameters={"m": 4, "efConstruction": 400, "efSearch": 500}
            )
        ],
        vectorizers=[
            AzureOpenAIVectorizer(
                name="openai-vectorizer",
                kind="azureOpenAI",
                azure_open_ai_parameters={
                    "resourceUri": AZURE_OPENAI_ENDPOINT,
                    "deploymentId": AZURE_EMBEDDING_DEPLOYMENT
                }
            )
        ],
        profiles=[
            VectorSearchProfile(
                name="default",
                algorithm_configuration_name="hnsw-config",
                vectorizer="openai-vectorizer"
            )
        ]
    )

    # Define index fields
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SimpleField(name="content", type=SearchFieldDataType.String, searchable=True),
        SearchField(
            name="content_vector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            vector_search_dimensions=1536,
            vector_search_profile_name="default"  # ✅ this is the correct property name
        )

    ]

    # Define the index itself
    index = SearchIndex(
        name=AZURE_SEARCH_INDEX,
        fields=fields,
        vector_search=vector_search
    )

    # Delete if already exists
    try:
        client.get_index(AZURE_SEARCH_INDEX)
        client.delete_index(AZURE_SEARCH_INDEX)
        print(f"🧹 Deleted existing index '{AZURE_SEARCH_INDEX}'")
    except ResourceNotFoundError:
        print(f"ℹ️ Index '{AZURE_SEARCH_INDEX}' does not exist yet. Creating fresh...")

    # Create it
    print(f"✅ Index '{AZURE_SEARCH_INDEX}' created successfully.")
    client.create_index(index)

