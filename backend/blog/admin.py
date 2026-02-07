"""
Django admin configuration for the blog app.

Configures the Article admin to allow selecting one or multiple sites,
with site selection being required.
"""
from django.contrib import admin
from django.contrib.sites.models import Site
from django import forms
from .models import Article


class ArticleAdminForm(forms.ModelForm):
    """
    Custom form for Article admin that makes site selection required.
    """
    sites = forms.ModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=True,
        help_text="Select one or more sites for this article. At least one site is required.",
    )

    class Meta:
        model = Article
        fields = '__all__'


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    """
    Admin interface for Article model.
    
    Allows selecting one or multiple sites for each article.
    Site selection is required - articles must be associated with
    at least one site.
    """
    form = ArticleAdminForm
    list_display = ['title', 'published', 'created_at', 'get_sites']
    list_filter = ['published', 'created_at', 'sites']
    search_fields = ['title', 'content']
    filter_horizontal = ['sites']
    
    fieldsets = (
        ('Content', {
            'fields': ('title', 'content')
        }),
        ('Publishing', {
            'fields': ('published', 'sites'),
            'description': 'Select one or more sites for this article. At least one site is required.'
        }),
    )

    def get_sites(self, obj):
        """Display comma-separated list of sites for this article."""
        return ", ".join([site.domain for site in obj.sites.all()])
    get_sites.short_description = 'Sites'
