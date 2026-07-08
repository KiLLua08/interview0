"""URL routes for authentication endpoints."""

from django.urls import path

from accounts.routes import views

urlpatterns = [
    path("register", views.register, name="auth-register"),
    path("login", views.login, name="auth-login"),
    path("me", views.me, name="auth-me"),
]
