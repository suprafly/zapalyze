from django.db import models

from django.conf import settings
from django.contrib.auth import get_user_model


def User():
    return get_user_model()


class Zap(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL)
    name = models.CharField(max_length=300)


class Task(models.Model):
    zap = models.ForeignKey(Zap)
    description = models.CharField(max_length=300)
    timestamp = models.DateTimeField()





