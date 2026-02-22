from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager , PermissionsMixin
import uuid
from django.utils import timezone
from datetime import timedelta


# Create your models here.
class Usermanager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("email is required ")
        user = self.model(email=self.normalize_email(email),**extra_fields)
        user.set_password(password)
        user.save(using =self._db)
        return user


    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", "ADMIN")

        return self.create_user(email, password, **extra_fields)

        
class User(AbstractBaseUser,PermissionsMixin):
    ROLE_CHOICES = (
        ("CUSTOMER", "CUSTOMER"),
        ("RESTAURANT", "RESTAURANT"),
        ("DELIVERY", "DELIVERY"),
        ("ADMIN", "ADMIN"),
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, unique=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]


    objects = Usermanager()
    def __str__(self):
        return self.email
    


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,related_name='profile')
    phone_number = models.CharField(max_length=20)
    address = models.TextField(blank=True, null=True)
    profile_image = models.ImageField(upload_to="profiles/" , blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self):
        return self.user.email

def default_expiry():
    return timezone.now() + timedelta(minutes=20)

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used= models.BooleanField(default=False)
    expires_at = models.DateTimeField(default=default_expiry)

    # def save(self, *args , **kwargs):
    #     if not self.expires_at:
    #         self.expires_at = timezone.now() + timedelta(minutes=15)
    #     super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.email}-{self.token}"



class Restaurant(models.Model):
    STATUS_CHOICES =(
       ( 'PENDING' , 'PENDING'),
       ( 'APPROVED' , 'APPROVED'),
       ( 'REJECTED' , 'REJECTED')
       )
    owner = models.OneToOneField(User, models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=100)
    address = models.CharField(max_length=100)
    is_active =  models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    