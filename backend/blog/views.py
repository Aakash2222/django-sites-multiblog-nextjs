"""
API views for the blog application.

These views use Django's Sites framework to automatically filter
articles based on the current domain making the request.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.sites.shortcuts import get_current_site
from .models import Article
from .serializers import ArticleSerializer


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
        current_site = get_current_site(self.request)
        
        # Return only published articles linked to the current site
        return Article.objects.filter(
            published=True,
            sites=current_site
        ).distinct()

    @action(detail=False, methods=['get'])
    def current_site(self, request):
        """
        Utility endpoint to get information about the current site.
        Useful for debugging and frontend display.
        """
        current_site = get_current_site(request)
        return Response({
            'id': current_site.id,
            'domain': current_site.domain,
            'name': current_site.name,
        })
