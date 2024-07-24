import json
from django.db import models
from app.enums import Role, LLMName


class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True)
    started_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat {self.id} - {self.name if self.name else 'Untitled'}"

    def add_message(self, content: str, role: str, model_used: str, predicted_semantic: str = ""):
        message = Message.objects.create(
            content=content,
            role=role,
            model_used=model_used,
            predicted_semantic=predicted_semantic,
            chat=self,
        )
        return message

class Message(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=[(role.value, role.name) for role in Role])
    model_used = models.CharField(max_length=255, choices=[(model.value, model.name) for model in LLMName])
    predicted_semantic = models.CharField(max_length=50, blank=True)
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")

    def __str__(self):
        return json.dumps({
                "role": self.role,
                "content": self.content,
            },
            ensure_ascii=False,
        )
