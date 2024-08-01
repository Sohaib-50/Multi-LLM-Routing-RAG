import random
from app.enums import LLMName


class LLM:
    def __init__(self, name: str):
        # TODO: add more fields like api base, api key, etc.
        
        if name not in [model.value for model in LLMName]:
            raise ValueError(f"Invalid LLM name: {name}")
        self.name = name

    def __str__(self):
        return f"{self.name} - {self.name}"

    @property
    def tokens_per_second(self):
        '''
        Simulates the number of tokens per second the LLM can process.
        TODO: replace with logic to get actual TPS from the model.
        '''
        min_tps = 20
        max_tps = 500
        return round(random.uniform(min_tps, max_tps), 2)
    

llms = {model.value: LLM(model.value) for model in LLMName}


