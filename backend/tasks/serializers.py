from rest_framework import serializers
from .models import User, Task, Comment

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'email', 'first_name', 'last_name', 'birthday', 'department']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        if not password:
            raise serializers.ValidationError({"password": "Şifre alanı zorunludur."})
        user = super().create(validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

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

    def validate_assignee(self, value):
        request = self.context.get('request')
        # Eğer istek atan kullanıcı admin değilse, görevi sadece kendine atayabilir
        if request and not request.user.is_staff:
            if value != request.user:
                raise serializers.ValidationError("Normal kullanıcılar sadece kendilerine görev atayabilirler.")
        return value