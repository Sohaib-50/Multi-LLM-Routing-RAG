# api/views.py

from django.http import JsonResponse

def example_view(request):
    data = {
        'message': 'Hello, this is an example view!',
    }
    print(JsonResponse(data))
    return JsonResponse(data)