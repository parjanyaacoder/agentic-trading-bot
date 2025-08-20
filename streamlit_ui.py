import streamlit as st
import requests
from exception.exceptions import TradingBotException
import sys
import os
import logging
import time
import traceback
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_ui.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Log application startup
logger.info("=" * 50)
logger.info("STREAMLIT UI STARTING")
logger.info("=" * 50)
logger.info(f"Start time: {datetime.now()}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Streamlit version: {st.__version__}")

BASE_URL = os.getenv("BACKEND_URL")
logger.info(f"BASE_URL from environment: {BASE_URL}")

# Log page configuration
logger.info("Setting up Streamlit page configuration...")
try:
    st.set_page_config(
        page_title="📈 Stock Market Agentic Chatbot",
        page_icon="📈",
        layout="centered",
        initial_sidebar_state="expanded",
    )
    logger.info("Page configuration set successfully")
except Exception as e:
    logger.error(f"Failed to set page configuration: {str(e)}")
    logger.error(traceback.format_exc())

logger.info("Setting up page title...")
st.title("📈 Stock Market Agentic Chatbot")

# Check server status with detailed logging
logger.info("Checking backend server status...")
try:
    logger.info(f"Making health check request to: {BASE_URL}/health")
    start_time = time.time()
    response = requests.get(f"{BASE_URL}/health", timeout=3)
    end_time = time.time()
    logger.info(f"Health check completed in {end_time - start_time:.2f} seconds")
    logger.info(f"Response status: {response.status_code}")
    logger.info(f"Response headers: {dict(response.headers)}")
    
    if response.status_code == 200:
        logger.info("Backend server is healthy")
        st.success("✅ Backend server is running")
    else:
        logger.warning(f"Backend server responded with error status: {response.status_code}")
        logger.warning(f"Response content: {response.text}")
        st.warning("⚠️ Backend server responded with an error")
        
