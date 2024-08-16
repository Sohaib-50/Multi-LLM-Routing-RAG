
from openai import OpenAI
from app.utils.llms import LLMs
from app.enums import OptimizationMetric, LLMName
from app.constants import SEMANTIC_ROUTES


def chat(query, optimization_metric=None):

    # setup custom parameters
    strong_model = LLMs[LLMName.GPT_4_O.value]
    weak_model = LLMs[LLMName.LLAMA3_8B.value]
    models = {
        "strong": {
            "model": strong_model.model,
            # "api_key": strong_model.api_key,
            # "api_base": strong_model.api_base,
        },
        "weak": {
            "model": weak_model.model,
            "api_key": weak_model.api_key,
            "api_base": weak_model.api_base,
        }
    }

    semantics = [
        {
            "name": semantic.name,
            "model_type": semantic.llm_type,
            "utterances": semantic.utterances,
        }
        for semantic in SEMANTIC_ROUTES
    ]

    api_base = "http://localhost:8000/api/"

    client = OpenAI(base_url=api_base)
    response = client.chat.completions.create(
        model="doesntmatter",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query},
        ],
        extra_body={
            "models": models,
            "optimization_metric": optimization_metric,
            "semantics": semantics,
        }
    )

    print(f"-> Response:\n{response}\n")
    print(f"-> Routing decision:\n{response.routing_decision}\n")
    print(f"-> response.choices[0].message.content:\n{response.choices[0].message.content}")



if __name__ == "__main__":
    # query = """Tell the authenticity of the reply to following question
    # Question:
    # 'how many subs allowd in footbal?'
    
    # Reply: 
    # 'According to the official rules of football (soccer), each team is allowed to have 12 outfield players, including defenders, midfielders, and forwards. Additionally, each team has:

    # * 1 goalkeeper
    # * 7 substitutes on the bench

    # So, in total, a team can have up to 11 players on the field at any given time, with 7 additional players who can substitute in during the game.'

    # Authenticity:
    # """
    query = input("Enter your query: ")


    # show menu for optimization metric
    optimization_metrics = [metric.value for metric in OptimizationMetric]
    print("\nChoose an optimization metric:")
    for i, metric in enumerate(optimization_metrics):
        print(f"{i+1}. {metric}")
    optimization_metric = input(f"Enter your choice (1-{len(optimization_metrics)}, anythign else to skip): ")
    try:
        if int(optimization_metric) > 0:
            optimization_metric = OptimizationMetric(optimization_metrics[int(optimization_metric)-1])
            print(f"{optimization_metric} selected.")
        else:
            raise ValueError
    except:
        optimization_metric = None
        print("No optimization metric selected")
    
    print("\n-> Getting response...\n")
    chat(query, optimization_metric)

