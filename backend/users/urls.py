from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FollowViewSet

router_v1 = DefaultRouter()
router_v1.register('subscriptions', FollowViewSet, basename='subscriptions')


urlpatterns = [
    path('', include(router_v1.urls)),
]
