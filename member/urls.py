from django.urls import path
from .views import list_media

app_name = "member"
urlpatterns = [
    path('', list_media, name='list_media'),
]