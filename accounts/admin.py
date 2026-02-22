from django.contrib import admin
from .models import User,Profile, Restaurant,PasswordResetToken
admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Restaurant)