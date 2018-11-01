from django.db import models


class Group(models.Model):
    name = models.CharField('班级名称', max_length=100)
    grade = models.IntegerField('年级')
    class_num = models.IntegerField('班级')
    major = models.CharField('专业名称', max_length=100)

    def __str__(self):
        return self.name
