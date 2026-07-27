from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from .models import Task, Comment, Notification, User, UserProfile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.get_or_create(user=instance)

@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created and instance.assignee:
        Notification.objects.create(
            user=instance.assignee,
            message=f"Yeni görev: {instance.title}",
            task=instance
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    if created and instance.task.creator != instance.user:
        Notification.objects.create(
            user=instance.task.creator,
            message=f"Görevinize yeni yorum yapıldı: {instance.task.title}",
            task=instance.task
        )

@receiver(post_save, sender=Task)
@receiver(post_delete, sender=Task)
def announce_task_change(sender, instance, **kwargs):
    channel_layer = get_channel_layer()
    if channel_layer:
        try:
            async_to_sync(channel_layer.group_send)(
                'tasks_channel_group',
                {
                    'type': 'task_event',
                    'action': 'task_updated',
                    'task_id': instance.id
                }
            )
        except Exception:
            pass