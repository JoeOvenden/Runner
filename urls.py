
from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path("profile/<str:username>", views.profile, name="profile"),
    path("edit_profile", views.edit_profile, name="edit_profile"),
    path("follow", views.follow, name="follow"),
    path("attend", views.attend, name="attend"),
    path("celebrate/<str:username>", views.celebrate, name="celebrate"),
    path("user_search", views.user_search, name="user_search"),
    path("create_event", views.create_event, name="create_event"),
    path("event/<int:event_id>", views.event_page, name="event"),
    path("404", views.page_not_found, name="404"),
    path("events_search", views.events_search, name="events_search")
]
