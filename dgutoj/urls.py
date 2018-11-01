from django.conf import settings
from django.conf.urls import include, url
from rest_framework.routers import SimpleRouter

from apps.xproblem.views import ProblemViewSet
from apps.collection.views import CourseViewSet, CollectionViewSet
# from apps.submission import views as submission_views
from apps.user import views as user_views
from apps.contest.views import ContestViewSet
from apps.delegation.views import DelegationViewSet
from apps.test_case.views import TestCaseView
from apps.user.views import login, dgut_login, dgut_logout
from apps.utils.ci import ci
from .views import sitemap

router = SimpleRouter()
router.register(r'xproblem', ProblemViewSet)
router.register(r'course', CourseViewSet)
router.register(r'collection', CollectionViewSet)
router.register(r'user', user_views.UserViewSet)
router.register(r'user_profile', user_views.UserProfileViewSet)
router.register(r'group', user_views.GroupViewSet)
router.register(r'xcontest', ContestViewSet)
router.register(r'delegation', DelegationViewSet)
# router.register(r'xsubmission', submission_views.SubmissionViewSet)

# Only for debug.
if settings.DEBUG:
    router.register(r'user_debug',
                    user_views.UserDebugViewSet,
                    base_name='user_debug')

urlpatterns = [
    url(r'^api/login/', dgut_login, name='dgut_login'),
    url(r'^api/logout/', dgut_logout, name='dgut_logout'),
    url(r'^', include('oj.urls')),
    url(r'^$', sitemap, name='sitemap'),
    url(r'^api/$', sitemap, name='sitemap'),
    url(r'^api/sitemap/$', sitemap, name='sitemap'),
    url(r'^api/ci/$', ci, name='ci'),
    url(r'^api/', include(router.urls)),
    url(r'^api/test_case/', TestCaseView.as_view(), name='test_case'),
]

# Only for debug
if settings.DEBUG:
    urlpatterns += [
        url(r'^api/xlogin/', login, name='xlogin'),
        url(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),

    ]
