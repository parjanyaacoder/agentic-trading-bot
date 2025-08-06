import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from utils.config_loader import load_config
from langchain_groq import ChatGroq

class ModelLoader:

    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config=load_config()

    def _validate_env(self):
        required_vars = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        missing_vars = [var for var in required_vars if not os.getenv(var)]
        if missing_vars:
            print(f"⚠️ Warning: Missing environment variables: {missing_vars}")
            print("💡 For development, you can continue without these variables.")
            # Don't raise error for development
            # raise EnvironmentError(f"Missing environment variables: {missing_vars}")
        
        # Set the API keys as instance attributes
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.groq_api_key = os.getenv("GROQ_API_KEY")

    def load_embeddings(self):
        model_name=self.config["embedding_model"]["model_name"]
        return GoogleGenerativeAIEmbeddings(model=model_name)

    def load_llm(self):
        print("LLM loading...")
        try:
            if not self.groq_api_key:
                raise ValueError("GROQ_API_KEY not configured")
            
            model_name=self.config["llm"]["groq"]["model_name"]
            groq_model=ChatGroq(model=model_name, api_key=self.groq_api_key)
            
            return groq_model
        except Exception as e:
            print(f"❌ Error loading LLM: {str(e)}")
            raise