from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    username = None
    name = models.CharField(max_length=30, blank=False, null=False)
    email = models.EmailField(unique=True, blank=False, null=False)
    password = models.TextField(blank=False, null=False)
    refer_code = models.CharField(max_length=30, blank=False, null=False)
    referral_points = models.IntegerField(default=0, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['refer_code'], name='unique_fields')
        ]


class Referrals(models.Model):
    refer_by = models.ForeignKey(User, on_delete=models.PROTECT)
    referral = models.OneToOneField(User, related_name='referral', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)