from django.db import models

from account.models import User
from utils.models import RichTextField
# Create your models here.

class FeedBack(models.Model):
  title = models.CharField(max_length=64)
  # HTML
  content = RichTextField()
  reply = RichTextField()
  create_time = models.DateTimeField(auto_now_add=True)
  created_by = models.ForeignKey(User)
  reply_by = models.ForeignKey(User)
  class Meta:
    db_table = "feedback"
    ordering = ("-create_time",)