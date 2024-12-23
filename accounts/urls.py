from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    JobSeekerProfileViewSet,
    EmployerProfileViewSet, EducationViewSet, WorkExperienceViewSet, SkillViewSet
)

router = DefaultRouter()

router.register('job-seekers', JobSeekerProfileViewSet, basename='job-seeker')
router.register(r'employers', EmployerProfileViewSet)
router.register(r'education', EducationViewSet)
router.register(r'work-experience', WorkExperienceViewSet)
router.register('skills', SkillViewSet, basename='skill')

urlpatterns = [
    path('', include(router.urls)),
]

