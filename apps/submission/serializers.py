from django.contrib.auth import get_user_model

from rest_framework import serializers

from submission.models import Submission
from apps.user.serializers import UserProfileSerializer


User = get_user_model()


class SubmissionSerializer(serializers.HyperlinkedModelSerializer):
    problem = serializers.SlugRelatedField(read_only=True, slug_field="title")
    show_link = serializers.SerializerMethodField()
    userprofile = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = self.context.get('request').user

    def get_show_link(self, obj):
        if not self.user.is_anonymous:
            return obj.check_user_permission(self.user)
        else:
            return False

    def get_userprofile(self, obj):
        userprofile = User.objects.get(pk=obj.user_id).userprofile
        return UserProfileSerializer(
            userprofile,
            context={'request': self.context['request']}
        ).data
