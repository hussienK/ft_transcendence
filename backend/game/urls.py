from django.urls import path
from . import views

urlpatterns = [
    path('join-queue/', views.JoinQueueView.as_view(), name='join_queue'),
    # Add more API endpoints as needed
]
