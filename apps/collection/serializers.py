from rest_framework import serializers

from .models import Course, Collection


class CourseSerializer(serializers.HyperlinkedModelSerializer):
    """Course Serializer."""
    problems = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Course
        fields = (
            'id', 'url', 'name', 'parent', 'problems',
        )


class CollectionSerializer(serializers.HyperlinkedModelSerializer):
    """Course Serializer."""
    problems = serializers.PrimaryKeyRelatedField(read_only=True, many=True)

    class Meta:
        model = Collection
        fields = (
            'id', 'url', 'name', 'parent', 'problems',
        )


class CourseDestroySerializer(serializers.Serializer):
    force_delete = serializers.BooleanField()
