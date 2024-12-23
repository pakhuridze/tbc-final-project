from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from .models import Job, JobApplication
from .serializers import (
    JobSerializer,
    JobListSerializer,
    JobApplicationSerializer
)
from .tasks import notify_application_received, update_job_views


class JobViewSet(viewsets.ModelViewSet):
    queryset = Job.objects.all()
    serializer_class = JobSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return JobListSerializer
        return JobSerializer

    def get_queryset(self):
        queryset = Job.objects.filter(status='published')

        # Search
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(company__name__icontains=search)
            )

        # Filters
        job_type = self.request.query_params.get('job_type', None)
        experience_level = self.request.query_params.get('experience_level', None)
        location = self.request.query_params.get('location', None)
        is_remote = self.request.query_params.get('is_remote', None)
        salary_min = self.request.query_params.get('salary_min', None)
        company = self.request.query_params.get('company', None)
        skills = self.request.query_params.getlist('skills', None)

        if job_type:
            queryset = queryset.filter(job_type=job_type)
        if experience_level:
            queryset = queryset.filter(experience_level=experience_level)
        if location:
            queryset = queryset.filter(location__icontains=location)
        if is_remote:
            queryset = queryset.filter(is_remote=is_remote)
        if salary_min:
            queryset = queryset.filter(salary_min__gte=salary_min)
        if company:
            queryset = queryset.filter(company_id=company)
        if skills:
            queryset = queryset.filter(skills__id__in=skills).distinct()

        # Sorting
        sort_by = self.request.query_params.get('sort_by', '-created_at')
        allowed_sorts = {
            'created_at': 'created_at',
            '-created_at': '-created_at',
            'salary': 'salary_min',
            '-salary': '-salary_min',
            'title': 'title',
            '-title': '-title',
            'company': 'company__name',
            '-company': '-company__name',
        }
        if sort_by in allowed_sorts:
            queryset = queryset.order_by(allowed_sorts[sort_by])

        return queryset

    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # Asynchronously increment view count
        update_job_views.delay(self.get_object().id)
        return response

    def perform_create(self, serializer):
        if not hasattr(self.request.user, 'employer_profile'):
            raise permissions.PermissionDenied("Only employers can post jobs")

        if not self.request.user.employer_profile.can_post_jobs:
            raise permissions.PermissionDenied("You don't have permission to post jobs")

        serializer.save(
            company=self.request.user.employer_profile.company,
            posted_by=self.request.user
        )

    def perform_update(self, serializer):
        job = self.get_object()
        if job.posted_by != self.request.user and not self.request.user.employer_profile.is_company_admin:
            raise permissions.PermissionDenied("You don't have permission to edit this job")
        serializer.save()

    def perform_destroy(self, instance):
        if instance.posted_by != self.request.user and not self.request.user.employer_profile.is_company_admin:
            raise permissions.PermissionDenied("You don't have permission to delete this job")
        instance.delete()

    @action(detail=True, methods=['post'])
    def apply(self, request, pk=None):
        job = self.get_object()

        # Check if user is a job seeker
        if not hasattr(request.user, 'job_seeker_profile'):
            return Response(
                {"error": "Only job seekers can apply for jobs"},
                status=status.HTTP_403_FORBIDDEN
            )

        # Check if job is still accepting applications
        if job.status != 'published':
            return Response(
                {"error": "This job is no longer accepting applications"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Check if user has already applied
        if JobApplication.objects.filter(
                job=job,
                applicant=request.user.job_seeker_profile
        ).exists():
            return Response(
                {"error": "You have already applied for this job"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = JobApplicationSerializer(data={
            'job': job.id,
            'applicant': request.user.job_seeker_profile.id,
            'cover_letter': request.data.get('cover_letter', ''),
            'resume': request.data.get('resume', None)
        })

        if serializer.is_valid():
            application = serializer.save()
            # Send notifications asynchronously
            notify_application_received.delay(application.id)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def similar_jobs(self, request, pk=None):
        """Get similar jobs based on skills and job type"""
        job = self.get_object()
        similar_jobs = Job.objects.filter(
            status='published',
            skills__in=job.skills.all()
        ).exclude(
            id=job.id
        ).annotate(
            matched_skills=Count('skills')
        ).filter(
            matched_skills__gt=0
        ).order_by('-matched_skills')[:5]

        serializer = JobListSerializer(similar_jobs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_jobs(self, request):
        """Get jobs posted by the current user's company"""
        if not hasattr(request.user, 'employer_profile'):
            return Response(
                {"error": "Only employers can view their jobs"},
                status=status.HTTP_403_FORBIDDEN
            )

        jobs = Job.objects.filter(company=request.user.employer_profile.company)
        serializer = JobSerializer(jobs, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """Get job posting statistics for the company"""
        if not hasattr(request.user, 'employer_profile'):
            return Response(
                {"error": "Only employers can view statistics"},
                status=status.HTTP_403_FORBIDDEN
            )

        company_jobs = Job.objects.filter(company=request.user.employer_profile.company)
        active_jobs = company_jobs.filter(status='published').count()
        total_applications = JobApplication.objects.filter(job__in=company_jobs).count()

        # Applications by status
        applications_by_status = JobApplication.objects.filter(
            job__in=company_jobs
        ).values('status').annotate(
            count=Count('id')
        )

        return Response({
            'active_jobs': active_jobs,
            'total_applications': total_applications,
            'applications_by_status': applications_by_status,
        })

class JobApplicationViewSet(viewsets.ModelViewSet):
    serializer_class = JobApplicationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'job_seeker_profile'):
            return JobApplication.objects.filter(applicant=self.request.user.job_seeker_profile)
        elif hasattr(self.request.user, 'employer_profile'):
            return JobApplication.objects.filter(job__company=self.request.user.employer_profile.company)
        return JobApplication.objects.none()