import os
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_core.rate_limiters import InMemoryRateLimiter
load_dotenv()


os.environ["TAVILY_API_KEY"] = os.getenv("TAVILY_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LLM_MODEL"] = os.getenv("LLM_MODEL")

model_name = os.environ["LLM_MODEL"]

rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,
    check_every_n_seconds=0.5,
    max_bucket_size=1,
)

llm = init_chat_model(
    model_name,
    temperature=0.3,
    max_retries=6,
    rate_limiter=rate_limiter,
)
