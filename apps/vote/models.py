from django.db import models
from django.contrib.auth import get_user_model

from problem.models import Problem


User = get_user_model()


class Vote(models.Model):
    problem = models.ForeignKey(Problem, related_name='votes',
                                null=True, blank=True,
                                on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='votes',
                             on_delete=models.CASCADE)
    is_up = models.BooleanField()
    score = models.IntegerField(default=0)
