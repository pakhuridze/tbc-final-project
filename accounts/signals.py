from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache  # Import for cache operations
from .models import CustomUser, JobSeekerProfile, EmployerProfile, Skill  # Ensure these models exist in your app

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        if instance.user_type == 'job_seeker':
            JobSeekerProfile.objects.create(user=instance)
        elif instance.user_type == 'employer' and not hasattr(instance, '_skip_profile_creation'):
            # Create an EmployerProfile only if the company exists
            if hasattr(instance, '_company'):
                EmployerProfile.objects.create(user=instance, company=instance._company)

@receiver(post_save, sender=Skill)
@receiver(post_delete, sender=Skill)
def invalidate_skill_cache(sender, **kwargs):
    cache_key = "categorized_skills"
    cache.delete(cache_key)
