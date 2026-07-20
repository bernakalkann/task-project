from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Task, Comment, UserProfile, Attachment

admin.site.register(User, UserAdmin)
admin.site.register(Task)
admin.site.register(Comment)
admin.site.register(UserProfile)
admin.site.register(Attachment)
