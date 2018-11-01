from django.db import models
from django.contrib.auth import get_user_model

from problem.models import Problem


User = get_user_model()


class ProblemValidation(models.Model):
    """Review record of problems."""
    problem = models.OneToOneField(Problem, related_name='validation',
                                   on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='validations',
                                 on_delete=models.CASCADE)
    create_time = models.DateTimeField(auto_now_add=True)
