# companies/serializers.py
from rest_framework import serializers
from django.db import transaction
from accounts.models import CustomUser, EmployerProfile
from .models import Company


class CompanyRegistrationSerializer(serializers.Serializer):
    company_name = serializers.CharField(max_length=200)
    industry = serializers.CharField(max_length=100)
    company_size = serializers.ChoiceField(choices=Company.COMPANY_SIZE_CHOICES)
    website = serializers.URLField(required=False)
    location = serializers.CharField(max_length=200)
    first_name = serializers.CharField(max_length=150)
    last_name = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    job_title = serializers.CharField(max_length=100)
    department = serializers.CharField(max_length=100)

    def create(self, validated_data):
        with transaction.atomic():
            # Create company
            company = Company.objects.create(
                name=validated_data['company_name'],
                industry=validated_data['industry'],
                company_size=validated_data['company_size'],
                website=validated_data.get('website', ''),
                location=validated_data['location']
            )

            # Create user
            user = CustomUser.objects.create_user(
                username=validated_data['email'],
                email=validated_data['email'],
                password=validated_data['password'],
                first_name=validated_data['first_name'],
                last_name=validated_data['last_name'],
                user_type='employer'
            )

            # Create employer profile
            EmployerProfile.objects.create(
                user=user,
                company=company,
                job_title=validated_data['job_title'],
                department=validated_data['department']
            )

            return {
                'user': user,
                'company': company
            }
class CompanySerializer(serializers.ModelSerializer):
    class Meta:
        model = Company
        fields = '__all__'


class CompanyListSerializer(serializers.ModelSerializer):
    """Serializer for listing companies with minimal information"""
    employees_count = serializers.SerializerMethodField()

    class Meta:
        model = Company
        fields = [
            'id',
            'name',
            'logo',
            'industry',
            'location',
            'company_size',
            'website',
            'is_verified',
            'employees_count'
        ]

    def get_employees_count(self, obj):
        return obj.employers.count()