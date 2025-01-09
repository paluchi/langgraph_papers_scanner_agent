from typing import Literal, Dict, Any, Optional
from packages.framework.chat_model.custom.chat_med_palm import ChatMedPalm
from langchain.chat_models.base import BaseChatModel
from langchain_google_vertexai import ChatVertexAI
from langchain_community.chat_models import ChatOpenAI

from langchain_google_vertexai import HarmBlockThreshold, HarmCategory

# Define Literal for model values
ModelType = Literal[
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    "chat-bison",
    "medlm-large",
    "medlm-medium",
    "gpt-3.5-turbo",
    "gpt-4-turbo",
]


modelToClassMap = {
    "gemini-1.5-flash": ChatVertexAI,
    "gemini-1.5-flash-001": ChatVertexAI,
    "gemini-1.5-flash-002": ChatVertexAI,
    "gemini-1.5-pro": ChatVertexAI,
    "gemini-1.5-pro-001": ChatVertexAI,
    "gemini-1.5-pro-002": ChatVertexAI,
    "gemini-2.0-flash-exp": ChatVertexAI,
    "chat-bison": ChatVertexAI,
    "medlm-large": ChatMedPalm,
    "medlm-medium": ChatMedPalm,
    "gpt-3.5-turbo": ChatOpenAI,
    "gpt-4-turbo": ChatOpenAI,
}


def get_chat_model(
    model_name: ModelType,
    temperature: Optional[float] = 0,
    max_tokens: Optional[int] = None,
    max_retries: Optional[int] = 6,
    stop: Optional[str] = None,
    safety_settings: Optional[Dict[HarmCategory, HarmBlockThreshold]] = {
        HarmCategory.HARM_CATEGORY_UNSPECIFIED: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_CIVIC_INTEGRITY: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.OFF,
        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.OFF,
    },
    **extra_props: Any,
) -> BaseChatModel:
    # Base configuration for all models
    base_config = {
        "temperature": temperature,
        "max_tokens": max_tokens,
        "max_retries": max_retries,
        "stop": stop,
    }

    # Include safety_settings only for Gemini models
    if model_name.startswith("gemini-"):
        base_config["safety_settings"] = safety_settings

    # Merge base_config with extra_props
    full_config = {**base_config, **extra_props}

    ChatClass = modelToClassMap[model_name]

    # Configure the specified model
    return ChatClass(model_name=model_name, **full_config)
