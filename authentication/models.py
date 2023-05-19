import datetime

import django.utils.timezone
from django.db import models


# Create your models here.

class User(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=100, default="")
    counter = models.IntegerField(default=0, blank=False)
    otp_created_at = models.DateTimeField(default=datetime.datetime.utcnow)
    is_blocked = models.BooleanField(default=False)
    blocked_at = models.DateTimeField(default=datetime.datetime.utcnow)
