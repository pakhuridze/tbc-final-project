from celery import shared_task
from django.core.mail import send_mail
from django.utils import timezone
from django.template.loader import render_to_string
from .models import Job, JobApplication


@shared_task
def notify_application_received(application_id):
    """
    აპლიკაციის მიღების შეტყობინება
    """
    try:
        application = JobApplication.objects.select_related(
            'job',
            'applicant__user',
            'job__company'
        ).get(id=application_id)

        # აპლიკანტისთვის
        applicant_context = {
            'name': application.applicant.user.get_full_name(),
            'job_title': application.job.title,
            'company': application.job.company.name
        }

        send_mail(
            subject='თქვენი აპლიკაცია მიღებულია',
            message=f'მადლობა {application.job.title} პოზიციაზე აპლიკაციისთვის',
            from_email='noreply@jobily.ge',
            recipient_list=[application.applicant.user.email],
            html_message=render_to_string(
                'jobs/emails/application_received.html',
                applicant_context
            )
        )

        # დამსაქმებლისთვის
        employer_context = {
            'applicant': application.applicant.user.get_full_name(),
            'job_title': application.job.title
        }

        send_mail(
            subject='ახალი აპლიკაცია',
            message=f'ახალი აპლიკაცია მიღებულია {application.job.title} პოზიციაზე',
            from_email='noreply@jobily.ge',
            recipient_list=[application.job.posted_by.email],
            html_message=render_to_string(
                'jobs/emails/new_application.html',
                employer_context
            )
        )

        return f"Notifications sent for application {application_id}"

    except JobApplication.DoesNotExist:
        return f"Application {application_id} not found"


@shared_task
def update_job_views(job_id):
    """
    ვაკანსიის ნახვების განახლება
    """
    try:
        job = Job.objects.get(id=job_id)
        job.views_count += 1
        job.save(update_fields=['views_count'])
        return f"Views updated for job {job_id}"
    except Job.DoesNotExist:
        return f"Job {job_id} not found"