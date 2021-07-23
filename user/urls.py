from django.urls import path
from user.views import CustomUserCreate, CustomUserDetail, CustomUserSearch


app_name = 'user'

urlpatterns = [
    path('register/', CustomUserCreate.as_view(), name="register-user"),
    path('<int:pk>/', CustomUserDetail.as_view(), name="user-detail"),
    path('search/', CustomUserSearch.as_view(), name="user-search"),
]
