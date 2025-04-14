from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchFieldDataType,
    VectorSearch, VectorSearchAlgorithmConfiguration, SearchField
)
from azure.core.credentials import AzureKeyCredential
from config import AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX

client = SearchIndexClient(
    endpoint=AZURE_SEARCH_ENDPOINT,
    credential=AzureKeyCredential(AZURE_SEARCH_KEY)
)

vector_config = VectorSearch(
    algorithm_configurations=[
        VectorSearchAlgorithmConfiguration(
            name="default",
            kind="hnsw",
            parameters={"m": 4, "efConstruction": 400, "efSearch": 500}
        )
    ]
)

fields = [
    SimpleField(name="id", type=SearchFieldDataType.String, key=True),
    SimpleField(name="content", type=SearchFieldDataType.String, searchable=True),
    SearchField(
        name="content_vector",
        type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
        searchable=True,
        vector_search_dimensions=1536,
        vector_search_configuration="default"
    )
]

index = SearchIndex(
    name=AZURE_SEARCH_INDEX,
    fields=fields,
    vector_search=vector_config
)

# Delete if exists
if client.get_index(name=AZURE_SEARCH_INDEX):
    client.delete_index(name=AZURE_SEARCH_INDEX)

client.create_index(index)
print(f"✅ Index '{AZURE_SEARCH_INDEX}' created.")
