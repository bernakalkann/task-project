from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('tasks.urls')), # 'api/' ile başlayan her şey tasks/urls.py'a gider
]