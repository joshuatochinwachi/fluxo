
from __future__ import annotations
import os
import time
import requests
from typing import Dict, Optional
from core.config import Settings

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_API_URL = os.getenv("OPENAI_API_URL", "https://api.openai.com/v1")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
ANTHROPIC_API_URL = os.getenv("ANTHROPIC_API_URL", "https://api.anthropic.com")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class LLMError(Exception):
    pass


class LLMClient:
    def __init__(self, openai_api_key: Optional[str] = None, anthropic_api_key: Optional[str] = None):
        self.openai_api_key = openai_api_key or OPENAI_API_KEY
        self.anthropic_api_key = anthropic_api_key or ANTHROPIC_API_KEY
        self.settings = Settings()

    def call_openai(self, prompt: str, model: str = "gpt-4o-mini", max_tokens: int = 512) -> Dict:
        """Call OpenAI Chat Completions endpoint (simple prototype).

        Returns the raw JSON response.
        """
        if not self.openai_api_key:
            raise LLMError("OPENAI_API_KEY is not set")

        url = f"{OPENAI_API_URL}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
        }
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        try:
            resp.raise_for_status()
        except Exception as e:
            raise LLMError(f"OpenAI request failed: {e} - {resp.text}")
        return resp.json()

    def call_claude(self, prompt: str, model: str = "claude-2.1", max_tokens: int = 500) -> Dict:
        """Call Anthropic Claude complete endpoint (prototype).

        Anthropic accepts either `Authorization: Bearer <key>` or `x-api-key` depending on contract.
        This prototype uses Bearer.
        """
        if not self.anthropic_api_key:
            raise LLMError("ANTHROPIC_API_KEY is not set")

        url = f"{ANTHROPIC_API_URL}/v1/complete"
        headers = {
            "Authorization": f"Bearer {self.anthropic_api_key}",
            "Content-Type": "application/json",
        }
        # Anthropic expects a `prompt` that includes an instruction + user text; this is a simple example
        body = {
            "model": model,
            "prompt": prompt,
            "max_tokens_to_sample": max_tokens,
            "temperature": 0.2,
        }
        resp = requests.post(url, headers=headers, json=body, timeout=30)
        try:
            resp.raise_for_status()
        except Exception as e:
            raise LLMError(f"Anthropic request failed: {e} - {resp.text}")
        return resp.json()

    
    
    def Call_gemini(self, prompt: str, model: str = "gemini-2.5-flash"):
        try:
            headers = {
                "x-goog-api-key": self.settings.gemini_api_key,
                "Content-Type": "application/json"
            }

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"text": str(prompt)}
                        ]
                    }
                ]
            }

            GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            time.sleep(3)
            response = requests.post(url=GEMINI_URL, json=payload, headers=headers)
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                text = text.split('json')[1].strip('```')
                return text
            else:
                print("Error In Gemini Ai:", response.status_code)
                return None

        except Exception as e:
            return None




    