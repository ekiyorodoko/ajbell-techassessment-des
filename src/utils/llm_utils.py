"""
LLM utilities module.
Provides functions for working with language models.
"""

import os
from typing import Optional, Dict, Any, Union

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import OllamaLLM


def get_llm(
    provider: str = "local", 
    model_name: Optional[str] = None,
    api_key: Optional[str] = None,
    temperature: float = 0.0
) -> BaseChatModel:
    """Get a language model based on provider choice.
    
    Args:
        provider: LLM provider to use (local, openai, google)
        model_name: Model name for the chosen provider
        api_key: API key for the chosen provider
        temperature: Temperature setting for the LLM
        
    Returns:
        Configured LLM
        
    Raises:
        ValueError: If an unsupported provider is specified or API key is missing
    """
    if provider == "local":
        # Use local model via Ollama
        return OllamaLLM(model=model_name or "llama3", temperature=temperature)
    
    elif provider == "openai":
        # Use OpenAI model
        if not api_key and "OPENAI_API_KEY" not in os.environ:
            raise ValueError("OpenAI API key required but not provided")
            
        key = api_key or os.environ.get("OPENAI_API_KEY")
        return ChatOpenAI(
            api_key=key, 
            model_name=model_name or "gpt-4o",
            temperature=temperature
        )
    
    elif provider == "google":
        # Use Google Gemini model
        if not api_key and "GOOGLE_API_KEY" not in os.environ:
            raise ValueError("Google API key required but not provided")
            
        key = api_key or os.environ.get("GOOGLE_API_KEY")
        return ChatGoogleGenerativeAI(
            api_key=key, 
            model=model_name or "gemini-1.5-pro",
            temperature=temperature
        )
    
    else:
        raise ValueError(f"Unsupported LLM provider: {provider}")


def get_available_providers() -> Dict[str, Dict[str, Any]]:
    """Get information about available LLM providers.
    
    Returns:
        Dictionary mapping provider names to information about them
    """
    return {
        "local": {
            "name": "Local (Ollama)",
            "description": "Run models locally using Ollama",
            "default_model": "llama3",
            "requires_api_key": False,
            "env_var": None,
            "models": ["llama3", "mistral", "mixtral", "phi3"]
        },
        "openai": {
            "name": "OpenAI",
            "description": "OpenAI's advanced models",
            "default_model": "gpt-4o",
            "requires_api_key": True,
            "env_var": "OPENAI_API_KEY",
            "models": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"]
        },
        "google": {
            "name": "Google Gemini",
            "description": "Google's Gemini models",
            "default_model": "gemini-1.5-pro",
            "requires_api_key": True,
            "env_var": "GOOGLE_API_KEY",
            "models": ["gemini-1.5-pro", "gemini-1.5-flash"]
        }
    }