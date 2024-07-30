from typing import List, Optional

from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer as SemanticRouteLayer
from routellm.controller import Controller
from litellm import completion

from backend.app.enums import LLMName, LLMType, OptimizationMetric
from backend.app.utils.semantic_route import SemanticRoute


class LLMRouter:

    def __init__(
        self,
        strong_model_name: LLMName,
        weak_model_name: LLMName,
        semantic_routes: Optional[List[SemanticRoute]] = None,
    ):
        if semantic_routes is None:
            semantic_routes = []

        self.models = {
            "strong": strong_model_name,
            "weak": weak_model_name,
        }

        self.semantic_routes = {route.name: route for route in semantic_routes}
        self.semantic_router_layer = SemanticRouteLayer(encoder=OpenAIEncoder(), routes=semantic_routes)

        self.routellm_controller = Controller(routers=["mf"], strong_model=self.models["strong"], weak_model=self.models["weak"])


    def _route_based_on_optimization_metric(self, query: str, optimization_metric: OptimizationMetric) -> dict:
        if optimization_metric == OptimizationMetric.PERFORMANCE:
            model = self.models["strong"]
        else:  # factor is either PRICE or LATENCY
            model = self.models["weak"]

        return {
            "query": query,
            "semantic_route": None,
            "model": model,
        }
    
    def _route_based_on_semantic(self, query: str) -> dict:
        # try to identify query type through semantic-router
        semantic_route_choice = self.semantic_router_layer(query)
        if semantic_route_choice.name is None:
            return {
                "query": query,
                "semantic_route": None,
                "model": self.models["weak"],
            }
        
        semantic_route = self.semantic_routes.get(semantic_route_choice.name)
        if semantic_route.llm_type == LLMType.STRONG:
            model = self.models["strong"]
        else:
            model = self.models["weak"]

        return {
            "query": query,
            "semantic_route": semantic_route,
            "model": model,
        }
    
    def _route_query_based_on_difficulty(self, query: str) -> dict:
        model = self.routellm_controller._get_routed_model_for_completion(
            messages=[{"role": "user", "content": query}],
            
            # matrix factorization model for router, for more options and details see https://github.com/lm-sys/RouteLLM?tab=readme-ov-file#routers
            router="mf",

            # calibrated threshold to route approximately 50% of the queries to the strong model, for more details see https://github.com/lm-sys/RouteLLM?tab=readme-ov-file#threshold-calibration
            threshold=0.11593,  
        )
        model = LLMName(model)

        return {
            "query": query,
            "semantic_route": None,
            "model": model,
        }


    def route_query(
        self,
        query: str,
        optimization_metric: Optional[OptimizationMetric] = None,
    ) -> dict:
        # TODO: add routing decision to return (eg optimization metric, semantic route, or difficulty)

        # First try to route based on optimization factor
        if optimization_metric is not None:
            return self._route_based_on_optimization_metric(query, optimization_metric)

        # Secondly try to route based on query semantics
        if self.semantic_routes and self.semantic_router_layer:
            routing_decision = self._route_based_on_semantic(query)
            if routing_decision["semantic_route"] is not None:
                return routing_decision
            
        # Lastly, if unable to identify query type, find out whether to use strong or weak model using RouteLLM
        return self._route_query_based_on_difficulty(query)
    
    
    def completion(self, *, optimization_metric: Optional[OptimizationMetric] = None, **kwargs):

        query = kwargs.get("messages")[-1]["content"]
        routing_decision = self.route_query(query, optimization_metric)
        model = routing_decision["model"]
        print(f"Model: {model}")    

        return completion(model=model, **kwargs)



if __name__ == '__main__':
    from backend.app.constants import SEMANTIC_ROUTES
    from dotenv import load_dotenv

    load_dotenv()
    llm_router = LLMRouter(strong_model_name=LLMName.GPT_4_O, weak_model_name=LLMName.GPT_3_5_TURBO, semantic_routes=SEMANTIC_ROUTES)
    response = llm_router.completion(messages=[{"role": "user", "content": "Tumhe coding aati hai? Ya nahi? assume that i have classes for 2 different models a weak and small. They are LLMs. And they expose .chat method. I wanna be able to route quries depending on their difficulty. I am confused about the routing logic. Can you help me write full code for it?"}])
    print(response)
    # print(response._hidden_params)


# response = llm_router.completion(messages=[{"role": "user", "content": "Hi whats ur age?"}])