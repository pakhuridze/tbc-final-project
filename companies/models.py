from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class Company(models.Model):
    COMPANY_SIZE_CHOICES = [
        ('1-10', '1-10'),
        ('11-50', '11-50'),
        ('51-200', '51-200'),
        ('201-500', '201-500'),
        ('501-1000', '501-1000'),
        ('1000+', '1000+'),
    ]

    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    industry = models.CharField(max_length=100, blank=True)
    company_size = models.CharField(
        max_length=20,
        choices=COMPANY_SIZE_CHOICES,
        blank=True
    )
    founded_year = models.PositiveIntegerField(
        validators=[
            MinValueValidator(1800),
            MaxValueValidator(2024)
        ],
        null=True,
        blank=True
    )

    website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    twitter = models.URLField(blank=True)
    facebook = models.URLField(blank=True)

    logo = models.ImageField(
        upload_to='company_logos/',
        default='company_logos/default.png',
        blank=True
    )

    location = models.CharField(max_length=200, blank=True)
    headquarters = models.CharField(max_length=200, blank=True)

    contact_email = models.EmailField(blank=True)
    phone_number = models.CharField(max_length=20, blank=True)

    is_verified = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Companies"
        ordering = ['-created_at']

    def __str__(self):
        return self.name