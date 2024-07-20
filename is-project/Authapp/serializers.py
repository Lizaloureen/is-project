from Authapp.models import User
from rest_framework import serializers
from django.contrib.auth import authenticate


class RegisterSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['email', 'password', 'user_type', 'phone']
    extra_kwargs = {'password': {'write_only': True}}

  def create(self, validated_data):
    user = User.objects.create_user(
       validated_data['email'], 
       validated_data['user_type'], 
       validated_data['phone'], 
       validated_data['password']
    )
    return user


class AuthSerializer(serializers.Serializer):
    '''serializer for the user authentication object'''
    username = serializers.EmailField()
    password = serializers.CharField(
        style={'input_type': 'password'},
        trim_whitespace=False
    )    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        user = authenticate(
            request=self.context.get('request'),    
            username=username,
            password=password
        )

        print('here', attrs.username, user.username)
        
        if not user:
            msg = ('Unable to authenticate with provided credentials')
            raise serializers.ValidationError(msg, code='authentication')

        attrs['user'] = user
        return