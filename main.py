from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from starlette.responses import JSONResponse
from data_ingestion.ingestion_pipeline import DataIngestion
from agent.workflow import GraphBuilder 
from data_models.models import *
from custom_logging.my_logger import logger
import traceback
        

# Add immediate console output
print("🚀 FastAPI server starting...")

# Initialize logger with error handling
try:
    from custom_logging.my_logger import logger
    print("📝 Logger initialized")
except Exception as e:
    print(f"⚠️ Logger initialization failed: {e}")
    # Create a simple fallback logger
    import logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("TradingBot") 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check endpoint"""
    return {"message": "Trading Bot API is running!", "status": "healthy"}

@app.get("/health")
async def health_check():
    """Simple health check endpoint"""
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.now().isoformat()}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    logger.info(f"📤 Upload request received with {len(files)} files")
    
    try:
        # Log file details
        for i, file in enumerate(files):
            logger.info(f"📄 File {i+1}: {file.filename} ({file.size} bytes)")
        
        logger.info("🔄 Initializing DataIngestion pipeline...")
        ingestion_pipeline = DataIngestion()
        
        logger.info("🚀 Starting ingestion pipeline...")
        await ingestion_pipeline.run_pipeline(files)
        
        logger.success("✅ Files uploaded and processed successfully")
        return {"message": "Files uploaded successfully"}
        
    except Exception as e:
        error_msg = f"❌ Upload failed: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"🔍 Full traceback: {traceback.format_exc()}")
        return JSONResponse(content={"message": error_msg}, status_code=500)

@app.post("/query")
async def query_chatbot(request: QuestionRequest):
    logger.info(f"💬 Query request received: {request.question}")
    
    try:
        logger.info("🔄 Building graph service...")
        graph_service = GraphBuilder()
        graph_service.build()
        graph = graph_service.get_graph()

        # Format messages correctly for LangGraph
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=request.question)]
        
        logger.info("🤖 Invoking graph with question...")
        result = graph.invoke({"messages": messages})

        if isinstance(result, dict) and "messages" in result:
            final_output = result["messages"][-1].content
        else:
            final_output = str(result)

        logger.success(f"✅ Query processed successfully")
        return {"answer": final_output}
        
    except Exception as e:
        error_msg = f"❌ Query failed: {str(e)}"
        logger.error(error_msg)
        logger.debug(f"🔍 Full traceback: {traceback.format_exc()}")
        return JSONResponse(content={"error": error_msg}, status_code=500)