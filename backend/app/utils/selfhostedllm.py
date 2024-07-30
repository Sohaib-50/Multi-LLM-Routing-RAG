from typing import Any, List, Optional
import json

import aiohttp
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM



class SelfHostedLLMInferenceClient:

    def __init__(self, base_url, api_key=None) -> None:
        self.base_url = base_url


    def _get_request_headers(self) -> dict:
        headers = {"Content-Type": "application/json"}
        return headers


    async def generate_text(
        self, prompt: str, temperature: float, model_name: str
    ):
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": model_name,
            "messages": [{"role": "user", "content": prompt}],
            "options": {"temperature": temperature},
            "stream": False,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, json=payload, headers=self._get_request_headers()
            ) as response:
                if response.status == 200:
                    json_response = await response.json()
                    return json_response.get("message", {}).get("content", "")
                else:
                    response.raise_for_status()



class LLMWrapper(LLM):

    inference_client: SelfHostedLLMInferenceClient = (
        SelfHostedLLMInferenceClient(base_url="https://llm.chatwards.ai")
    )
    temperature: float = 0.7
    model_name: str

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ):
        return self.inference_client.generate_text(
                prompt=prompt,
                temperature=self.temperature,
                model_name=self.model_name,
            )

