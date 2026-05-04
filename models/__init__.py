import os
from .base import BaseClassifier
from .openrouter import OpenRouterClassifier
from .azure_openai import AzureOpenAIClassifier
from .gemini import GeminiClassifier


def get_classifier() -> BaseClassifier:
    provider = os.environ.get("MODEL_PROVIDER", "openrouter")

    if provider == "azure":
        return AzureOpenAIClassifier(
            endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            api_key=os.environ["AZURE_OPENAI_API_KEY"],
            deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            key_senders=os.environ["KEY_SENDERS"],
            excluded_topics=os.environ["EXCLUDED_TOPICS"],
        )

    if provider == "gemini":
        return GeminiClassifier(
            api_key=os.environ["GEMINI_API_KEY"],
            model=os.environ.get("MODEL", "gemini-flash-latest"),
            key_senders=os.environ["KEY_SENDERS"],
            excluded_topics=os.environ["EXCLUDED_TOPICS"],
        )

    return OpenRouterClassifier(
        api_key=os.environ["OPENROUTER_API_KEY"],
        model=os.environ.get("MODEL", "google/gemma-3-27b-it:free"),
        key_senders=os.environ["KEY_SENDERS"],
        excluded_topics=os.environ["EXCLUDED_TOPICS"],
    )
