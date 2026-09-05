from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/notes/', include('apps.notes.urls'), name='notes'),
    path('api/summarizer/', include('apps.summarizer.urls'), name='summarizer'),
    path('api/transcriber/', include('apps.transcriber.urls'), name='transcriber'),
    path('api/users/', include('apps.users.urls'), name='users'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
