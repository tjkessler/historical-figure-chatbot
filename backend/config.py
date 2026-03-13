import os

from dotenv import load_dotenv


load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "chatbot.db")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")
HUGGINGFACE_MODEL = os.getenv("HUGGINGFACE_MODEL", "meta-llama/Llama-3.1-8B-Instruct:cerebras")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
