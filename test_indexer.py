import streamlit as st
import numpy as np
import openai
import uuid
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndex, SimpleField, SearchField, SearchFieldDataType,
    HnswAlgorithmConfiguration, VectorSearch, AzureOpenAIVectorizer, VectorSearchProfile
)
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import ResourceNotFoundError
from config import *

from chunker import pdf2text, split_by_sections