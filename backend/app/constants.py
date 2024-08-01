from app.utils.semantic_route import SemanticRoute
from app.enums import LLMType, LLMName


SEMANTIC_ROUTES = [
    SemanticRoute(
        name="greeting",
        llm_type=LLMType.WEAK,
        utterances=[
            "Hi",
            "Hello",
            "Hey",
            "Hola",
            "Bonjour",
            "Konnichiwa",
            "Salam",
            "Ciao",
        ],
    ),
    SemanticRoute(
        name="multi_lingual",
        llm_type=LLMType.STRONG,
        utterances=[
            "kiya programming seekhna easy hai?",
            "mujhe HR policies ki details explain karo",
            "Can you tell me about the 'Parlez-vous anglais?'",
            "¿Dónde está el 'supermercado'?",
            "我想知道 'weather' 的中文是什么?",
        ],
    ),
]

STRONG_MODEL_NAME = LLMName.GPT_4_O
WEAK_MODEL_NAME = LLMName.GPT_3_5_TURBO




