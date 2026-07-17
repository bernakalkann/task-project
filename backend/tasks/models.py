from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    birthday = models.DateField(null=True, blank=True) 
    department = models.CharField(max_length=100, null=True, blank=True)
    pass

class Task(models.Model):
    STATE_CHOICES = [
        ('done', 'DONE'),
        ('to do', 'TODO'),
        ('in progress', 'IN_PROGRESS')
    ]
    
    title = models.CharField(max_length=250)
    create_date = models.DateTimeField(auto_now_add=True)
    definition = models.TextField() 
    #foreignkeys
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assignee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_tasks')
    state = models.CharField(max_length=30, choices=STATE_CHOICES, default='to do')

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