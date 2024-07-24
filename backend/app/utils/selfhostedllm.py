from typing import Any, List, Optional
import json

import aiohttp
from langchain_core.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM




class SelfHostedLLMInferenceClient:
    """
    A client for interfacing with a self-hosted
    Large Language Model (LLM) inference API.

    Attributes:
        base_url (str): The base URL of the LLM inference API.
        api_key (str, optional): The API key for authenticating requests.
        Defaults to None.
    """

    def __init__(self, base_url, api_key=None) -> None:
        """
        Initializes the SelfHostedLLMInferenceClient with
        the given base URL and optional API key.

        Args:
            base_url (str): The base URL of the LLM inference API.
            api_key (str, optional): The API key for authenticating requests.
            Defaults to None.
        """
        self.base_url = base_url

        # TODO: Handle APIKeys logic in future.
        self.api_key = api_key

    def _get_request_headers(self) -> dict:
        """
        Constructs the headers for the API request,
        including the authorization header if an API key is provided.

        Returns:
            dict: A dictionary of headers for the API request.
        """
        headers = {"Content-Type": "application/json"}

        if self.api_key:
            # TODO: Validate APIKey and then send it in Authorization headers.
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers

    async def generate_text(
        self, prompt: str, temperature: float, model_name: str
    ):
        """
        Sends a request to the Self-hosted LLM API to generate
        non-streaming text based on the given prompt.

        Args:
            prompt (str): The text prompt to send to the LLM API.

        Returns:
            str: The generated non-streaming text response from the LLM API.

        Raises:
            requests.exceptions.HTTPError: If the API request fails.
        """

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
    """
    A wrapper class for integrating a self-hosted LLM inference client with the LangChain LLM base class.
    Guide to override LLM: https://python.langchain.com/v0.1/docs/modules/model_io/llms/custom_llm/

    Attributes:
        streaming: Whether to stream the results or not.
        inference_client (SelfHostedLLMInferenceClient): The client used to interact with the self-hosted LLM API.
        temperature: LLM temperature for generation. defaults to 0.7.
        model_name: LLM name.


    """

    streaming: bool = False
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
        """
        Calls the self-hosted LLM API to generate a text response based on the given prompt.

        Args:
            prompt (str): The text prompt to send to the LLM API.
            stop (Optional[List[str]]): A list of stop sequences where the LLM should stop generating further tokens. Defaults to None.

        Returns:
            str: The generated text response from the LLM API.
        """
        return self.inference_client.generate_text(
                prompt=prompt,
                temperature=self.temperature,
                model_name=self.model_name,
            )

