from django.db import models
from mptt.models import MPTTModel, TreeForeignKey

from problem.models import Problem


class Course(MPTTModel):
    """Problem collection sorted out by course."""
    name = models.CharField('课程名称', max_length=100)
    # problems = models.ManyToManyField('problem', related_name='courses')
    problems = models.ManyToManyField(Problem, related_name='courses')
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', verbose_name='父课程')

    def __str__(self):
        return self.name


class Collection(MPTTModel):
    """Problem collection sorted out by knowledge point."""
    name = models.CharField('分类名称', max_length=100)
    # problems = models.ManyToManyField('problem', related_name='collections')
    problems = models.ManyToManyField(Problem, related_name='collections')
    parent = TreeForeignKey('self', null=True, blank=True,
                            related_name='children', verbose_name='父分类')

    def __str__(self):
        return self.name
