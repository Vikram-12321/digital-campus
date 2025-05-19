"""
apps/search/forms.py

Form for performing searches across posts, users, events, and clubs.

Author: Vikram Bhojanala  
Last updated: 2025-05-09
"""

from django import forms


class SearchForm(forms.Form):
    """
    Search form for querying content across multiple models.

    Fields:
        - query:     user-entered search string
        - filter_by: optional model type to filter results by
        - order_by:  optional field to order results
    """

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'class': 'form-control mr-sm-2',
            'aria-label': 'Search input',
        })
    )

    FILTER_CHOICES = [
        ('all', 'All'),
        ('posts', 'Posts'),
        ('users', 'People'),
        ('clubs', 'Clubs'),
        ('events', 'Events'),
    ]

    filter_by = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        widget=forms.HiddenInput()  # Swap to Select() if making filter visible
    )

    ORDER_CHOICES = [
        ('date_posted', 'Date Posted'),
        ('title', 'Title'),
        ('username', 'Username'),
    ]

    order_by = forms.ChoiceField(
        choices=ORDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control mr-sm-2',
            'aria-label': 'Sort search results',
        })
    )
