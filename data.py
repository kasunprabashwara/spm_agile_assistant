# data.py

import os
from langchain_community.document_loaders import PyPDFLoader

def get_data(docs_folder="docs"):
    documents = []
    for filename in os.listdir(docs_folder):
        if filename.endswith(".pdf"):
            print(f"Loading document: {filename}")
            file_path = os.path.join(docs_folder, filename)
            loader = PyPDFLoader(file_path)
            documents.extend(loader.load_and_split())
    return documents
