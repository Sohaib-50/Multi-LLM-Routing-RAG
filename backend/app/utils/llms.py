import random
from typing import Optional
from app.enums import LLMName


class LLM:
    def __init__(self, name: str, api_base: Optional[str] = None, api_key: Optional[str] = None, provider: Optional[str] = None):
          
        if name not in [model.value for model in LLMName]:
            raise ValueError(f"Invalid LLM name: {name}")
        
        self.name = name
        self.api_base = api_base
        self.api_key = api_key
        
        if provider:
            self.model = f'{provider}/{name}'
        else:
            self.model = name

    def __str__(self):
        return self.name

    @property
    def tokens_per_second(self):
        '''
        Simulates the number of tokens per second the LLM can process.
        TODO: replace with logic to get actual TPS from the model.
        '''
        min_tps = 20
        max_tps = 500
        return round(random.uniform(min_tps, max_tps), 2)
    

LLMs = {
    LLMName.GPT_3_5_TURBO: LLM(name=LLMName.GPT_3_5_TURBO.value),
    LLMName.GPT_4: LLM(name=LLMName.GPT_4.value),
    LLMName.GPT_4_O: LLM(name=LLMName.GPT_4_O.value),
    LLMName.LLAMA3_8B: LLM(name=LLMName.LLAMA3_8B.value, api_base='https://llm.chatwards.ai/', api_key='ollama', provider='ollama'),
}