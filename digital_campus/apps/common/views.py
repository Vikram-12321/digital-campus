from django.shortcuts import render, redirect, get_object_or_404
from dal import autocomplete
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from itertools import chain
from .home_algorithim import recency_score, relevance_score, ALPHA, BETA

#Models
from .models import Course, Notification  
from apps.posts.models import Post
from apps.events.models import Event


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
    
@login_required
def notifications_list(request):
    qs = request.user.notifications.order_by('-timestamp')
    # Mark all as read if you like:
    qs.filter(unread=True).update(unread=False)
    return render(request, 'digital_campus/notifications/list.html', {'notifications': qs})

@login_required
def dismiss_notification(request, pk):
    n = get_object_or_404(Notification, pk=pk, recipient=request.user)
    n.delete()  # or n.unread = False; n.save()
    return redirect(request.META.get('HTTP_REFERER','common:notifications'))
