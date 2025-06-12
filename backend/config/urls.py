from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/notes/', include('apps.notes.urls'), name='notes'),
    path('api/summarizer/', include('apps.summarizer.urls'), name='summarizer'),
    path('api/transcriber/', include('apps.transcriber.urls'), name='transcriber'),
    path('api/users/', include('apps.users.urls'), name='users'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
