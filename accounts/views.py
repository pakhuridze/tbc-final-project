import json
import requests
from django.core import cache
from django.db import transaction
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import Skill
from .models import JobSeekerProfile, EmployerProfile, Education, WorkExperience
from .serializers import (
    CustomUserSerializer, JobSeekerProfileSerializer,
    EmployerProfileSerializer, EducationSerializer, WorkExperienceSerializer, EmployerRegistrationSerializer,
    JobSeekerRegistrationSerializer, SkillSerializer
)
from decouple import config

def get_openai_api_key():
    return config('OPENAI_API_KEY')

class JobSeekerProfileViewSet(viewsets.ModelViewSet):
    queryset = JobSeekerProfile.objects.all()
    serializer_class = JobSeekerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return JobSeekerProfile.objects.all()
        return JobSeekerProfile.objects.filter(user=self.request.user)

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def me(self, request):
        if request.method == 'GET':
            try:
                profile = JobSeekerProfile.objects.get(user=request.user)
                profile_serializer = self.get_serializer(profile)
                user_serializer = CustomUserSerializer(request.user)

                return Response({
                    'user': user_serializer.data,
                    'profile': profile_serializer.data
                })
            except JobSeekerProfile.DoesNotExist:
                return Response({
                    'user': CustomUserSerializer(request.user).data,
                    'profile': None
                })

        # PUT and PATCH methods are for updating the profile
        elif request.method in ['PUT', 'PATCH']:
            try:
                profile = JobSeekerProfile.objects.get(user=request.user)
                serializer = self.get_serializer(
                    profile,
                    data=request.data,
                    partial=request.method == 'PATCH'
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()

                return Response({
                    'user': CustomUserSerializer(request.user).data,
                    'profile': serializer.data
                })
            except JobSeekerProfile.DoesNotExist:
                return Response(
                    {"detail": "Profile not found"},
                    status=status.HTTP_404_NOT_FOUND
                )

    @action(detail=False, methods=['GET', 'PUT', 'PATCH'])
    def generate_about_me(self, request, *args, **kwargs):
        profile = JobSeekerProfile.objects.get(user=request.user)
        skills = ', '.join(profile.skills.all().values_list('name', flat=True))

        prompt = f"my name is {request.user.first_name} Generate cv like text. 150 characters. my skills are {skills}"
        print(f'Skills: {skills}')

        try:
            # Send request to OpenAI API
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {get_openai_api_key()}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "gpt-4o-mini",
                    "messages": [
                        {
                            "role": "system",
                            "content": "Create about me text. for Job Seeker. language Georgian"
                        },
                        {"role": "user", "content": prompt}
                    ],
                    "temperature": 0.7
                }
            )
            response.raise_for_status()

            # Parse the OpenAI API response
            about_me_data = response.json()
            content = about_me_data["choices"][0]["message"]["content"]

            # Update the JobSeekerProfile's about_me field
            try:
                profile = JobSeekerProfile.objects.get(user=request.user)
                profile.about_me = content
                profile.save()

                return Response({
                    "message": "About me generated and updated successfully.",
                    "about_me": content
                }, status=status.HTTP_200_OK)

            except JobSeekerProfile.DoesNotExist:
                return Response(
                    {"detail": "Profile not found for the user."},
                    status=status.HTTP_404_NOT_FOUND
                )

        except requests.exceptions.HTTPError as e:
            print("HTTP error:", response.text)
            return Response(
                {"error": "OpenAI API error", "details": response.text},
                status=status.HTTP_400_BAD_REQUEST
            )
        except (json.JSONDecodeError, KeyError) as e:
            print("Invalid response format:", response.text)
            return Response(
                {"error": "Invalid response from OpenAI", "details": response.text},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        if JobSeekerProfile.objects.filter(user=request.user).exists():
            return Response(
                {"detail": "Profile already exists"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)

        response_data = {
            'user': CustomUserSerializer(request.user).data,
            'profile': serializer.data
        }

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class EmployerProfileViewSet(viewsets.ModelViewSet):
    queryset = EmployerProfile.objects.all()
    serializer_class = EmployerProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.action == 'list':
            return EmployerProfile.objects.filter(user=self.request.user)
        return EmployerProfile.objects.all()


class EducationViewSet(viewsets.ModelViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Education.objects.filter(profile__user=self.request.user)


class WorkExperienceViewSet(viewsets.ModelViewSet):
    queryset = WorkExperience.objects.all()
    serializer_class = WorkExperienceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return WorkExperience.objects.filter(profile__user=self.request.user)


class JobSeekerRegistrationView(APIView):
    permission_classes = [AllowAny]

    @transaction.atomic
    def post(self, request):
        serializer = JobSeekerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                refresh = RefreshToken.for_user(user)

                return Response({
                    "user": {
                        "email": user.email,
                        "username": user.username,
                    },
                    "message": "Job Seeker registered successfully",
                    "tokens": {
                        "refresh": str(refresh),
                        "access": str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)

            except Exception as e:
                # Log the exception for debugging
                print(f"Error during registration: {e}")
                return Response({
                    "error": f"Registration failed. Error: {str(e)}"
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmployerRegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = EmployerRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)

            return Response({
                'user': serializer.data,
                'message': 'Employer registered successfully',
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkillViewSet(viewsets.ModelViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['POST'])
    def add_skills(self, request):
        try:
            # Get user profile
            profile = JobSeekerProfile.objects.get(user=request.user)

            # Get skill IDs from request
            skill_ids = request.data.get('skills', [])

            # Verify skills exist
            skills = Skill.objects.filter(id__in=skill_ids)
            if len(skills) != len(skill_ids):
                return Response(
                    {"detail": "ზოგიერთი სკილი ვერ მოიძებნა"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Add new skills to existing ones
            current_skills = set(profile.skills.values_list('id', flat=True))
            new_skills = set(skill_ids)
            all_skills = list(current_skills.union(new_skills))

            # Update profile skills
            profile.skills.set(all_skills)

            # Return updated profile
            serializer = JobSeekerProfileSerializer(profile)
            return Response(serializer.data)

        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"detail": "პროფილი ვერ მოიძებნა"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['POST'])
    def remove_skills(self, request):
        """Remove skills from user profile"""
        try:
            profile = JobSeekerProfile.objects.get(user=request.user)
            skill_ids = request.data.get('skills', [])

            # Remove specified skills
            current_skills = set(profile.skills.values_list('id', flat=True))
            skills_to_remove = set(skill_ids)
            remaining_skills = list(current_skills - skills_to_remove)

            profile.skills.set(remaining_skills)

            serializer = JobSeekerProfileSerializer(profile)
            return Response(serializer.data)
        except JobSeekerProfile.DoesNotExist:
            return Response(
                {"detail": "Profile Not Found"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['GET'])
    def by_category(self, request):
        cache_key = "categorized_skills"
        categorized_skills = cache.get(cache_key)

        if not categorized_skills:
            skills = Skill.objects.all()
            categorized_skills = {}

            for skill in skills:
                if skill.category not in categorized_skills:
                    categorized_skills[skill.category] = []

                categorized_skills[skill.category].append({
                    'id': skill.id,
                    'name': skill.name,
                    'created_at': skill.created_at
                })

            # Cache the result for 1 hour (3600 seconds)
            cache.set(cache_key, categorized_skills, timeout=3600)

        return Response(categorized_skills)