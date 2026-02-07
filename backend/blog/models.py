"""
Blog models for multi-site blog system.

The Article model uses Django's Sites framework to allow articles
to be published to one or multiple sites (domains).
"""
from django.db import models
from django.contrib.sites.models import Site


class Article(models.Model):
    """
    Article model for blog posts.
    
    Uses ManyToManyField to Site to allow articles to be published
    to one or multiple sites. This enables:
    - Publishing to a single site (e.g., blog1.com only)
    - Publishing to multiple sites (e.g., both blog1.com and blog2.com)
    
    The sites field is required - articles must be associated with
    at least one site to be displayed.
    """
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.BooleanField(default=False)
    # ManyToManyField to Site allows articles to be linked to multiple sites
    # This is the core of the multi-site functionality
    sites = models.ManyToManyField(Site, related_name='articles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title
