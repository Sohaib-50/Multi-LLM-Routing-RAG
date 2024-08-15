import json
import logging

from django.http import JsonResponse
from django.db import transaction
from django.views.decorators.csrf import csrf_exempt


from app.models import Chat
from app.utils.chat import get_models, update_models, create_index, get_ai_response
from app.utils.llms import LLMs
from app.enums import OptimizationMetric, LLMName
from app.utils.llmrouter import LLMRouter
from .forms import ChatCompletionExtraBodyForm

# Initial setup
logger = logging.getLogger(__name__)
update_models()  # set default models


def example_view(request):
    return JsonResponse({"message": "Hello, World!"})


def all_models(request):
    return JsonResponse({"models": [model.value for model in LLMName]})


def models_info(request):
    if request.method == "PUT":

        # get and validate model names
        try:
            request_data = json.loads(request.body)

            strong_model_name = LLMName(request_data.get("strong_model_name"))
            weak_model_name = LLMName(request_data.get("weak_model_name"))
            
            if strong_model_name == weak_model_name:
                raise ValueError("Strong and weak models cannot be the same")
            
            # update models
            update_models(strong_model_name=strong_model_name, weak_model_name=weak_model_name)
            
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            return JsonResponse({"error": f"Invalid model name(s) provided. Error: {e}"}, status=400) 
    
    return JsonResponse(get_models())


def get_chat(request, chat_id):
    '''
    Retrieve a chat and its messages with detailed information
    '''
    try:
        chat_id = int(chat_id)
        chat = Chat.objects.get(id=chat_id)
    except (ValueError, Chat.DoesNotExist):
        return JsonResponse({"error": "Invalid chat_id provided"}, status=400)

    # get all messages in the chat and related information
    messages = [
        {
            "content": message.content,
            "role": message.role,
            "model_used": message.model_used,
            "predicted_semantic": message.predicted_semantic,
            "metadata": message.metadata,
            "sent_at": message.sent_at,
        }
        for message in chat.get_messages()
    ]

    return JsonResponse({"name": f"{chat.id} - {chat.name}", "messages": messages})


def get_chats(request):
    '''
    Retrieve all chats with basic info
    '''

    chats = [
        {
            "id": chat.id,
            "name": chat.name,
            "started_at": chat.started_at,
            "last_message": chat.messages.last().content[:50] if chat.messages.last() else "",
        }
        for chat in Chat.objects.all()
    ]
    return JsonResponse({"chats": chats})


def create_chat(request):
    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    print(f"Received create chat request: {str(request.POST)[:500]}...", flush=True)
    print("Debug message for troubleshooting")

    # check if text is provided
    if not (knowledgebase := request.POST.get("knowledgebase")):
        return JsonResponse({"error": "No knowledgebase provided"}, status=400)
        
    # attempt to create chat and index
    try:
        with transaction.atomic():
            chat = Chat.objects.create(name=request.POST.get("name"))
            create_index(knowledgebase.strip(), chat.id)
    except Exception as e:
        print(f"Error creating chat: {e}", flush=True)
        return JsonResponse({"error": str(e)}, status=500)
    
    print(f"Chat created successfully: {chat.id}", flush=True)
    return JsonResponse({"chat_id": chat.id, "message": "Chat created successfully"})


def ai_response(request, chat_id):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)

        
    try:
        chat_id = int(chat_id)
        Chat.objects.get(id=chat_id)
    except (ValueError, Chat.DoesNotExist):
        return JsonResponse({"error": "Invalid chat_id provided"}, status=400)

    query = request.POST.get("query")

    # check if optimization metric is provided and valid
    if (optimization_metric := request.POST.get("optimization_metric")) in OptimizationMetric:
        optimization_metric = OptimizationMetric(optimization_metric)  # enumerate
        
    ai_response_data = get_ai_response(query=query, chat_id=chat_id, optimization_metric=optimization_metric)

    return JsonResponse(ai_response_data)



@csrf_exempt
def chat_completions(request):
    '''
    Mimics OpenAI's completion endpoint for chat completions

    Parameters:
        - `model` (str): A placeholder for the model name, pass any string, this isn't used, just needed bec its part of OpenAI's API.
        - `messages` (list of dicts): A list of message objects that make up the conversation history, exactly like OpenAI's format. Each message object should contain:
            - `role` (str): The role of the sender: 'system', 'user', or 'assistant'.
            - `content` (str): The content of the message.
        - `extra_body` (dict): Additional parameters for processing the completion request For our implementation, this should include:
            - `models` (dict): A dictionary with two keys, 'strong' and 'weak', each representing model configurations. Each model configuration should include:
                - `model` (str): The model identifier in the format '<provider>/<model_name>', where '<provider>/' is optional and defaults to 'openai'.
                - `api_key` (str, optional): The API key for accessing the model, if required, defaults to OPENAI_API_KEY environment variable.
                - `api_base` (str, optional): The base URL for the model API, defaults to OpenAI's API base URL.
            - `optimization_metric` (str, optional): Prefered metric to be optimized.
            - `semantics` (list of dicts, optional): A list of semantic route definitions. Each semantic route object should contain:
                - `name` (str): The name of the semantic route.
                - `model_type` (str): The type of the model, either 'weak' or 'strong'.
                - `utterances` (list of str): A list of example utterances for the route.
    '''
    # TODO: make this route exactly as per OpenAI specs

    if request.method != "POST":
        # TODO: make this response exactly as per specs
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)


    kwargs = json.loads(request.body)

    # extra_body_form = ChatCompletionExtraBodyForm(kwargs)
    # if not extra_body_form.is_valid():
    #     return JsonResponse({"error": extra_body_form.errors}, status=400)
    
    # print(f"Extra body form: {extra_body_form.cleaned_data}", flush=True)
    # print(extra_body_form.cleaned_data.keys(), flush=True)

    # # TODO: technical debt, fix this
    # strong_model = kwargs["models"]["strong"]
    # strong_model_model = strong_model["model"]
    # strong_model_model_split = strong_model_model.split("/")
    # strong_model_name = strong_model_model_split[-1]
    # if len(strong_model_model_split) == 2:
    #     strong_model_provider = strong_model_model_split[0]
    # else:
    #     strong_model_provider = None
    # kwargs["models"]["strong"].update({
    #     "name": strong_model_name,
    #     "provider": strong_model_provider,
    # })
    # weak_model = kwargs["models"]["weak"]
    # weak_model_model = weak_model["model"]
    # weak_model_model_split = weak_model_model.split("/")
    # weak_model_name = weak_model_model_split[-1]
    # if len(weak_model_model_split) == 2:
    #     weak_model_provider = weak_model_model_split[0]
    # else:
    #     weak_model_provider = None
    # kwargs["models"]["weak"].update({
    #     "name": weak_model_name,
    #     "provider": weak_model_provider,
    # })

    if kwargs.get("optimization_metric"):
        kwargs["optimization_metric"] = OptimizationMetric(kwargs["optimization_metric"])

    response = LLMRouter.completion(**kwargs)

    metadata = response["_hidden_params"]
    routing_decision = metadata["routing_decision"]
    response = response.json()
    response["metadata"] = metadata
    response["routing_decision"] = routing_decision

    return JsonResponse(response)
