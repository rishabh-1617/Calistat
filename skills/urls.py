from django.urls import path
from . import views

app_name = "skills"

urlpatterns = [
    path("", views.skill_list, name="skill_list"),
    path("<slug:slug>/", views.skill_detail, name="skill_detail"),
    path("<slug:slug>/start/", views.start_learning, name="start_learning"),
    path("<slug:slug>/verify/", views.submit_verification, name="submit_verification"),
]
