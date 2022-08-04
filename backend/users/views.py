from rest_framework import (
    filters, mixins, pagination, permissions, serializers, status, viewsets,
)

from .models import Follow
from .serializers import FollowSerializer


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (permissions.AllowAny,)
