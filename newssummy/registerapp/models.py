from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    activation_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()
    used_key = models.BooleanField(default=False)

    class Meta:
        db_table = 'UserProfile'


class UserPassChange(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pass_key = models.CharField(max_length=40)
    key_expires = models.DateTimeField()

    class Meta:
        db_table = 'UserPassChange'
