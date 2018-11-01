from ipaddress import ip_network

from rest_framework import serializers, exceptions

from contest.models import Contest
from apps.user.models import Group
from apps.user.serializers import GroupSerializer
from utils.cache import cache
from utils.constants import CacheKey


class ContestSerializer(serializers.HyperlinkedModelSerializer):
    problem = serializers.HyperlinkedRelatedField(
        source='problem_set',
        read_only=True,
        many=True,
        view_name='problem-detail'
    )
    groups = GroupSerializer(many=True, read_only=True)
    created_by = serializers.SerializerMethodField()

    class Meta:
        model = Contest
        fields = (
            'id', 'url', 'problem', 'groups', 'title', 'description',
            'real_time_rank', 'rule_type', 'start_time', 'end_time',
            'create_time', 'last_update_time', 'visible', 'allowed_ip_ranges',
            'created_by',
        )

    def get_created_by(self, obj):
        return obj.created_by.userprofile.real_name


class ContestUpdateCreateSerializer(serializers.HyperlinkedModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(),
        many=True,
        allow_null=True,
    )

    class Meta:
        model = Contest
        fields = (
            'status', 'contest_type', 'title', 'description', 'real_time_rank',
            'password', 'rule_type', 'start_time', 'end_time', 'visible',
            'allowed_ip_ranges', 'groups',
        )

    def create(self, validated_data):
        user = self.context.get('request').user
        validated_data['created_by'] = user
        return super().create(validated_data)

    def validate_password(self, value):
        """From qduoj."""
        if not value:
            return None
        return value

    def validate_allowed_ip_ranges(self, value):
        for ip_range in value:
            try:
                ip_network(ip_range, strict=False)
            except ValueError:
                raise serializers.ValidationError(f'{ip_range} 不是有效的 CIDR')
        return value

    def validate(self, data):
        if data['start_time'] >= data['end_time']:
            raise serializers.ValidationError('结束时间必须在开始时间之后')
        return data

    def update(self, instance, validated_data):
        # # From qduoj.
        # if not instance.real_time_rank and validated_data["real_time_rank"]:
        #     cache_key = f"{CacheKey.contest_rank_cache}:{instance.id}"
        #     cache.delete(cache_key)

        return super().update(instance, validated_data)
