import json
import random
from typing import Optional

from django.db import models
from app.enums import Role, LLMName


class Chat(models.Model):
    name = models.CharField(max_length=255, blank=True, null=True)
    started_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Chat {self.id} - {self.name if self.name else 'Untitled'}"

    def add_message(self, content: str, role: str, model_used: Optional[str] = None,
                    predicted_semantic: Optional[str] = None, metadata: Optional[dict] = None):
        message = Message.objects.create(
            content=content,
            role=role,
            model_used=model_used,
            predicted_semantic=predicted_semantic,
            chat=self,
            metadata=metadata or {},
        )
        return message
    
    def get_messages(self, k_recent: Optional[int] = None):
        if k_recent is not None:
            return self.messages.order_by("-sent_at")[:k_recent][::-1]
        else:
            return self.messages.all().order_by("sent_at")

    
class Message(models.Model):
    content = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)
    role = models.CharField(max_length=20, choices=[(role.value, role.name) for role in Role])
    model_used = models.CharField(max_length=255, choices=[(model.value, model.name) for model in LLMName], blank=True, null=True)  # only for AI messages
    predicted_semantic = models.CharField(max_length=50, blank=True, null=True)  # only for user messages where semantic was predicted
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    metadata = models.JSONField(default=dict)  

    def __str__(self):
        return json.dumps({
                "role": self.role,
                "content": self.content,
            },
            ensure_ascii=False,
        )
    
    def serialize(self):
        return {
            "id": self.id,
            "chat_id": self.chat_id,
            "role": self.role,
            "content": self.content,
            "sent_at": self.sent_at.isoformat(),
            "model_used": self.model_used,
            "predicted_semantic": self.predicted_semantic,
            "metadata": self.metadata,
        }
    
# class LLM(models.Model):
#     name = models.CharField(max_length=255, choices=[(model.value, model.name) for model in LLMName], primary_key=True)

#     def __str__(self):
#         return f"{self.name} - {self.model_name}"
    
#     @property
#     def tokens_per_second(self):
#         '''
#         Simulates the number of tokens per second the LLM can process.
#         '''
#         min_tps = 20
#         max_tps = 500
#         return round(random.uniform(min_tps, max_tps), 2)

