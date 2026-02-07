"""
API views for the blog application.

These views use Django's Sites framework to automatically filter
articles based on the current domain making the request.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from .models import Article
from .serializers import ArticleSerializer


def get_site_from_request(request):
    """
    Custom site detection that explicitly checks X-Forwarded-Host header.
    
    Django's get_current_site() should use X-Forwarded-Host when USE_X_FORWARDED_HOST=True,
    but we'll explicitly check it to ensure it works correctly.
    """
    # First, try to get host from X-Forwarded-Host (set by Next.js proxy)
    forwarded_host = request.META.get('HTTP_X_FORWARDED_HOST', '')
    if forwarded_host:
        # Strip port if present
        host = forwarded_host.split(':')[0]
        print(f"DEBUG get_site_from_request - Using X-Forwarded-Host: {host}")
        try:
            site = Site.objects.get(domain=host)
            print(f"DEBUG get_site_from_request - Found site: ID={site.id}, Domain={site.domain}")
            return site
        except Site.DoesNotExist:
            print(f"DEBUG get_site_from_request - Site not found for domain: {host}")
    
    # Fallback to standard get_current_site
    print(f"DEBUG get_site_from_request - Falling back to get_current_site()")
    return get_current_site(request)


class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for Article model.
    
    Automatically filters articles based on the current site detected
    from the incoming HTTP request's Host header.
    
    How it works:
    1. get_current_site(request) detects the site from the request's Host header
    2. Only published articles linked to the current site are returned
    3. The same API endpoint works for all domains without code changes
    
    Example:
    - Request to blog1.com/api/articles/ returns only articles for blog1.com
    - Request to blog2.com/api/articles/ returns only articles for blog2.com
    """
    serializer_class = ArticleSerializer

    def get_queryset(self):
        """
        Filter articles by:
        1. published=True (only published articles)
        2. sites contains the current site (detected from request)
        
        This ensures each domain only sees articles assigned to it.
        """
        # Get the current site from the request's Host header
        # This is the core of the multi-site functionality
        # Use custom function that explicitly checks X-Forwarded-Host
        current_site = get_site_from_request(self.request)
        
        # Debug: Log site detection for articles query
        print(f"DEBUG Articles Query - Detected site: ID={current_site.id}, Domain={current_site.domain}")
        
        # Debug: List all articles and their status
        all_articles = Article.objects.all()
        print(f"DEBUG - Total articles in database: {all_articles.count()}")
        for article in all_articles:
            article_sites = [s.domain for s in article.sites.all()]
            print(f"  Article '{article.title}': published={article.published}, sites={article_sites}")
        
        # Return only published articles linked to the current site
        queryset = Article.objects.filter(
            published=True,
            sites=current_site
        ).distinct()
        
        print(f"DEBUG Articles Query - Found {queryset.count()} articles for site {current_site.domain}")
        print(f"DEBUG - Article titles: {[a.title for a in queryset]}")
        
        return queryset

    @action(detail=False, methods=['get'])
    def current_site(self, request):
        """
        Utility endpoint to get information about the current site.
        Useful for debugging and frontend display.
        """
        # Debug: Log request headers to see what Django receives
        print(f"DEBUG - Request headers:")
        print(f"  Host: {request.META.get('HTTP_HOST', 'N/A')}")
        print(f"  X-Forwarded-Host: {request.META.get('HTTP_X_FORWARDED_HOST', 'N/A')}")
        print(f"  SERVER_NAME: {request.META.get('SERVER_NAME', 'N/A')}")
        
        # Use custom function that explicitly checks X-Forwarded-Host
        current_site = get_site_from_request(request)
        
        # Debug: Log detected site
        print(f"DEBUG - Detected site: ID={current_site.id}, Domain={current_site.domain}, Name={current_site.name}")
        
        return Response({
            'id': current_site.id,
            'domain': current_site.domain,
            'name': current_site.name,
            'debug': {
                'http_host': request.META.get('HTTP_HOST', None),
                'x_forwarded_host': request.META.get('HTTP_X_FORWARDED_HOST', None),
                'server_name': request.META.get('SERVER_NAME', None),
            }
        })
