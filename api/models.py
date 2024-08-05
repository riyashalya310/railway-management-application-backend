from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('user', 'User'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES,default='user')
    
    def __str__(self):
        return self.username

    groups = models.ManyToManyField(
        Group,
        related_name='custom_user_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='custom_user_permissions_set',  # Add related_name to avoid conflict
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

class Train(models.Model):
    train_number = models.CharField(max_length=20, unique=True)
    origin = models.CharField(max_length=50)
    destination = models.CharField(max_length=50)
    total_seats = models.IntegerField()

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    booking_time = models.DateTimeField(auto_now_add=True)
