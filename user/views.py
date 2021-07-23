from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend, FilterSet, CharFilter
from rest_framework import status, filters
from rest_framework.generics import CreateAPIView, RetrieveUpdateDestroyAPIView, ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from user.models import PrismUser
from user.serializers import CustomUserSerializer


class CustomUserCreate(CreateAPIView):
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer
    queryset = PrismUser.objects.all()


class CustomUserDetail(RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = PrismUser.objects.all()

    def update(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = get_object_or_404(PrismUser, pk=pk)
        if request.user != user:
            return Response({'error': 'Access restricted to account owner only'}, status=status.HTTP_403_FORBIDDEN)

        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        user = get_object_or_404(PrismUser, pk=pk)
        if request.user != user:
            return Response({'error': 'Access restricted to account owner only'}, status=status.HTTP_403_FORBIDDEN)

        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class UserFilter(FilterSet):
    user_name = CharFilter(field_name='user_name', lookup_expr='icontains')
    email = CharFilter(field_name='email', lookup_expr='icontains')
    first_name = CharFilter(field_name='first_name', lookup_expr='icontains')
    last_name = CharFilter(field_name='last_name', lookup_expr='icontains')

    class Meta:
        model = PrismUser
        fields = ['user_name', 'email', 'first_name', 'last_name']


class CustomUserSearch(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CustomUserSerializer
    queryset = PrismUser.objects.all()
    filter_backends = (DjangoFilterBackend, filters.SearchFilter,)
    filter_class = UserFilter
    filter_fields = ('user_name', 'email', 'first_name', 'last_name')
