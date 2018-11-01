from rest_framework import serializers

from .models import Comment
from apps.user.serializers import UserProfileSerializer


class CommentSerializer(serializers.HyperlinkedModelSerializer):
    user = UserProfileSerializer(source='user.userprofile')

    class Meta:
        model = Comment
        fields = (
            'id', 'content', 'user', 'create_time', 'last_edit_time',
            'is_modified', 'ordinal',
            )
