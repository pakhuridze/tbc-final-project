# Generated by Django 5.1.4 on 2024-12-23 12:47

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('companies', '0001_initial'),
        ('jobs', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Job',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('location', models.CharField(max_length=200)),
                ('job_type', models.CharField(choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship'), ('temporary', 'Temporary')], max_length=20)),
                ('experience_level', models.CharField(choices=[('entry', 'Entry Level'), ('junior', 'Junior'), ('mid', 'Mid Level'), ('senior', 'Senior'), ('lead', 'Lead'), ('manager', 'Manager')], max_length=20)),
                ('description', models.TextField()),
                ('requirements', models.TextField()),
                ('responsibilities', models.TextField()),
                ('salary_type', models.CharField(choices=[('fixed', 'Fixed'), ('range', 'Range'), ('negotiable', 'Negotiable')], max_length=20)),
                ('salary_min', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('salary_max', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('status', models.CharField(choices=[('draft', 'Draft'), ('published', 'Published'), ('closed', 'Closed'), ('archived', 'Archived')], default='draft', max_length=20)),
                ('is_remote', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('expires_at', models.DateTimeField(blank=True, null=True)),
                ('views_count', models.PositiveIntegerField(default=0)),
                ('applications_count', models.PositiveIntegerField(default=0)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='jobs', to='companies.company')),
                ('posted_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='posted_jobs', to=settings.AUTH_USER_MODEL)),
                ('skills', models.ManyToManyField(related_name='jobs', to='accounts.skill')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='JobApplication',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.CharField(choices=[('pending', 'Pending'), ('review', 'Under Review'), ('shortlisted', 'Shortlisted'), ('rejected', 'Rejected'), ('accepted', 'Accepted')], default='pending', max_length=20)),
                ('cover_letter', models.TextField(blank=True)),
                ('resume', models.FileField(blank=True, null=True, upload_to='job_applications/resumes/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('applicant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='accounts.jobseekerprofile')),
                ('job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='applications', to='jobs.job')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.DeleteModel(
            name='Skill',
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['-created_at'], name='jobs_job_created_77460a_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['status'], name='jobs_job_status_7d017a_idx'),
        ),
        migrations.AddIndex(
            model_name='job',
            index=models.Index(fields=['company'], name='jobs_job_company_9ee5ea_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='jobapplication',
            unique_together={('job', 'applicant')},
        ),
    ]
