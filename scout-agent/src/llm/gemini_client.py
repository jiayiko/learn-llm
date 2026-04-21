"""Gemini LLM client initialization and configuration."""
from langchain_google_genai import ChatGoogleGenerativeAI


def get_llm_client(model_name: str = "gemini-2.5-flash-lite", temperature: float = 0):
    """
    Initialize and return a Gemini LLM client.
    
    Args:
        model_name: Model name to use (default: gemini-2.5-flash-lite)
        temperature: Temperature setting for LLM (default: 0 for deterministic)
        
    Returns:
        ChatGoogleGenerativeAI instance
    """
    return ChatGoogleGenerativeAI(model=model_name, temperature=temperature)
