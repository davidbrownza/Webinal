from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

from datetime import datetime, timedelta

class Credentials(models.Model):
    Token = models.TextField()
    TokenExpiryDate = models.DateTimeField(default=self.calculate_expiry())

    User = models.OneToOneField(User)

    class Meta:
        db_table = "Credentials"

    def calculate_expiry(self):
        return datetime.now() + timedelta(seconds=settings.TOKEN_TTL)
