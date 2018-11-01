from rest_framework import decorators, exceptions
from rest_framework.reverse import reverse

from . import serializers
from .models import Course, Collection
from problem.models import Problem
from .permissions import BaseCollectionPermission
from apps.xproblem.views import MyModelViewSet, GetSerializerClass
from apps.utils.response import Response


def get_family(queryset, view_name, request):
    """List recursive relation of course or collection."""
    ret = []
    for each in queryset:
        ret.append({
            'id': each.pk,
            'url': reverse(view_name, kwargs={'pk': each.pk}, request=request),
            'name': each.name,
            'problem': [problem.pk for problem in each.problems.all()],
            'children': get_family(each.children.all(), view_name, request)
        })

    return ret


class BaseCollectionViewSet(object):
    """Abstract class of course and collection viewset."""
    def modify_problems(self, request, action):
        """Add/remove problems to/from course/collection."""
        # Action check.
        if action not in ('add', 'remove'):
            msg = 'Invalid action for modifing problem.'
            return Response(msg)

        # Validate problems ID.
        problems = request.data.get('problems')
        for each in problems:
            try:
                Problem.objects.get(pk=each)
            except (ValueError, Problem.DoesNotExist):
                msg = 'Illegal problem ID'
                return Response(msg)

        # Modify course or collection.
        instance = self.get_object()
        if action == 'add':
            instance.problems.add(*problems)
        elif action == 'remove':
            instance.problems.remove(*problems)
        return Response('Success')


class CourseViewSet(GetSerializerClass,
                    BaseCollectionViewSet,
                    MyModelViewSet):
    """
    # Destroy
    By default, course contains problems can't be deleted, but you can
    choose ignore it and force delete.

        DELETE /<id>/
        {
            "force_delete": True
        }

    # Problems
    **Add** problems to course:

        POST /<course_id>/add_problems/

        {
            "problems": [
                <problem1_id>,
                <problem2_id>,
                ...
            ]
        }

    **Remove** problems from course:

        POST /<course_id>/remove_problems/

        {
            "problems": [
                <problem1_id>,
                <problem2_id>,
                ...
            ]
        }
    """
    queryset = Course.objects.prefetch_related('problems')
    serializer_class = serializers.CourseSerializer
    permission_classes = (BaseCollectionPermission,)
    serializer_action_classes = {
        'destroy': serializers.CourseDestroySerializer,
    }

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(level=0)
        return Response({
            'course': get_family(queryset, 'course-detail', request)
        })

    # Return new instance data which frontend need.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)

    @decorators.detail_route(methods=('POST',))
    def add_problems(self, request, *args, **kwargs):
        return self.modify_problems(request, 'add')

    @decorators.detail_route(methods=('POST',))
    def remove_problems(self, request, *args, **kwargs):
        return self.modify_problems(request, 'remove')

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Only leaf-node course can be deleted.
        if not instance.is_leaf_node():
            raise exceptions.ValidationError('无法删除含有子结点的课程')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_destroy(instance, serializer)

        return Response('Success')

    def perform_destroy(self, instance, serializer):
        # By default, course contains problems can't be deleted, but
        # you can choose ignore it and force delete.
        if serializer.data['force_delete']:
            instance.problems.all().delete()
        elif instance.problems.exists():
            raise exceptions.ValidationError('无法删除已有题目的课程')

        instance.delete()


class CollectionViewSet(MyModelViewSet):
    """Collection viewset.

    **Delete** a collection:

        GET /<collection_id>/delete/

    """
    queryset = Collection.objects.all()
    serializer_class = serializers.CollectionSerializer
    permission_classes = (BaseCollectionPermission,)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset().filter(level=0)
        return Response({
            'collection': get_family(queryset, 'collection-detail', request),
        })

    # Return new instance data which frontend need.
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response(serializer.data)
