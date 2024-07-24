from semantic_router import Route

class SemanticRoute(Route):
    def __init__(self, name, utterances):
        super().__init__(name=name, utterances=utterances)