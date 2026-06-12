from rest_framework import serializers

from users.models import User

from .validators import validate_username


class SignupSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
    )
    email = serializers.EmailField(max_length=254)

    class Meta:
        model = User
        fields = ('email', 'username')
        validators = ()

    def validate(self, attrs):
        username = attrs['username']
        email = attrs['email']
        username_owner = User.objects.filter(username=username).first()
        email_owner = User.objects.filter(email=email).first()

        if username_owner and username_owner.email != email:
            raise serializers.ValidationError(
                {'username': 'Это имя пользователя уже занято.'}
            )
        if email_owner and email_owner.username != username:
            raise serializers.ValidationError(
                {'email': 'Этот адрес электронной почты уже занят.'}
            )
        return attrs

    def create(self, validated_data):
        user, created = User.objects.get_or_create(**validated_data)
        if created:
            user.set_unusable_password()
            user.save(update_fields=('password',))
        return user


class TokenSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    confirmation_code = serializers.CharField()


class UserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        max_length=150,
        validators=(validate_username,),
    )

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
        )

    def validate_username(self, value):
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError(
                'Это имя пользователя уже занято.'
            )
        return value


class MeSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        read_only_fields = ('role',)
