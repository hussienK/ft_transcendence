from django.urls import path
from . import views

urlpatterns = [
    path('join-queue/', views.JoinQueueView.as_view(), name='join_queue'),
    path('join-local/', views.JoinLocalGame.as_view(), name='join_local'),
    path('leave-queue/', views.LeaveQueueView.as_view(), name='leave_queue'),
]
