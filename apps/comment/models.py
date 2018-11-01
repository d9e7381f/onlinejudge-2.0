from django.db import models
from django.contrib.auth import get_user_model

from mptt.models import MPTTModel, TreeForeignKey

from utils.models import RichTextField
from problem.models import Problem


User = get_user_model()


class Comment(MPTTModel):
    """Comment of problem."""
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', verbose_name='父评论')
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE,
                                related_name='comments', verbose_name='题目')
    user = models.ForeignKey(User, on_delete=models.CASCADE,
                             related_name='comments', verbose_name='用户')
    content = RichTextField('内容')
    create_time = models.DateTimeField(auto_now_add=True)
    last_edit_time = models.DateTimeField(auto_now=True)
    is_modified = models.BooleanField('是否有修改', default=False)
    # The ordinal number of comment of a problem.
    ordinal = models.IntegerField()

    class Meta:
        ordering = ('create_time',)
