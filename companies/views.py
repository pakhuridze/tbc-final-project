# companies/views.py
from rest_framework import viewsets, status, permissions
from rest_framework.views import APIView
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.db import transaction
from .models import Company
from .serializers import CompanySerializer, CompanyRegistrationSerializer, CompanyListSerializer


class CompanyViewSet(viewsets.ModelViewSet):
    queryset = Company.objects.all()
    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return CompanyListSerializer
        return CompanySerializer

    @action(detail=False, methods=['GET'])
    def all_companies(self, request):
        """Get all companies list with pagination"""
        companies = self.get_queryset()
        page = self.paginate_queryset(companies)

        if page is not None:
            serializer = CompanyListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = CompanyListSerializer(companies, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = Company.objects.all()

        # Filters
        industry = self.request.query_params.get('industry', None)
        location = self.request.query_params.get('location', None)
        company_size = self.request.query_params.get('company_size', None)

        if industry:
            queryset = queryset.filter(industry__icontains=industry)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if company_size:
            queryset = queryset.filter(company_size=company_size)

        return queryset.order_by('-created_at')

    @action(detail=False, methods=['GET'])
    def me(self, request):
        """Get current user's company"""
        try:
            company = request.user.employer_profile.company
            serializer = self.get_serializer(company)
            return Response(serializer.data)
        except:
            return Response(
                {"detail": "No company found for this user"},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['GET'])
    def filters(self, request):
        """Get unique values for filters"""
        industries = Company.objects.values_list('industry', flat=True).distinct()
        locations = Company.objects.values_list('location', flat=True).distinct()
        company_sizes = dict(Company.COMPANY_SIZE_CHOICES)

        return Response({
            'industries': sorted(filter(None, industries)),
            'locations': sorted(filter(None, locations)),
            'company_sizes': company_sizes
        })


class CompanyRegistrationViewSet(viewsets.ViewSet):
    permission_classes = [AllowAny]
    serializer_class = CompanyRegistrationSerializer

    def create(self, request):
        """Handle POST request for company registration"""
        serializer = self.serializer_class(data=request.data)

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                result = serializer.save()
                refresh = RefreshToken.for_user(result['user'])

                return Response({
                    'success': True,
                    'company': CompanySerializer(result['company']).data,
                    'user': {
                        'email': result['user'].email,
                        'first_name': result['user'].first_name,
                        'last_name': result['user'].last_name,
                        'user_type': result['user'].user_type
                    },
                    'tokens': {
                        'refresh': str(refresh),
                        'access': str(refresh.access_token),
                    }
                }, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({
                'success': False,
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)