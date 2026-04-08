from django.urls import path

from .views import (
    RegisterView,
    google_auth,
    forgot_password,
    reset_password_confirm,
    CustomTokenObtainPairView,
    admin_get_users,
    admin_create_user,
    admin_update_user,
    admin_delete_user,
)

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/", CustomTokenObtainPairView.as_view()),
    path("google/", google_auth),
    path("forgot-password/", forgot_password),
    path("reset-password-confirm/", reset_password_confirm),

    # Admin routes
    path("admin/users/", admin_get_users),
    path("admin/users/create/", admin_create_user),
    path("admin/users/<int:user_id>/update/", admin_update_user),
    path("admin/users/<int:user_id>/delete/", admin_delete_user),
]
