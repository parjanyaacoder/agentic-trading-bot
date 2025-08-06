import streamlit as st
import requests
from exception.exceptions import TradingBotException
import sys

BASE_URL = "http://localhost:8000"

st.set_page_config(
    page_title="📈 Stock Market Agentic Chatbot",
    page_icon="📈",
    layout="centered",
    initial_sidebar_state="expanded",
)

st.title("📈 Stock Market Agentic Chatbot")

# Check server status
try:
    response = requests.get(f"{BASE_URL}/health", timeout=3)
    if response.status_code == 200:
        st.success("✅ Backend server is running")
    else:
        st.warning("⚠️ Backend server responded with an error")
except requests.exceptions.ConnectionError:
    st.error("❌ Backend server is not running")
    st.info("💡 Start the server with: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
except requests.exceptions.Timeout:
    st.warning("⚠️ Backend server is slow to respond")
    st.info("💡 The server is running but taking time to respond")
except Exception as e:
    st.warning(f"⚠️ Cannot check server status: {str(e)}")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("📄 Upload Documents")
    st.markdown("Upload **stock market PDFs or DOCX** to create knowledge base.")
    uploaded_files = st.file_uploader("Choose files", type=["pdf", "docx"], accept_multiple_files=True)

    if st.button("Upload and Ingest"):
        if uploaded_files:
            files = []
            for f in uploaded_files:
                file_data = f.read()
                if not file_data:
                    continue
                filename = f.name if hasattr(f, 'name') else f"file_{len(files)}.pdf"
                files.append(("files", (filename, file_data, f.type)))

            if files:
                try:
                    with st.spinner("Uploading and processing files..."):
                        response = requests.post(f"{BASE_URL}/upload", files=files, timeout=30)
                        if response.status_code == 200:
                            st.success("✅ Files uploaded and processed successfully!")
                        else:
                            st.error(f"❌ Upload failed (Status: {response.status_code}): {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error("❌ Cannot connect to server. Make sure the FastAPI server is running on port 8000.")
                    st.info("💡 To start the server, run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
                except requests.exceptions.Timeout:
                    st.error("❌ Request timed out. The server is taking too long to respond.")
                except Exception as e:
                    st.error(f"❌ Upload failed: {str(e)}")
                    st.info("💡 Check if the FastAPI server is running and accessible.")
            else:
                st.warning("Some files were empty or unreadable.")

st.header("💬 Chat")
for chat in st.session_state.messages:
    if chat["role"] == "user":
        st.markdown(f"**🧑 You:** {chat['content']}")
    else:
        st.markdown(f"**🤖 Bot:** {chat['content']}")

with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_input("Your message", placeholder="e.g. Tell me about NIFTY 50")
    submit_button = st.form_submit_button("Send")

if submit_button and user_input.strip():
    try:
        st.session_state.messages.append({"role": "user", "content": user_input})

        with st.spinner("Bot is thinking..."):
            payload = {"question": user_input}
            response = requests.post(f"{BASE_URL}/query", json=payload, timeout=30)

        if response.status_code == 200:
            answer = response.json().get("answer", "No answer returned.")
            st.session_state.messages.append({"role": "bot", "content": answer})
            st.rerun()  
        else:
            st.error(f"❌ Bot failed to respond (Status: {response.status_code}): {response.text}")

    except requests.exceptions.ConnectionError:
        st.error("❌ Cannot connect to server. Make sure the FastAPI server is running on port 8000.")
        st.info("💡 To start the server, run: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`")
    except requests.exceptions.Timeout:
        st.error("❌ Request timed out. The server is taking too long to respond.")
    except Exception as e:
        st.error(f"❌ Chat failed: {str(e)}")
        st.info("💡 Check if the FastAPI server is running and accessible.")