from collections import OrderedDict

from django.conf import settings

from rest_framework import decorators
from rest_framework.response import Response
from rest_framework.reverse import reverse


@decorators.api_view(['GET'])
def sitemap(request, format=None):
    urls_dict = OrderedDict([
        ('sitemap', 'sitemap'),
        ('course', 'course-list'),
        ('collection', 'collection-list'),
        ('problem', 'problem-list'),
        ('dgut_login', 'dgut_login'),
        ('dgut_logout', 'dgut_logout'),
        ('test_case', 'test_case'),
        ('user', 'user-list'),
        ('contest', 'contest-list'),
        ('group', 'group-list'),
        ('delegation', 'delegation-list'),
    ])

    if settings.DEBUG:
        urls_dict.update({
            'xlogin': 'xlogin',
            'user debug': 'user_debug-list',
        })

    urls = OrderedDict()
    for k, v in urls_dict.items():
        urls[k] = reverse(v, request=request, format=format)

    return Response(urls)
