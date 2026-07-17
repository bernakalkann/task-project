from rest_framework import serializers
from .models import User, Task, Comment

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'birthday', 'department']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Sadece kullanıcı adını göstersin
    class Meta:
        model = Comment
        fields = ['id', 'task', 'user', 'description', 'create_date']

class TaskSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True) # Task ile yorumları beraber çekmek için

    class Meta:
        model = Task
        fields = ['id', 'title', 'definition', 'create_date', 'creator', 'assignee', 'state', 'comments']
        read_only_fields = ['creator'] # creator otomatik olarak atanacak, kullanıcı değiştiremez