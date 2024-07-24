from enum import Enum

class LLMName(str, Enum):
    GPT_3_5_TURBO = "GPT_3.5_TURBO_1106"
    GPT_4= "gpt-4-1106-preview"
    GPT_4_O = "gpt-4o-2024-05-13"
    LAMA3_8B = "llama3:8b-instruct-q8_0"


class OptimizationMetric(str, Enum):
    PRICE = "price"
    LATENCY = "latency"
    PERFORMANCE = "performance"