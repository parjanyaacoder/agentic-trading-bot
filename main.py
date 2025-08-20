from fastapi import FastAPI, UploadFile, File, Request, Form 
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.background import BackgroundTasks
# from starlette.responses import JSONResponse
from data_ingestion.ingestion_pipeline import DataIngestion
from agent.workflow import GraphBuilder 
from data_models.models import *
from custom_logging.my_logger import logger
import traceback, os
        

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

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Landing page with health status."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/chat", response_class=HTMLResponse)
async def chat_ui(request: Request):
    """Chat UI page."""
    return templates.TemplateResponse("chat.html", {"request": request})

@app.get("/health")
async def health():
    from datetime import datetime
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try:
        logger.info(f"📤 Upload request with {len(files)} files")
        ingestion_pipeline = DataIngestion()
        await ingestion_pipeline.run_pipeline(files)
        return {"message": "Files uploaded and processed"}
    except Exception as e:
        logger.error(traceback.format_exc())
        return JSONResponse(status_code=500,
                            content={"error": f"Upload failed: {e}"})
    


@app.post("/query")
async def query_chatbot(question: str = Form(...)):
    logger.info(f"💬 Query request received: {question}")
    
    try:
        logger.info("🔄 Building graph service...")
        graph_service = GraphBuilder()
        graph_service.build()
        graph = graph_service.get_graph()

        # Format messages correctly for LangGraph
        from langchain_core.messages import HumanMessage
        messages = [HumanMessage(content=question)]
        
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