from rest_framework.generics import CreateAPIView
from rest_framework.permissions import AllowAny

from user.models import PrismUser
from user.serializers import CustomUserSerializer


class CustomUserCreate(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer
    queryset = PrismUser.objects.all()
