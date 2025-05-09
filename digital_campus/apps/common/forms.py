from django import forms


class SearchForm(forms.Form):
    """
    Search form for querying content across posts, users, events, and clubs.
    Includes:
    - query: search input
    - filter_by: hidden or user-selected filter category
    - order_by: sort option for search results
    """

    query = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search...',
            'class': 'form-control mr-sm-2'
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
        widget=forms.HiddenInput()  # Change to Select if you want visible filter bar
    )

    ORDER_CHOICES = [
        ('date_posted', 'Date Posted'),
        ('title', 'Title'),
        ('username', 'Username'),
    ]

    order_by = forms.ChoiceField(
        choices=ORDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control mr-sm-2'})
    )
