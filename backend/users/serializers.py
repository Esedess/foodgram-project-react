from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Follow

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
        )


class FollowSerializer(serializers.ModelSerializer):
    user = UserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault(),
    )

    class Meta:
        fields = ('user', 'author',)
        model = Follow
