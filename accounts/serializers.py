from rest_framework import serializers
from .models import User,Profile,Restaurant
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields =['email', 'password', 'first_name', 'last_name']

    def create(self,validated_data):
        print(validated_data)
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        return user
    

class ProfileSerailizer(serializers.ModelSerializer):
    # first_name = serializers.CharField(source="user.first_name", read_only= True)
    # last_name = serializers.CharField(source="user.last_name", read_only=True)

    class Meta:
        model = Profile
        fields = ["phone_number", "address"]

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", {})

        # update user fields
        user = instance.user
        for attr, value in user_data.items():
            setattr(user, attr, value)

        user.save()

        # update profile fields if any
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        return instance



class ChangepasswordSerializer(serializers.Serializer):
    old_password =  serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_pass(self,value):
        validate_password(value)
        return value
    

# class ProfileSeralizer(serializers.ModelSerializer):
#     class Meta:
#         model = Profile
#         fields =['phone_number', 'address', 'profile_image']



class UserEnableDisableSeralizer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['is_active']



class ChangeUserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields =['role']

    def validate_role(self, value):
        restricted_role =['ADMIN']
        if value in restricted_role:
            raise serializers.ValidationError("You are not allowed to assign admin role here ")
        return value



class ForgetPasswordserializer(serializers.Serializer):
    email = serializers.EmailField()

class VerifyTokenSerializer(serializers.Serializer):
    token = serializers.UUIDField()


class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.UUIDField()
    new_password = serializers.CharField()
    confirm_password = serializers.CharField()


    def validate(self , data):
        if data["new_password"] != data["confirm_password"]:
            raise serializers.ValidationError("password could not match")
        return data 
    

class RestaurantSeralizer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        # fields = "__all__"
        exclude =['owner']
        read_only_fields= ['status', 'is_active']


class PendingRestaurantSerializer(serializers.ModelSerializer):
        owner_email = serializers.CharField(source="owner.email", read_only=True)
        class Meta:
            model = Restaurant
            fields =["id", "name", "address", "status", "owner_email", "created_at"]



class ApprovePendingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields =['status']

    def validate_status(self,value):
        # status =['APPROVED', 'REJECTED']
        if value not in ['APPROVED', 'REJECTED']:
            raise serializers.ValidationError("Status must be APPROVED or REJECTED")
        return value

            

