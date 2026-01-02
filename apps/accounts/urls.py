from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("profile/edit/", views.profile_edit, name="profile_edit"),
    path("password-change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("register/", views.register_view, name="register"),
    path("verify/<str:token>/", views.verify_email_view, name="verify_email"),
    path("pending/", views.verification_pending_view, name="verification_pending"),
]
