from rest_framework import serializers

from core.models import User


class UserSerializer(serializers.ModelSerializer):
    # model serializer does not provide seperation of concerns
    # we can use regular serializer for that
    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        instance = self.Meta.model(**validated_data)
        if password is not None:
            instance.set_password(password)
        instance.save() # save the user instance to the database
        return instance