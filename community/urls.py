from django.urls import path
from . import views

app_name = "community"

urlpatterns = [
    path("", views.feed, name="feed"),
    path("post/", views.create_post, name="create_post"),
    path("post/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path("post/<int:pk>/comment/", views.add_comment, name="add_comment"),
    path("post/<int:pk>/report/", views.report_post, name="report_post"),
]
