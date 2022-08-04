# from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('users/', include('users.urls')),
    path('', include('djoser.urls')),
    path('', include('food.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
