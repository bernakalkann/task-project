from rest_framework import serializers
from .models import User, Task, Comment, UserProfile, Notification

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
    assignee_username = serializers.ReadOnlyField(source='assignee.username')
    creator_username = serializers.ReadOnlyField(source='creator.username')

    class Meta:
        model = Task
        fields = ['id', 'title', 'definition', 'create_date', 'creator', 'creator_username', 'assignee', 'assignee_username', 'state', 'comments']
        read_only_fields = ['creator'] # creator otomatik olarak atanacak, kullanıcı değiştiremez

    def validate_assignee(self, value):
        request = self.context.get('request')
        # Eğer istek atan kullanıcı admin değilse, görevi sadece kendine atayabilir
        if request and not request.user.is_staff:
            if value != request.user:
                raise serializers.ValidationError("Normal kullanıcılar sadece kendilerine görev atayabilirler.")
        return value
    


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ['id', 'message', 'is_read', 'created_at']

class UserProfileSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(source='user.first_name', required=False, allow_blank=True)
    last_name = serializers.CharField(source='user.last_name', required=False, allow_blank=True)
    email = serializers.EmailField(source='user.email', required=False, allow_blank=True)
    username = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'id', 'username', 'first_name', 'last_name', 'email',
            'department', 'position', 'bio', 'phone', 'avatar', 'created_at'
        ]
        read_only_fields = ['id', 'username', 'created_at']

    def update(self, instance, validated_data):
        # Birebir ilişkili User modelindeki alanları güncelle
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        for attr, value in user_data.items():
            setattr(user, attr, value)
        user.save()

        # UserProfile modelindeki alanları güncelle
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance