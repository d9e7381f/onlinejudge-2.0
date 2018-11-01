from utils.api import serializers
from utils.api._serializers import UsernameSerializer

from .models import Announcement


class CreateAnnouncementSerializer(serializers.Serializer):
    title = serializers.CharField(max_length=64)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()


class AnnouncementSerializer(serializers.ModelSerializer):
    created_by = UsernameSerializer()
    userprofile = serializers.SerializerMethodField()

    class Meta:
        model = Announcement
        fields = "__all__"

    def get_userprofile(self, obj):
        return {
            'real_name': obj.created_by.userprofile.real_name,
        }


class EditAnnouncementSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    title = serializers.CharField(max_length=64)
    content = serializers.CharField(max_length=1024 * 1024 * 8)
    visible = serializers.BooleanField()
