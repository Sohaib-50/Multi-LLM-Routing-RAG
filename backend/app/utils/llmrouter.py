from dataclasses import dataclass
from typing import List, Optional

from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer as SemanticRouteLayer
from routellm.controller import Controller
from litellm import completion

from app.enums import LLMName, LLMType, OptimizationMetric
from app.utils.semantic_route import SemanticRoute


@dataclass
class RoutingDecision:
    query: str
    model: LLMName
    model_type: LLMType
    predicted_semantic: Optional[str] = None
    optimization_metric: Optional[OptimizationMetric] = None

    def to_dict(self):
        return {
            "query": self.query,
            "predicted_semantic": self.predicted_semantic,
            "model": self.model,
            "model_type": self.model_type,
            "optimization_metric": self.optimization_metric,
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            query=data["query"],
            predicted_semantic=data.get("predicted_semantic"),
            model=data["model"],
            model_type=data["model_type"],
            optimization_metric=data.get("optimization_metric"),
        )
class LLMRouter:

    def __init__(
        self,
        strong_model: LLMName,
        weak_model: LLMName,
        semantic_routes: Optional[List[SemanticRoute]] = None,
    ):
        if semantic_routes is None:
            semantic_routes = []

        self.models = {
            "strong": strong_model,
            "weak": weak_model,
        }

        self.semantic_routes = {route.name: route for route in semantic_routes}
        self.semantic_router_layer = SemanticRouteLayer(encoder=OpenAIEncoder(), routes=semantic_routes)

        self.routellm_controller = Controller(routers=["mf"], strong_model=self.models["strong"], weak_model=self.models["weak"])


    def _route_based_on_optimization_metric(self, query: str, optimization_metric: OptimizationMetric) -> dict:
        if optimization_metric == OptimizationMetric.PERFORMANCE:
            model_type = LLMType.STRONG
        else:  # factor is either PRICE or LATENCY
            model_type = LLMType.WEAK

        return {
            "query": query,
            "predicted_semantic": None,
            "model": self.models[model_type],
            "model_type": model_type,
            "optimization_metric": optimization_metric,
            "based_on": f"optimization_metric: {optimization_metric}",
        }
    
    def _route_based_on_semantic(self, query: str) -> dict:
        
        # try to identify query type through semantic-router
        semantic_route_choice = self.semantic_router_layer(query)
        if semantic_route_choice.name is None:
            return {
                "query": query,
                "predicted_semantic": None,
                "model": None,
                "model_type": None,
                "optimization_metric": None,
                "based_on": None,
            }
        
        semantic_route = self.semantic_routes.get(semantic_route_choice.name)
        model_type = semantic_route.llm_type

        return {
            "query": query,
            "predicted_semantic": semantic_route.name,
            "model": self.models[model_type],
            "model_type": model_type,
            "optimization_metric": None,
            "based_on": f"Semantic: {semantic_route.name}",
        }
    
    def _route_query_based_on_difficulty(self, query: str) -> dict:
        model = self.routellm_controller._get_routed_model_for_completion(
            messages=[{"role": "user", "content": query}],
            
            # matrix factorization model for router, for more options and details see https://github.com/lm-sys/RouteLLM?tab=readme-ov-file#routers
            router="mf",

            # calibrated threshold to route approximately 50% of the queries to the strong model, for more details see https://github.com/lm-sys/RouteLLM?tab=readme-ov-file#threshold-calibration
            threshold=0.11593,  
        )

        return {
            "query": query,
            "predicted_semantic": None,
            "model": model,
            "model_type": LLMType.STRONG if model == self.models["strong"] else LLMType.WEAK,
            "optimization_metric": None,
            "based_on": "difficulty",
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
            if routing_decision["predicted_semantic"] is not None:
                return routing_decision
            
        # Lastly, if unable to identify query type, find out whether to use strong or weak model using RouteLLM
        return self._route_query_based_on_difficulty(query)
    
    
    def completion(self, *, optimization_metric: Optional[OptimizationMetric] = None, **kwargs):

        query = kwargs.get("messages")[-1]["content"]
        routing_decision = self.route_query(query, optimization_metric)
        
        model = routing_decision["model"]
        print(f"Routed Model: {model}")    

        response = completion(model=model, **kwargs)
        response["_hidden_params"]["routing_decision"] = routing_decision
        return response


if __name__ == '__main__':
    from app.constants import SEMANTIC_ROUTES
    from dotenv import load_dotenv

    load_dotenv()
    llm_router = LLMRouter(strong_model=LLMName.GPT_4_O, weak_model=LLMName.GPT_3_5_TURBO, semantic_routes=SEMANTIC_ROUTES)
    response = llm_router.completion(messages=[{"role": "user", "content": "Tumhe coding aati hai? Ya nahi? assume that i have classes for 2 different models a weak and small. They are LLMs. And they expose .chat method. I wanna be able to route quries depending on their difficulty. I am confused about the routing logic. Can you help me write full code for it?"}])
    print(response)
    # print(response._hidden_params)


# response = llm_router.completion(messages=[{"role": "user", "content": "Hi whats ur age?"}])