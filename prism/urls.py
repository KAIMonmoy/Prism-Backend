"""prism URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.schemas import get_schema_view
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    # User Authentication
    path('api/user/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/user/token-refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    # User Registration
    path('api/user/', include('user.urls', namespace='user')),
    # Core URLs
    path('api/workspace/', include('core.urls', namespace='core')),
    # Rest-Framework Auth Form
    path('api-auth/', include('rest_framework.urls')),

    # OpenAPI Schema
    path('api/schema/', get_schema_view(
        title="Prism",
        description="API for all Prism endpoints"
    ), name='openapi-schema'),
    # Swagger-UI Docs
    path('api/docs/', TemplateView.as_view(
        template_name='swagger-ui.html',
        extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
