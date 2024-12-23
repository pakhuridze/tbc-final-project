from django.core.management.base import BaseCommand
from accounts.models import Skill

class Command(BaseCommand):
    help = 'Creates default skills'

    def handle(self, *args, **kwargs):
        default_skills = {
            'Programming Languages': [
                'Python', 'JavaScript', 'Java', 'C++', 'Ruby', 'PHP',
                'Swift', 'TypeScript', 'Go', 'Rust'
            ],
            'Frameworks': [
                'Django', 'React', 'Angular', 'Vue.js', 'Flask',
                'Spring Boot', 'Laravel', 'Express.js', 'Ruby on Rails'
            ],
            'Databases': [
                'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'SQLite',
                'Oracle', 'Cassandra', 'Microsoft SQL Server'
            ],
            'DevOps': [
                'Docker', 'Kubernetes', 'AWS', 'Jenkins', 'Git',
                'Linux', 'CI/CD', 'Azure', 'Google Cloud'
            ],
            'Frontend': [
                'HTML', 'CSS', 'SASS', 'Bootstrap', 'Tailwind CSS',
                'jQuery', 'Redux', 'Webpack', 'Material UI'
            ],
            'Mobile': [
                'React Native', 'Flutter', 'iOS', 'Android', 'Xamarin',
                'Kotlin', 'SwiftUI', 'Mobile App Development'
            ],
            'Other': [
                'Agile', 'Scrum', 'REST API', 'GraphQL', 'Unit Testing',
                'UI/UX Design', 'Problem Solving', 'Team Leadership'
            ]
        }

        for category, skills in default_skills.items():
            for skill_name in skills:
                skill, created = Skill.objects.get_or_create(
                    name=skill_name,
                    defaults={'category': category}
                )
                if created:
                    self.stdout.write(
                        self.style.SUCCESS(f'Created skill "{skill_name}" in category "{category}"')
                    )
                else:
                    self.stdout.write(
                        self.style.WARNING(f'Skill "{skill_name}" already exists')
                    )