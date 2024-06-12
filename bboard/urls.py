from django.urls import path

from .views import index, t_index

urlpatterns = [
    path('', index),
    path('test', t_index),
]
