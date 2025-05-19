"""
apps/common/views.py

Contains shared views for the Digital Campus project, including:
- Static pages (About, Account)
- Autocomplete for course selection

Integrates home feed scoring (recency, relevance) via modular imports.

Author: Vikram Bhojanala  
Last updated: 2025-05-09
"""

from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from dal import autocomplete
from .models import Course


# ————————————————————————————————————
# Static Pages
# ————————————————————————————————————
def about(request: HttpRequest) -> HttpResponse:
    """Render the About page."""
    return render(request, 'digital_campus/about.html')


def account(request: HttpRequest) -> HttpResponse:
    """Render the Account page."""
    return render(request, 'digital_campus/account.html')


# ————————————————————————————————————
# Autocomplete
# ————————————————————————————————————
class CourseAutocomplete(autocomplete.Select2QuerySetView):
    """
    Autocomplete view for course selection using django-autocomplete-light.
    Returns a queryset of matching courses.
    """

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Course.objects.none()

        qs = Course.objects.all()

        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
