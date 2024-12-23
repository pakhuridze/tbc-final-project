from rest_framework import serializers
from accounts.models import Skill
from .models import Job, JobApplication
from accounts.serializers import SkillSerializer
from companies.serializers import CompanyListSerializer

class JobSerializer(serializers.ModelSerializer):
    skills = SkillSerializer(many=True, read_only=True)
    company = CompanyListSerializer(read_only=True)
    skills_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Skill.objects.all(), source='skills'
    )

    class Meta:
        model = Job
        fields = '__all__'
        read_only_fields = ('views_count', 'applications_count', 'posted_by')

    def create(self, validated_data):
        skills = validated_data.pop('skills', [])
        job = Job.objects.create(**validated_data)
        job.skills.set(skills)
        return job

class JobListSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.name')
    company_logo = serializers.ImageField(source='company.logo')

    class Meta:
        model = Job
        fields = [
            'id', 'title', 'company_name', 'company_logo', 'location',
            'job_type', 'salary_min', 'salary_max', 'created_at',
            'is_remote'
        ]

class JobApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobApplication
        fields = '__all__'
        read_only_fields = ('status',)

    def validate(self, data):
        # Check if user has already applied
        if JobApplication.objects.filter(
            job=data['job'],
            applicant=data['applicant']
        ).exists():
            raise serializers.ValidationError("You have already applied for this job.")
        return data