from django.urls import path

from api.views import bbs, BbDetailView, comments

urlpatterns = [
    path("bbs/<int:pk>/comments/", comments),
    path("bbs/<int:pk>/", BbDetailView.as_view()),
    path("bbs/", bbs),
]
