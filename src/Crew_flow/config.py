from crewai import LLM
from functools import lru_cache

@lru_cache(maxsize=1)
def get_llm():
    llm = LLM(
        model="groq/llama-3.3-70b-versatile",
        temperature = 0.5
    )

    return llm