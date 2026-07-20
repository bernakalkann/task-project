from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    birthday = models.DateField(null=True, blank=True) 
    department = models.CharField(max_length=100, null=True, blank=True)
    pass

class Task(models.Model):
    STATE_CHOICES = [
        ('to do', 'TO DO'),
        ('in progress', 'IN PROGRESS'),
        ('in code review', 'IN CODE REVIEW'),
        ('blocked dev', 'BLOCKED (DEV)'),
        ('ready for test', 'READY FOR TEST'),
        ('in test', 'IN TEST'),
        ('blocked test', 'BLOCKED (TEST)'),
        ('done', 'DONE')
    ]
    
    title = models.CharField(max_length=250)
    create_date = models.DateTimeField(auto_now_add=True)
    definition = models.TextField() 
    #foreignkeys
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    state = models.CharField(max_length=30, choices=STATE_CHOICES, default='to do')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subtasks')

    PRIORITY_CHOICES = [
        ('low', 'Düşük'),
        ('medium', 'Orta'),
        ('high', 'Yüksek'),
        ('critical', 'Acil')
    ]
    TYPE_CHOICES = [
        ('task', 'Görev'),
        ('bug', 'Hata'),
        ('story', 'Hikaye'),
        ('epic', 'Epic')
    ]
    
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    task_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='task')
    duration = models.PositiveIntegerField(default=0, help_text="Tahmini süre (saat)")
    due_date = models.DateField(null=True, blank=True)
    epic = models.CharField(max_length=100, blank=True, null=True, default='')
    version = models.CharField(max_length=50, blank=True, null=True, default='')

    def __str__(self):
        return self.title

class Comment(models.Model):
    #foreignkeys
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    description = models.TextField()
    create_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.description[:20]}"
    

class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    message = models.CharField(max_length=255)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey('Task', on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

class UserProfile(models.Model):
    DEPARTMENT_CHOICES = [
        ('İK', 'İK'),
        ('Yazılım', 'Yazılım'),
        ('Satış', 'Satış'),
        ('Tasarım', 'Tasarım')
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, default='Yazılım')
    position = models.CharField(max_length=100, blank=True)
    bio = models.TextField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.TextField(blank=True)  # Base64 image content
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} Profili"

class Attachment(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='attachments', null=True, blank=True)
    name = models.CharField(max_length=255)
    file_data = models.TextField() # Base64 representation
    file_type = models.CharField(max_length=100, blank=True, default='')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.file_type})"