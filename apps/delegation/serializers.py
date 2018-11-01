from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import Delegation
from apps.collection.models import Course
from apps.user.serializers import UserMinSerializer


User = get_user_model()


class DelegationSerializer(serializers.HyperlinkedModelSerializer):
    delegator = UserMinSerializer()
    delegates = UserMinSerializer(many=True, read_only=True)
    course = serializers.StringRelatedField()

    class Meta:
        model = Delegation
        fields = (
            'id', 'url', 'delegator', 'delegates', 'course', 'create_time',
            'read_time', 'is_completed',
        )


class DelegationModifySerializer(serializers.HyperlinkedModelSerializer):
    delegates = serializers.ListField(child=serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(admin_type='Regular User')))
    course = serializers.PrimaryKeyRelatedField(
        queryset=Course.objects.all())

    class Meta:
        model = Delegation
        fields = (
            'delegates', 'course',
        )

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['delegator'] = user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context['request'].user
        validated_data['delegator'] = user
        return super().update(instance, validated_data)
