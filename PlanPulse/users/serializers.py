from rest_framework import serializers
from django.contrib.auth import get_user_model, authenticate

UserModel = get_user_model()

class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserModel
        fields = ["email", "password"]
    
    def create(self, validated_data):
        if 'email' not in validated_data:
            raise serializers.ValidationError("The email field is required.")
        validated_data['username'] = validated_data['email']
        user = UserModel.objects.create_user(**validated_data)
        return user
    

class UserLoginSerializer(serializers.Serializer):
    username = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Incorrect Credentials")
    

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = ["username", "email"]