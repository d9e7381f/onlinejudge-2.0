from django_filters import rest_framework as filters

from options.options import SysOptions
from problem.models import Problem
from submission.models import Submission


class SubmissionFilter(filters.FilterSet):
    """Problem filter."""
    problem_id = filters.CharFilter(method='filter_problem_id')
    myself = filters.BooleanFilter(method='filter_myself')
    username = filters.CharFilter(lookup_expr='icontains')

    class Meta:
        model = Submission
        fields = [
            'result',
        ]

    def filter_problem_id(self, queryset, name, value):
        param = {
            'contest': None,
            'visible': True,
            '_id': value,
        }
        # django_filters will handle the exception
        problem = Problem.objects.filter(**param).first()
        return queryset.filter(problem=problem)

    def filter_myself(self, queryset, name, value):
        if not SysOptions.submission_list_show_all:
            return queryset.filter(user_id=self.request.user.id)
