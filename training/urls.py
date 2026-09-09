from django.urls import path
from . import views

app_name = "training"

urlpatterns = [
    path("", views.program_list, name="program_list"),
    path("programs/<int:pk>/", views.program_detail, name="program_detail"),
    path("workout/<int:pk>/start/", views.start_workout, name="start_workout"),
    path("workout/<int:pk>/", views.workout_player, name="workout_player"),
    path("workout/<int:pk>/complete/", views.complete_workout, name="complete_workout"),
    path("history/", views.history, name="history"),
]
