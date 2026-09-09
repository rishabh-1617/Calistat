from django.urls import path
from . import views

app_name = "ranking"

urlpatterns = [
    path("", views.leaderboard, name="leaderboard"),
    path("analytics/", views.analytics_dashboard, name="analytics_dashboard"),
]
