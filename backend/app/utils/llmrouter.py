from typing import List, Optional
from semantic_router.encoders import OpenAIEncoder
from semantic_router.layer import RouteLayer
from routellm.controller import Controller
from app.enums import LLMName, OptimizationMetric
from semantic_router import Route as SemanticRoute


class LLMRouter:

    def __init__(
        self,
        strong_model_name: LLMName,
        weak_model_name: LLMName,
        semantic_routes: List[SemanticRoute],
    ):
        self.models = {
            "strong": strong_model_name,
            "weak": weak_model_name,
        }
        self.semantic_routes = {route.name: route for route in semantic_routes}

        self.semantic_router_layer = RouteLayer(
            encoder=OpenAIEncoder(), routes=semantic_routes
        )

        self.routellm_controller = Controller(
            routers=["mf"], strong_model=self.models["strong"], weak_model=self.models["weak"]
        )

    def route_query(
        self,
        query: str,
        optimization_factor: Optional[OptimizationMetric] = None,
    ) -> dict:

        # First try to route based on optimization factor
        if optimization_factor is not None:
            if optimization_factor == OptimizationMetric.PERFORMANCE:
                model = LLMName(self.models["strong"])
            else:  # factor is either PRICE or LATENCY
                model = LLMName(self.models["weak"])

            return {
                "query": query,
                "semantic_route": None,
                "model": model,
            }

        # Secondly try to route based on query semantics
        # try to identify query type through semantic-router
        semantic_route = self.semantic_router_layer(query)
        if semantic_route.name is not None:
            return {
                "query": query,
                "semantic_route": semantic_route,
                "model": (
                    self.models["strong"]
                    if semantic_route.name == "greeting"
                    else self.models["weak"]
                ),
            }

        # Lastly, if unable to identify query type, find out whether to use strong or weak model using RouteLLM
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
