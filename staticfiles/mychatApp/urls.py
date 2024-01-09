from django.urls import path
from .views import chatbot

app_name = 'mychatApp'
urlpatterns = [
    path('', chatbot, name='home'),
    path('chatbot', chatbot, name='chatbot'),
]