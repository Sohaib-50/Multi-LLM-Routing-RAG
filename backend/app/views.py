
from django.http import JsonResponse
from django.db import transaction

from app.models import Chat, Message
from app.utils.train import create_index
from app.utils.chat import create_index, get_ai_response
from backend.app.enums import OptimizationMetric

def example_view(request):
    return JsonResponse({"message": "Hello, World!"})


def get_chat(request, chat_id):
    '''
    Retrieve a chat and its messages with detailed information
    '''

    chat = Chat.objects.get(id=chat_id)

    # get all messages in the chat and related information
    messages = [
        {
            "content": message.content,
            "role": message.role,
            "model_used": message.model_used,
            "predicted_semantic": message.predicted_semantic,
            "sent_at": message.sent_at,
        }
        for message in chat.messages.all()
    ]

    return JsonResponse({"chat": chat.name, "messages": messages})


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
    '''

    '''

    # check if text is provided
    if not (text := request.POST.get("text").strip()):
        return JsonResponse({"error": "No text provided"}, status=400)
    
    # attempt to create chat and index
    try:
        with transaction.atomic():
                chat = Chat.objects.create()
                create_index(text, chat.id)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
    
    return get_chat(request, chat.id)
    


# route which gets chat id and user message, gets ai response does other necessary things and returns the response
def ai_response(request):
    
    chat_id = request.POST.get("chat_id")
    try:
        chat_id = int(chat_id)
    except ValueError:
        return JsonResponse({"error": "Invalid Chat ID"}, status=400)

    chat = Chat.objects.get(id=chat_id)

    message = request.POST.get("message")
    optimization_metric = OptimizationMetric[request.POST.get("optimization_metric")]  # TODO: dropdown

    get_ai_response(message=message, chat_id=chat_id, optimization_metric=optimization_metric)

    








"""
Your existing views look quite functional but could benefit from some improvements and additional checks. Here are a few suggestions for your current views:

Error Handling:

Your get_chat view should handle cases where the Chat with the given chat_id doesn't exist. Use get_object_or_404 instead of get to automatically handle this scenario.
In get_chats, consider handling empty querysets gracefully, though this is not critical.
Performance Considerations:

If you have many messages or chats, you might want to use pagination to avoid performance issues with large data sets.
Data Security:

Make sure to sanitize or validate the input to avoid security issues, especially in views that handle user input.
Here's how you might adjust your current views with these considerations:

python
Copy code
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from app.models import Chat, Message
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET"])
def get_chat(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    messages = [
        {
            "content": message.content,
            "role": message.role,
            "model_used": message.model_used,
            "predicted_semantic": message.predicted_semantic,
            "sent_at": message.sent_at,
        }
        for message in chat.messages.all()
    ]
    return JsonResponse({"chat": chat.name, "messages": messages})

@require_http_methods(["GET"])
def get_chats(request):
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

@require_http_methods(["POST"])
def create_chat(request):
    chat = Chat.objects.create()
    return JsonResponse({"chat_id": chat.id})
New View for Chat Interaction
To handle user input and generate AI responses, here's a view outline:

Receive user message.
Generate a mock AI response.
Save both the user message and AI response to the database.
Return the AI response to the user.
Here's a basic implementation:

python
Copy code
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from app.models import Chat, Message

@require_http_methods(["POST"])
def chat_with_ai(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    
    try:
        content = request.POST['content']
    except KeyError:
        return JsonResponse({"error": "Content is required"}, status=400)
    
    # Save the user's message
    user_message = Message.objects.create(
        content=content,
        role='user',
        chat=chat,
        model_used='None',  # No model used for user's input
    )
    
    # Mock AI response (replace this with actual AI interaction)
    ai_response_content = "This is a mock AI response."
    
    # Save the AI's response
    ai_message = Message.objects.create(
        content=ai_response_content,
        role='ai',
        chat=chat,
        model_used='MockAI',  # Mock model name
    )
    
    return JsonResponse({
        "user_message": user_message.content,
        "ai_response": ai_message.content,
    })
Notes:
Input Handling: Ensure you validate and sanitize inputs. For a production app, use Django forms or serializers for robust input validation.
AI Integration: Replace the mock AI response with actual logic to interact with an AI service or model.
Authentication: Consider adding authentication and authorization to secure these endpoints if needed.




"""