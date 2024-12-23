from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('jobs', views.JobViewSet, basename='job')
router.register('applications', views.JobApplicationViewSet, basename='job-application')

urlpatterns = [
    path('', include(router.urls)),
]