except requests.exceptions.ConnectionError as e:
    logger.error(f"Connection error during health check: {str(e)}")
    logger.error(f"BASE_URL: {BASE_URL}")
    st.error("❌ Backend server is not running")
    st.info("💡 Start the server with: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
except requests.exceptions.Timeout as e:
    logger.warning(f"Timeout during health check: {str(e)}")
    st.warning("⚠️ Backend server is slow to respond")
    st.info("💡 The server is running but taking time to respond")
except Exception as e:
    logger.error(f"Unexpected error during health check: {str(e)}")
    logger.error(traceback.format_exc())
    st.warning(f"⚠️ Cannot check server status: {str(e)}")

# Initialize session state
logger.info("Initializing session state...")
if "messages" not in st.session_state:
    logger.info("Creating new messages session state")
    st.session_state.messages = []
else:
    logger.info(f"Existing messages in session: {len(st.session_state.messages)}")

# Sidebar setup
logger.info("Setting up sidebar...")
with st.sidebar:
    st.header("📄 Upload Documents")
    st.markdown("Upload **stock market PDFs or DOCX** to create knowledge base.")
    
    logger.info("Creating file uploader...")
    uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx"], accept_multiple_files=True)
    
    if uploaded_files:
        logger.info(f"Files uploaded: {[f.name for f in uploaded_files]}")

    if st.button("Upload and Ingest"):
        logger.info("Upload and Ingest button clicked")
        if uploaded_files:
            logger.info(f"Processing {len(uploaded_files)} uploaded files")
            files = []
            for i, f in enumerate(uploaded_files):
                logger.info(f"Processing file {i+1}: {f.name} (type: {f.type})")
                try:
                    file_data = f.read()
                    logger.info(f"File {f.name} size: {len(file_data)} bytes")
                    if not file_data:
                        logger.warning(f"File {f.name} is empty, skipping")
                        continue
                    filename = f.name if hasattr(f, 'name') else f"file_{len(files)}.pdf"
                    files.append(("files", (filename, file_data, f.type)))
                    logger.info(f"Successfully added file {filename} to upload list")
                except Exception as e:
                    logger.error(f"Error processing file {f.name}: {str(e)}")
                    logger.error(traceback.format_exc())

            if files:
                logger.info(f"Preparing to upload {len(files)} files")
                try:
                    with st.spinner("Uploading and processing files..."):
                        logger.info(f"Making upload request to: {BASE_URL}/upload")
                        start_time = time.time()
                        response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
                        end_time = time.time()
                        logger.info(f"Upload request completed in {end_time - start_time:.2f} seconds")
                        logger.info(f"Upload response status: {response.status_code}")
                        logger.info(f"Upload response headers: {dict(response.headers)}")
                        
                        if response.status_code == 200:
                            logger.info("Files uploaded and processed successfully")
                            st.success("✅ Files uploaded and processed successfully!")
                        else:
                            logger.error(f"Upload failed with status {response.status_code}: {response.text}")
                            st.error(f"❌ Upload failed (Status: {response.status_code}): {response.text}")
                            
                except requests.exceptions.ConnectionError as e:
                    logger.error(f"Connection error during upload: {str(e)}")
                    st.error("❌ Cannot connect to server. Make sure the FastAPI server is running on port 8000.")
                    st.info("💡 To start the server, run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
                except requests.exceptions.Timeout as e:
                    logger.error(f"Timeout during upload: {str(e)}")
                    st.error("❌ Request timed out. The server is taking too long to respond.")
                except Exception as e:
                    logger.error(f"Unexpected error during upload: {str(e)}")
                    logger.error(traceback.format_exc())
                    st.error(f"❌ Upload failed: {str(e)}")
                    st.info("💡 Check if the FastAPI server is running and accessible.")
            else:
                logger.warning("No valid files to upload")
                st.warning("Some files were empty or unreadable.")
        else:
            logger.warning("Upload button clicked but no files selected")

# Chat interface setup
logger.info("Setting up chat interface...")
st.header("💬 Chat")

# Display existing messages
logger.info(f"Displaying {len(st.session_state.messages)} existing messages")
for i, chat in enumerate(st.session_state.messages):
    logger.info(f"Displaying message {i+1}: {chat['role']} - {chat['content'][:50]}...")
    if chat["role"] == "user":
        st.markdown(f"**🧑 You:** {chat['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {chat['content']}")

# Chat form
logger.info("Creating chat form...")
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message", placeholder="e.g. Tell me about NIFTY 50")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    logger.info(f"Chat form submitted with input: {user_input}")
    try:
        logger.info("Adding user message to session state")
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Bot is thinking..."):
            logger.info("Preparing chat request payload")
            payload = {"question": user_input}
            logger.info(f"Making chat request to: {BASE_URL}/query")
            logger.info(f"Request payload: {payload}")
            
            start_time = time.time()
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)
            end_time = time.time()
            logger.info(f"Chat request completed in {end_time - start_time:.2f} seconds")
            logger.info(f"Chat response status: {response.status_code}")
            logger.info(f"Chat response headers: {dict(response.headers)}")

        if response.status_code == 200:
            logger.info("Chat request successful, processing response")
            response_data = response.json()
            logger.info(f"Response data keys: {list(response_data.keys())}")
            answer = response_data.get("answer", "No answer returned.")
            logger.info(f"Bot answer length: {len(answer)} characters")
            logger.info(f"Bot answer preview: {answer[:100]}...")
            
            logger.info("Adding bot response to session state")
            st.session_state.messages.append({"role": "bot", "content": answer})
            logger.info("Triggering page rerun")
            st.rerun()  
        else:
            logger.error(f"Chat request failed with status {response.status_code}: {response.text}")
            st.error(f"❌ Bot failed to respond (Status: {response.status_code}): {response.text}")

    except requests.exceptions.ConnectionError as e:
        logger.error(f"Connection error during chat: {str(e)}")
        st.error("❌ Cannot connect to server. Make sure the FastAPI server is running on port 8000.")
        st.info("💡 To start the server, run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
    except requests.exceptions.Timeout as e:
        logger.error(f"Timeout during chat: {str(e)}")
        st.error("❌ Request timed out. The server is taking too long to respond.")
    except Exception as e:
        logger.error(f"Unexpected error during chat: {str(e)}")
        logger.error(traceback.format_exc())
        st.error(f"❌ Chat failed: {str(e)}")
        st.info("💡 Check if the FastAPI server is running and accessible.")

logger.info("Streamlit UI setup completed")
logger.info("=" * 50)