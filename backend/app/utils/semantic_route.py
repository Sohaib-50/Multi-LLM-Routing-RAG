from typing import Optional
from semantic_router import Route

class SemanticRoute(Route):
    llm_type: Optional[str] = None

    def __str__(self):
        if self.llm_type:
            return f"{self.name} (LLM Type: {self.llm_type})"
        else:
            return self.name