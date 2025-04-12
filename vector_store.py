#from langchain.vectorstores import FAISS
from langchain_community.vectorstores import FAISS
#from langchain.embeddings import OllamaEmbeddings
from langchain_community.embeddings import OllamaEmbeddings
#from llama_index.embeddings.ollama import OllamaEmbedding

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List, Dict, Any
import os

class LogVectorDB:
    def __init__(self, model_name="llama3:8b"):
        
       # self.embeddings = OllamaEmbeddings(model=model_name)

        self.embeddings = OllamaEmbeddings(model=model_name)




        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n"]
        )
        self.vectorstore = None
    
    def create_documents(self, logs: List[Dict[str, Any]]) -> List[Document]:
        """Convert parsed logs to Document objects."""
        documents = []
        for i, log in enumerate(logs):
            # Use raw log as text content
            text = log["raw"]
            # Store all parsed fields as metadata
            metadata = {k: v for k, v in log.items() if k != "raw"}
            metadata["id"] = i  # Add an ID for reference
            documents.append(Document(page_content=text, metadata=metadata))
        return documents
    
    def chunk_documents(self, documents: List[Document]) -> List[Document]:
        """Split documents into chunks for better retrieval."""
        return self.text_splitter.split_documents(documents)
    
    def create_vectorstore(self, documents: List[Document]):
        """Create a vector store from documents."""
        self.vectorstore = FAISS.from_documents(documents, self.embeddings)
        return self.vectorstore
    
    def save_vectorstore(self, path: str):
        """Save the vector store to disk."""
        if self.vectorstore:
            self.vectorstore.save_local(path)
    
    def load_vectorstore(self, path: str):
        """Load the vector store from disk."""
        self.vectorstore = FAISS.load_local(path, self.embeddings,allow_dangerous_deserialization=True)
        return self.vectorstore
    
    def similarity_search(self, query: str, k: int = 5):
        """Search for similar log entries."""
        if not self.vectorstore:
            raise ValueError("Vector store not initialized")
        return self.vectorstore.similarity_search(query, k=k)
