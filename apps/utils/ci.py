import os

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings


@csrf_exempt
def ci(request):
    """Git webhook for repo update"""
    # Script locates at parent dir of repo dir
    dirname = os.path.dirname(settings.BASE_DIR)
    basename = 'githook.sh'
    fp = os.path.join(dirname, basename)
    if os.path.exists(fp):
        os.system('sh %s/%s' % (dirname, basename))
    return HttpResponse('Success')
