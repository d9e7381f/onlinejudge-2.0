from django.conf import settings

from rest_framework import exceptions
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

from apps.utils.response import Response


class GetSerializerClass(object):
    def get_serializer_class(self):
        try:
            return self.serializer_action_classes[self.action]
        except (KeyError, AttributeError):
            return super().get_serializer_class()


def custom_exception_handler(exc, context):
    """Return as following format for compatible of origin version.

    {
      "error": "error",
      "data": error_msg,
    }
    """
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Error from REST browable API.
    if not response:
        return response

    # Set data for different type of exceptions.
    # For validation error.
    if isinstance(exc, ValidationError):
        data = '非法输入'  # Default error message.

        # Custom error message.
        if isinstance(exc.detail, list):
            data = exc.detail[0]

        # Non-field error.
        elif exc.detail.get('non_field_errors'):
            data = exc.detail['non_field_errors'][0]

        # Field error.
        elif isinstance(exc.detail, dict):
            # Catch the first custom field error.
            for k, v in exc.detail.items():
                if isinstance(v, list):
                    data = v[0]
                else:  # v is str
                    data = v
                break

    # Exception dict in {'detail': <exc>} format.
    elif response.data.get('detail'):
        data = response.data.get('detail')
    else:
        return response

    if response is not None and data:
        origin_exc = response.data
        origin_status_code = response.status_code

        response.status_code = 200
        response.data = {
            'error': 'error',
            'data': data,
        }

        # Origin exception from DRF.
        if settings.DEBUG:
            response.data['exception'] = origin_exc
            response.data['status_code'] = origin_status_code

    return response


class MyModelViewSet(ModelViewSet):
    """
    Custom response format for compatibility of origin version.
    """
    def list(self, request, *args, **kwargs):
        return Response(super().list(request, *args, **kwargs))

    def retrieve(self, request, *args, **kwargs):
        return Response(super().retrieve(request, *args, **kwargs))

    def create(self, request, *args, **kwargs):
        # Response with only a string rather than serializer's data to
        # prevent issue from m2m field.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        return Response('Success')

    def destroy(self, request, *args, **kwargs):
        super().destroy(request, *args, **kwargs)
        return Response('Success')

    def update(self, request, *args, **kwargs):
        # Response with only a string rather than serializer's data to
        # prevent issue from m2m field.
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data,
                                         partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response('Success')
