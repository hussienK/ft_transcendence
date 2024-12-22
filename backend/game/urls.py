from django.urls import path
from . import views

urlpatterns = [
    path('join-queue/', views.JoinQueueView.as_view(), name='join_queue'),
    path('join-local/', views.JoinLocalGame.as_view(), name='join_local'),
    path('leave-queue/', views.LeaveQueueView.as_view(), name='leave_queue'),
    path("tournament/create/", views.CreateTournamentView.as_view(), name="create_tournament"),
    path("tournament/<str:tournament_id>/register/",views. RegisterAliasView.as_view(), name="register_alias"),
    path("tournament/<str:tournament_id>/start/", views.StartTournamentView.as_view(), name="start_tournament"),
    path("tournament/<str:tournament_id>/match/<str:match_index>/save_result/", views.SaveMatchResultView.as_view(), name="save_match_result"),
]
