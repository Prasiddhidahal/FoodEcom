from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=50, unique=True)
    bio = models.CharField(max_length=255)
    
    USERNAME_FIELD = "email"  # Login will be with email instead of username
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.username

