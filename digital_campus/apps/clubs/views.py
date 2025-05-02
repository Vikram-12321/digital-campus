from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, get_object_or_404
from .models import Club
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import CreateView, DetailView
from django.http import HttpResponseForbidden


## CLUB STUFF ##

@login_required
def join_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    club.members.add(request.user)
    return redirect(request.META.get("HTTP_REFERER", "/events/"))

@login_required
def leave_club(request, pk):
    club = get_object_or_404(Club, pk=pk)
    club.members.remove(request.user)
    return redirect(request.META.get("HTTP_REFERER", "/events/"))

class ClubCreateView(LoginRequiredMixin, CreateView):
    ...
    def form_valid(self, form):
        form.save(creator=self.request.user)
        return super().form_valid(form)
    
    
class ClubDetailView(DetailView):
    model = Club
    template_name = "clubs/detail.html"
    context_object_name = "club"
    slug_field = "slug"
    slug_url_kwarg = "slug"


@login_required
def toggle_featured(request, slug):
    """
    Toggle the `is_featured` flag on a Club.
    Only owners may perform this action.
    """
    club = get_object_or_404(Club, slug=slug)

    # Only owners can feature/unfeature
    if request.user not in club.owners.all():
        return HttpResponseForbidden("You do not have permission to feature this club.")

    club.is_featured = not club.is_featured
    club.save()

    # Redirect back to the club detail page
    return redirect(club.get_absolute_url())