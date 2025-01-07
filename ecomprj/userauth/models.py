from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True)
    bio = models.CharField(max_length=255, blank=True, null=True)
    

    # Ensure username is set to email automatically
    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.email
        super(User, self).save(*args, **kwargs)

    USERNAME_FIELD = "email"  # Login will be with email instead of username
    REQUIRED_FIELDS = ["username"]  # Make username required during user creation
    def __str__(self):
        return self.email

