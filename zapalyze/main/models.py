from django.db import models

from django.conf import settings
from django.contrib.auth import get_user_model


def User():
    return get_user_model()


class UserProfile(models.Model):
    user   = models.OneToOneField(settings.AUTH_USER_MODEL)
    avatar = models.ImageField(blank=True)


class Zap(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=300)


class TaskSummary(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    zap = models.ForeignKey(Zap)
    number_of_tasks = models.IntegerField()
    date = models.DateField()





