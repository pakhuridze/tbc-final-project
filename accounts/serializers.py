from django.db import transaction
from .models import CustomUser, JobSeekerProfile, EmployerProfile, Education, WorkExperience
from rest_framework import serializers
from accounts.models import Skill

class CustomUserSerializer(serializers.ModelSerializer):
    profile_picture = serializers.ImageField(max_length=None, use_url=True, required=False)

    class Meta:
        model = CustomUser
        fields = ('id', 'email', 'username', 'password', 'user_type', 'is_verified', 'profile_picture')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomUser.objects.create_user(**validated_data)
        return user


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class WorkExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkExperience
        fields = '__all__'



class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'created_at', 'updated_at']


class JobSeekerProfileSerializer(serializers.ModelSerializer):
    education = EducationSerializer(many=True, read_only=True)
    work_experience = WorkExperienceSerializer(many=True, read_only=True)
    user = CustomUserSerializer(read_only=True)
    skills = SkillSerializer(many=True, read_only=True)
    skills_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Skill.objects.all(), source='skills', required=False
    )

    class Meta:
        model = JobSeekerProfile
        fields = '__all__'
        read_only_fields = ('user',)

    def validate_current_salary(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Salary cannot be negative")
        return value

    def validate_expected_salary(self, value):
        if value and value < 0:
            raise serializers.ValidationError("Expected salary cannot be negative")
        return value

    def validate_phone_number(self, value):
        # Add your phone number validation logic here
        if value and not value.startswith('+'):
            raise serializers.ValidationError("Phone number must start with '+'")
        return value


class EmployerProfileSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)

    class Meta:
        model = EmployerProfile
        fields = '__all__'


class JobSeekerRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm', 'profile_picture']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        profile_picture = validated_data.pop('profile_picture', None)

        # Create the CustomUser instance
        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            user_type='job_seeker'
        )

        # Save the profile picture if provided
        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        # Do not manually create JobSeekerProfile here, signals handle it
        return user


class EmployerRegistrationSerializer(serializers.ModelSerializer):
    password_confirm = serializers.CharField(style={'input_type': 'password'}, write_only=True)
    company_id = serializers.IntegerField(write_only=True)
    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password', 'password_confirm', 'profile_picture', 'company_id']
        extra_kwargs = {
            'password': {'write_only': True},
            'email': {'required': True},
            'username': {'required': True}
        }

    def validate_email(self, value):
        if CustomUser.objects.filter(email=value).exists():
            raise serializers.ValidationError("This email is already registered.")
        return value

    def validate_username(self, value):
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError("This username is already taken.")
        return value

    def validate(self, data):
        if data.get('password') != data.get('password_confirm'):
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('password_confirm', None)
        company_id = validated_data.pop('company_id')
        profile_picture = validated_data.pop('profile_picture', None)

        user = CustomUser.objects.create_user(
            email=validated_data['email'],
            username=validated_data['username'],
            password=validated_data['password'],
            user_type='employer'
        )

        if profile_picture:
            user.profile_picture = profile_picture
            user.save()

        EmployerProfile.objects.create(
            user=user,
            company_id=company_id
        )
        return user
