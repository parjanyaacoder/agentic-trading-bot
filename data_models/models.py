from pydantic import BaseModel
from langgraph.graph.message import add_messages

class RagToolSchema(BaseModel):
    question: str

class QuestionRequest(BaseModel):
    question: str
