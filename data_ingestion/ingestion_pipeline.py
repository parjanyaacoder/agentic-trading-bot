import os 
import tempfile
import traceback
from typing import List
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_community.document_loaders import PyPDFLoader, Docx2txtLoader, UnstructuredFileLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from utils.model_loaders import ModelLoader
from utils.config_loader import load_config
from pinecone import ServerlessSpec
from pinecone import Pinecone
from uuid import uuid4
from custom_logging.my_logger import logger
 
class DataIngestion:
    def __init__(self):
        logger.info("🔄 Initializing DataIngestion class...")
        self.model_loader = ModelLoader()
        self._load_env_variables()
        self.config = load_config()
        logger.success("✅ DataIngestion initialized successfully")
    
    def _load_env_variables(self):
        logger.info("🔍 Loading environment variables...")
        load_dotenv()
        required_env_vars = [
            "PINECONE_API_KEY",
            "GOOGLE_API_KEY",
        ]

        missing_vars = [var for var in required_env_vars if os.getenv(var) is None]

        if missing_vars:
            logger.warning(f"⚠️ Missing environment variables: {missing_vars}")
            logger.info("💡 For development, you can continue without these variables.")
            # Don't raise error for development
            # raise EnvironmentError(f"Missing environment variables: {missing_vars}")

        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.pinecone_api_key = os.getenv("PINECONE_API_KEY")
        
        logger.info(f"🔑 Google API Key: {'✅ Set' if self.google_api_key else '❌ Missing'}")
        logger.info(f"🔑 Pinecone API Key: {'✅ Set' if self.pinecone_api_key else '❌ Missing'}")

    async def _load_documents(self, uploaded_files: List[Document]):
        logger.info(f"📄 Loading {len(uploaded_files)} documents...")
        documents = []
        
        for i, uploaded_file in enumerate(uploaded_files):
            logger.info(f"📄 Processing file {i+1}: {uploaded_file.filename}")
            
            try:
                if uploaded_file.filename.endswith(".pdf"):
                    logger.debug(f"📄 Loading PDF file: {uploaded_file.filename}")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
                        file_content = await uploaded_file.read()
                        temp_file.write(file_content)
                        loader = PyPDFLoader(temp_file.name)
                        loaded_docs = loader.load()
                        documents.extend(loaded_docs)
                        logger.info(f"✅ PDF loaded: {len(loaded_docs)} pages")
                        
                elif uploaded_file.filename.endswith(".docx"):
                    logger.debug(f"📄 Loading DOCX file: {uploaded_file.filename}")
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".docx") as temp_file:
                        file_content = await uploaded_file.read()
                        temp_file.write(file_content)
                        loader = Docx2txtLoader(temp_file.name)
                        loaded_docs = loader.load()
                        documents.extend(loaded_docs)
                        logger.info(f"✅ DOCX loaded: {len(loaded_docs)} sections")
                        
                else:
                    logger.warning(f"⚠️  Unsupported file type: {uploaded_file.filename}")
                    
            except Exception as e:
                logger.error(f"❌ Error loading file {uploaded_file.filename}: {str(e)}")
                
        logger.success(f"✅ Total documents loaded: {len(documents)}")
        return documents
    
    def store_in_vector_db(self, documents: List[Document]):
        if not self.pinecone_api_key:
            logger.warning("⚠️  PINECONE_API_KEY not configured. Skipping vector storage.")
            return []
            
        try:
            logger.info("🔪 Splitting documents into chunks...")
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200,
                length_function=len,
            )

            documents = text_splitter.split_documents(documents)
            logger.info(f"✅ Documents split into {len(documents)} chunks")
            
            logger.info("🔗 Connecting to Pinecone...")
            pc = Pinecone(api_key=self.pinecone_api_key)
            logger.success("✅ Connected to Pinecone")

            index_name = self.config["vector_db"]["index_name"]
            logger.info(f"🔍 Checking for index: {index_name}")
            
            if not pc.has_index(index_name):
                logger.info(f"🏗️  Creating new index: {index_name}")
                pc.create_index(
                    name=index_name,
                    spec=ServerlessSpec(
                        cloud="aws",
                        region="us-east-1"
                    ),
                    dimension=768,
                    metric="cosine",
                )
                logger.success(f"✅ Index '{index_name}' created successfully")
            else:
                logger.info(f"✅ Index '{index_name}' already exists")

            logger.info("📊 Getting index...")
            index = pc.Index(index_name)
            logger.success("✅ Index retrieved successfully")
            
            logger.info("🔗 Creating vector store...")
            vector_store = PineconeVectorStore(
                index=index,
                embedding=self.model_loader.load_embeddings(),
            )
            logger.success("✅ Vector store created")
            
            logger.info("📝 Generating UUIDs for documents...")
            uuids = [str(uuid4()) for _ in range(len(documents))]
            logger.info(f"✅ Generated {len(uuids)} UUIDs")
            
            logger.info("💾 Adding documents to vector store...")
            vector_store.add_documents(documents=documents, ids=uuids)
            logger.success(f"✅ Successfully stored {len(documents)} documents in vector DB")
            
            return uuids
        
        except Exception as e:
            logger.error(f"❌ Error storing documents in vector DB: {str(e)}")
            logger.debug(f"🔍 Full traceback: {traceback.format_exc()}")
            return []

    async def run_pipeline(self, uploaded_files):
        logger.info("🚀 Starting ingestion pipeline...")
        
        documents = await self._load_documents(uploaded_files)

        if not documents:
            logger.warning("⚠️  No valid documents found")
            return

        logger.info("💾 Storing documents in vector database...")
        self.store_in_vector_db(documents)
        
        logger.success("✅ Ingestion pipeline completed successfully")

if __name__ == "__main__":
    ingestion_pipeline = DataIngestion()
    ingestion_pipeline.run_pipeline()
   