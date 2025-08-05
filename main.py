from fastapi import FastAPI, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import List
from starlette.responses import JSONResponse
from data_ingestion.ingestion_pipeline import DataIngestion
from agent.workflow import GraphBuilder 
from data_models.models import * 

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    try: 
        ingestion_pipeline = DataIngestion()
        ingestion_pipeline.run_pipeline(files)
        return {"message": "Files uploaded successfully"}
    except Exception as e:
        return JSONResponse(content={"message": str(e)}, status_code=500)

@app.post("/query")
async def query_chatbot(request: QuestionRequest):
    try:
        graph_service = GraphBuilder()
        graph_service.build()
        graph = graph_service.get_graph()

        messages = {"messages": [request.question]}
        
        result = graph.invoke({"message": messages})

        if isinstance(result, dict) and "messages" in result:
            final_output = result["messages"][-1].content
        else:
            final_output = str(result)

        return {"answer": final_output}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)