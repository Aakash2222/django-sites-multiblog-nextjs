"""
Serializers for the blog API.
"""
from rest_framework import serializers
from .models import Article


class ArticleSerializer(serializers.ModelSerializer):
    """
    Serializer for Article model.
    
    Exposes article data to the API, including title, content,
    and creation date. The sites field is not exposed as the
    API automatically filters by the current site.
    """
    class Meta:
        model = Article
        fields = ['id', 'title', 'content', 'created_at']
        read_only_fields = ['id', 'created_at']
