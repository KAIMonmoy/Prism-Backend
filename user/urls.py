from django.urls import path
from user.views import CustomUserCreate


app_name = 'user'

urlpatterns = [
    path('register/', CustomUserCreate.as_view(), name="register-user"),
]
