from enum import Enum

class LLMType(str, Enum):
    STRONG = "strong"
    WEAK = "weak"

class LLMName(str, Enum):
    GPT_3_5_TURBO = "gpt-3.5-turbo"
    GPT_4= "gpt-4-1106-preview"
    GPT_4_O = "gpt-4o-2024-05-13"
    LAMA3_8B = "llama3:8b-instruct-q8_0"


class OptimizationMetric(str, Enum):
    PRICE = "price"
    LATENCY = "latency"
    PERFORMANCE = "performance"


class Role(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"



print([(role.value, role.name) for role in Role])
