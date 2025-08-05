import os
from langchain.tools import tool
from langchain_community.tools import TavilySearchResults
from langchain_core.tools.polygon.financials import PolygonFinancials
from langchain_community.utilties.polygon import PolygonAPIWrapper
from langchain_community.tools.bing_search import BingSearchResults
from data_models.models import RagToolSchema
from langchain_pinecone import PineconeVectorStore
from utils.model_loader import ModelLoader
from utils.config_loader import load_config
from dotenv import load_dotenv

api_wrapper = PolygonAPIWrapper()
model_loader = ModelLoader()
config = load_config()

load_dotenv()

pinecode_api_key = os.getenv("PINECODE_API_KEY")
pc = Pinecone(api_key=pinecode_api_key)
embedding = config["embedding_model"]["model_name"]
index = pc.Index(config["vector_db"]["index_name"])




@tool(args_schema=RagToolSchema)
def retriever_tool(question):
    pinecode_api_key = os.getenv("PINECODE_API_KEY")
    pc = Pinecone(api_key=pinecode_api_key)
    embedding = model_loader.load_embeddings()
    index = pc.Index(config["vector_db"]["index_name"])
    vector_store = PineconeVectorStore(index=index, embedding=embedding)
    retriever = vector_store.as_retriever(
        search_type="similarity_score_threshold",
        search_kwargs={"k": config["retriever"]["top_k"],
        "score_threshold": config["retriever"]["score_threshold"]}
    )
    retriever_result = retriever.invoke(question)

    return retriever_result

tavily_tool = TavilySearchResults(
    max_results=config["tools"]["tavily"]["max_results"],
    search_depth="advanced",
    include_raw_content=True,
    include_answer=True
    )

financials_tool = PolygonFinancials(api_wrapper=api_wrapper)

