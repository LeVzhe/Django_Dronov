from django.contrib import admin
from django.urls import path, include

from bboard.views import index

urlpatterns = [
    path('bboard/', include('bboard.urls')),
    path('admin/', admin.site.urls),
]
