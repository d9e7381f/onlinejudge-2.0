from rest_framework import serializers
from rest_framework.reverse import reverse

from django.contrib.auth import get_user_model

from .models import Group
from account.models import UserProfile


User = get_user_model()


class UserMinSerializer(serializers.HyperlinkedModelSerializer):
    # Serializer of only necessary data of user and her userprofile.
    real_name = serializers.CharField(source='userprofile.real_name')
    avatar = serializers.CharField(source='userprofile.avatar')
    mood = serializers.CharField(source='userprofile.mood')
    group = serializers.StringRelatedField(source='userprofile.group')

    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'real_name', 'avatar', 'mood', 'group',
        )


class UserProfileSerializer(serializers.HyperlinkedModelSerializer):
    group = serializers.StringRelatedField()

    class Meta:
        model = UserProfile
        fields = (
            'id', 'url', 'acm_problems_status', 'oi_problems_status',
            'real_name', 'avatar', 'blog', 'mood', 'github', 'accepted_number',
            'total_score', 'submission_number', 'group',
        )


class UserRankSerializer(serializers.HyperlinkedModelSerializer):
    problem_count = serializers.IntegerField()
    vote_count = serializers.IntegerField()
    profile = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'admin_type', 'problem_count',
            'vote_count', 'profile',
        )

    def get_profile(self, obj):
        return {
            'real_name': obj.real_name,
            'avatar': obj.avatar,
            'group': obj.group,
            'mood': obj.mood,
        }


class UserDebugSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.SerializerMethodField()
    group = serializers.StringRelatedField(source='userprofile.group')

    class Meta:
        model = User
        fields = (
            'id', 'url', 'username', 'admin_type', 'group',
        )

    def get_url(self, obj):
        return reverse('user_debug-detail',
                       kwargs=({'pk': obj.pk}),
                       request=self.context.get('request'))


class UserDebugCreateSerializer(serializers.Serializer):
    # Only create user with group and username.
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all())
    username = serializers.CharField()

    def create(self, validated_data):
        instance = User.objects.create(username=validated_data['username'])

        # Set default password
        pwd = 'password'
        instance.set_password(pwd)
        instance.save()

        # Add user to group.
        UserProfile.objects.create(
            user=instance,
            group=validated_data['group'],
        )

        return instance


class UserDebugUpdateSerializer(serializers.Serializer):
    """Change user's group."""
    group = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all())

    def update(self, instance, validated_data):
        userprofile = instance.userprofile
        userprofile.group = validated_data['group']
        userprofile.save()

        return instance


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class_num = serializers.SerializerMethodField()

    class Meta:
        model = Group
        fields = (
            'id', 'url', 'name', 'grade', 'major', 'class_num',
        )

    def get_class_num(self, obj):
        return f'{obj.class_num}班'
