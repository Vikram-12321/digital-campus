from django import forms

class SearchForm(forms.Form):
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
        ['clubs', 'Clubs'],
        ['events', 'Events']

    ]
    filter_by = forms.ChoiceField(
        choices=FILTER_CHOICES,
        required=False,
        # widget=forms.Select(attrs={'class': 'form-control mr-sm-2'})
        widget=forms.HiddenInput()
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
