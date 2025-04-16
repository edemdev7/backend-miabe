from djoser.serializers import UserCreateSerializer as BaseUserCreateSerializer
from djoser.serializers import UserSerializer as BaseUserSerializer
from .models import CustomUser

class UserCreateSerializer(BaseUserCreateSerializer):
    class Meta(BaseUserCreateSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'password', 'type', 'location')

class UserSerializer(BaseUserSerializer):
    class Meta(BaseUserSerializer.Meta):
        model = CustomUser
        fields = ('id', 'username', 'email', 'type', 'location', 'points')
