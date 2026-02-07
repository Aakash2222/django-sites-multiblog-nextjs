"""
Management command to set up initial sites for the multi-site blog.

Usage:
    python manage.py setup_sites
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Set up initial sites (blog1.com and blog2.com) for the multi-site blog'

    def handle(self, *args, **options):
        # Create or update Site 1
        site1, created = Site.objects.get_or_create(
            id=1,
            defaults={'domain': 'blog1.com', 'name': 'Blog 1'}
        )
        if not created:
            site1.domain = 'blog1.com'
            site1.name = 'Blog 1'
            site1.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Site 1: {site1.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created Site 1: {site1.domain}'))

        # Create or update Site 2
        site2, created = Site.objects.get_or_create(
            id=2,
            defaults={'domain': 'blog2.com', 'name': 'Blog 2'}
        )
        if not created:
            site2.domain = 'blog2.com'
            site2.name = 'Blog 2'
            site2.save()
            self.stdout.write(self.style.SUCCESS(f'Updated Site 2: {site2.domain}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created Site 2: {site2.domain}'))

        self.stdout.write(self.style.SUCCESS('\nSites setup complete!'))
        self.stdout.write(f'Site 1: {site1.domain} (ID: {site1.id})')
        self.stdout.write(f'Site 2: {site2.domain} (ID: {site2.id})'))
