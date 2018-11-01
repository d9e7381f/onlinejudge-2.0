from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Delegation(models.Model):
    delegator = models.ForeignKey(User, on_delete=models.CASCADE,
                                  related_name='delegations')
    delegates = models.ManyToManyField(User, related_name='jobs')
    course = models.ForeignKey('collection.course', on_delete=models.CASCADE,
                               related_name='delegations')
    create_time = models.DateTimeField(auto_now_add=True)
    read_time = models.DateTimeField(null=True)
    is_completed = models.BooleanField(default=False)

    def is_read(self):
        return bool(self.read_time)

    class Meta:
        ordering = ('-create_time',)
        db_table = 'delegation'
