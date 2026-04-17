from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ADMIN = 'ADMIN'
    MANAGER = 'MANAGER'
    SALES = 'SALES'
    
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MANAGER, 'Manager'),
        (SALES, 'Sales Executive'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=SALES)
    phone = models.CharField(max_length=15, blank=True, null=True)

    def __str__(self):
        return f"{self.username} ({self.role})"
