import os 
import templine
from typing import List
from dotenv import load_dotenv
from langchain_core.document_loaders import PyPDFLoader, Docx2txtLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from utils.model_loaders import ModelLoader
from utils.config_loader import load_config
from pinecone import ServerlessSpec
from pinecone import Pinecone
from uuid import uuid4
 
class DataIngestion:
    def __init__(self):
        self.model_loader = ModelLoader()
        self._load_env_variables()
        self.config = load_config()
    
    def _load_env_variables(self):
        load_dotenv()
        required_env_vars = [
            "PINECODE_API_KEY",
            "GOOGLE_API_KEY",
        ]

        missing_vars = [var for var in required_env_vars if os.getenv(var) is None]

        if missing_vars:
            raise EnvironmentError(f"Missing environment variables: {missing_vars}")

        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.pinecode_api_key = os.getenv("PINECODE_API_KEY")

    def _load_documents(self, uploaded_files: List[Document]):
        documents = []
        for uploaded_file in uploaded_files:
            if uploaded_file.name.endswith(".pdf"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                    temp_file.write(uploaded_file.read())
                    loader = PyPDFLoader(temp_file.name)
                    documents.extend(loader.load())
            elif uploaded_file.name.endswith(".docx"):
                with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                    temp_file.write(uploaded_file.read())
                    loader = Docx2txtLoader(temp_file.name)
                    documents.extend(loader.load())
            else:
                print(f"Unsupported file type: {uploaded_file.name}")
        return documents
    
    def store_in_vector_db(self, documents: List[Document]):
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )

        documents = text_splitter.split_documents(documents)
        pc = Pinecone(api_key=self.pinecode_api_key)

        if not pc.has_index(self.config["vector_db"]["index_name"]):
            pc.create_index(
                name=self.config["vector_db"]["index_name"],
                spec=ServerlessSpec(
                    dimension=768,
                    metric="cosine",
                ),
            )

        index = pc.Index(self.config["vector_db"]["index_name"])

        vector_store = PineconeVectorStore(
            index=index,
            embedding=self.model_loader.load_embeddings(),
        )

        uuids = [str(uuid4()) for _ in range(len(documents))]

        vector_store.add_documents(documents=documents, ids=uuids)

        return uuids

    def run_pipeline(self, uploaded_files):
        documents = self._load_documents(uploaded_files)

        if not documents:
            print("No valid documents found")
            return

        self.store_in_vector_db(documents)

if __name__ == "__main__":
    ingestion_pipeline = DataIngestion()
    ingestion_pipeline.run_pipeline()
   