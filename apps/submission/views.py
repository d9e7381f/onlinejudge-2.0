from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from apps.utils.response import Response
from submission.models import Submission
from .filters import SubmissionFilter
from . import serializers


class SubmissionViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        GenericViewSet):
    queryset = Submission.objects.select_related('problem__created_by')
    filter_class = SubmissionFilter
    serializer_class = serializers.SubmissionSerializer

    def list(self, request, *args, **kwargs):
        return Response(super().list(request, *args, **kwargs))

    def retrieve(self, request, *args, **kwargs):
        return Response(super().list(request, *args, **kwargs))
