from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register('register', views.CompanyRegistrationViewSet, basename='company-registration')
router.register('', views.CompanyViewSet, basename='company')

urlpatterns = [
    path('', include(router.urls)),
]