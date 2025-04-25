from django.shortcuts import render
from dal import autocomplete
from .models import Course  # or wherever your Course is


#Models
from apps.posts.models import Post

def home(request):
    context = { 
        'posts': Post.objects.all() 
    }
    return render(request, 'digital_campus/home.html', context)

def about(request):
    return render(request, 'digital_campus/about.html')

def account(request):
    return render(request, 'digital_campus/account.html')

class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # Ensure user is logged in or has permissions if needed
        if not self.request.user.is_authenticated:
            return Course.objects.none()

        qs = Course.objects.all()

        # Filter by user input if necessary:
        if self.q:
            qs = qs.filter(name__icontains=self.q)

        return qs
    
