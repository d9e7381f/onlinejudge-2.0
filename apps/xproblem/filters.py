from django.db.models import Q

from django_filters import rest_framework as filters

from problem.models import Problem
from apps.collection.models import Course, Collection


class ProblemFilter(filters.FilterSet):
    """Problem filter."""
    course_id = filters.NumberFilter(label='课程ID', method='filter_course_id')
    collection_id = filters.NumberFilter(label='分类ID',
                                         method='filter_collection_id')
    is_valid = filters.BooleanFilter(name='is_valid')
    is_open_test_case = filters.BooleanFilter(name='is_open_test_case')
    in_course = filters.BooleanFilter(method='filter_in_course')
    keyword = filters.CharFilter(method='filter_keyword')
    tag = filters.CharFilter(method='filter_tag')
    has_perm = filters.BooleanFilter(method='filter_has_perm')
    contest_id = filters.NumberFilter(method='filter_contest_id')

    class Meta:
        model = Problem
        fields = [
            'difficulty',
        ]

    def filter_keyword(self, queryset, name, value):
        return queryset.filter(Q(title__icontains=value)
                               | Q(_id__icontains=value))

    def filter_tag(self, queryset, name, value):
        return queryset.filter(tags__name=value)

    def filter_course_id(self, queryset, name, value):
        # Filter problems under the course and its descendant children.
        courses = Course.objects.get(pk=value) \
                                .get_descendants(include_self=True)
        return queryset.filter(courses__in=courses)

    def filter_contest_id(self, queryset, name, value):
        if not value:
            # 0 means filter problems not in contest.
            param = {'contest': None}
        else:
            param = {'contest': value}

        return queryset.filter(**param)

    def filter_collection_id(self, queryset, name, value):
        # Filter problems under the collection and its descendant
        # children.
        collections = Collection.objects.get(pk=value) \
                                .get_descendants(include_self=True)
        return queryset.filter(collections__in=collections)

    def filter_in_course(self, queryset, name, value):
        if not value:
            return queryset.filter(courses=None)
        else:
            return queryset.exclude(courses=None)

    def filter_has_perm(self, queryset, name, value):
        """Return problems which user has permission to change."""
        if not value:
            return queryset

        user = self.request.user
        if user.is_anonymous:
            return queryset.none()
        elif not user.is_admin_role():
            return queryset.filter(created_by=user, is_valid=False)
        return queryset
