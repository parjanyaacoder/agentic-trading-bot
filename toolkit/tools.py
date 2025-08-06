import os
from langchain.tools import tool
from langchain_community.tools import TavilySearchResults
from langchain_community.tools.polygon.financials import PolygonFinancials
from langchain_community.utilities.polygon import PolygonAPIWrapper
from data_models.models import RagToolSchema
from langchain_pinecone import PineconeVectorStore
from utils.model_loaders import ModelLoader
from utils.config_loader import load_config
from dotenv import load_dotenv
from pinecone import Pinecone
load_dotenv()
api_wrapper = PolygonAPIWrapper()
model_loader=ModelLoader()
config = load_config()

@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    """Retrieve relevant documents from vector database"""
    try:
        pinecone_api_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_api_key:
            return "⚠️ Pinecone API key not configured. RAG features disabled."
        
        pc = Pinecone(api_key=pinecone_api_key)
        vector_store = PineconeVectorStore(
            index=pc.Index(config["vector_db"]["index_name"]), 
            embedding=model_loader.load_embeddings()
        )
        retriever = vector_store.as_retriever(
            search_type="similarity_score_threshold",
            search_kwargs={
                "k": config["retriever"]["top_k"], 
                "score_threshold": config["retriever"]["score_threshold"]
            },
        )
        retriever_result = retriever.invoke(question)
        return retriever_result
    except Exception as e:
        return f"❌ Error in RAG tool: {str(e)}"

tavily_tool = TavilySearchResults(
    max_results=config["tools"]["tavily"]["max_results"],
    search_depth="advanced",
    include_raw_content=True,
    include_answer=True
    )

financials_tool = PolygonFinancials(api_wrapper=api_wrapper)