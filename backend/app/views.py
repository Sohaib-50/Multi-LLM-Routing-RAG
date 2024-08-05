import json
import logging
import os

from django.http import JsonResponse
from django.db import transaction

from app.models import Chat, Message
from app.utils.chat import get_models, update_models, create_index, get_ai_response
from app.utils.llms import LLMs
from app.enums import OptimizationMetric, LLMName

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
            
        except (KeyError, ValueError, json.JSONDecodeError) as e:
            return JsonResponse({"error": f"Invalid model name(s) provided. Error: {e}"}, status=400) 

        update_models(strong_model_name=strong_model_name, weak_model_name=weak_model_name)
    
    return JsonResponse(get_models())
    

def get_chat(request, chat_id):
    '''
    Retrieve a chat and its messages with detailed information
    '''

    # # mock response
    # return JsonResponse({
    #     "name": "Chat 1",
    #     "messages": [
    #         {
    #             "content": "Hello, World!",
    #             "role": "user",
    #             "model_used": None,
    #             "predicted_semantic": None,
    #             "sent_at": "2021-09-01T00:00:00Z",
    #         },
    #         {
    #             "content": "This is a mock response from the AI model.",
    #             "role": "ai",
    #             "model_used": "GPT-3",
    #             "predicted_semantic": "greeting",
    #             "sent_at": "2021-09-01T00:00:00Z",
    #         },
    #     ]
    # })

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

    # # mock
    # chats = [
    #     {
    #         "id": 1,
    #         "name": "Chat 1",
    #         "started_at": "2021-09-01T00:00:00Z",
    #         "last_message": "Hello, World!",
    #     },
    #     {
    #         "id": 2,
    #         "name": "Chat 2",
    #         "started_at": "2021-09-01T00:00:00Z",
    #         "last_message": "Hello, World!",
    #     },
    #     {
    #         "id": 3,
    #         "name": "Chat 3",
    #         "started_at": "2021-09-01T00:00:00Z",
    #         "last_message": "Hello, World!",
    #     },
    # ]
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
    


# route which gets chat id and user message, gets ai response does other necessary things and returns the response
# path('chat/<int:chat_id>/get_ai_response/', views.get_ai_response, name='get_ai_response'),
def ai_response(request, chat_id):

    if request.method != "POST":
        return JsonResponse({"error": "Only POST requests are allowed"}, status=405)
    
    # else:
    #     print(f"Received AI response request: {str(request.POST)[:500]}...", flush=True)
    #     # mock response
    #     query = request.POST.get("query")
    #     return JsonResponse({
    #         "query": query,
    #         "response": "This is a mock response from the AI model."
    #     })
        
    try:
        chat_id = int(chat_id)
        Chat.objects.get(id=chat_id)
    except (ValueError, Chat.DoesNotExist):
        return JsonResponse({"error": "Invalid chat_id provided"}, status=400)

    query = request.POST.get("query")
    # return JsonResponse({
    #         "query": query,
    #         "response": f"This is a mock response from the AI model for chat {chat_id} with query: {query}"
    #     })

    # check if optimization metric is provided and valid
    if (optimization_metric := request.POST.get("optimization_metric")) in OptimizationMetric:
        optimization_metric = OptimizationMetric(optimization_metric)  # enumerate
        
    ai_response_data = get_ai_response(query=query, chat_id=chat_id, optimization_metric=optimization_metric)

    return JsonResponse(ai_response_data)

    
    