from django.views import View
from django.views.generic import TemplateView, UpdateView, DeleteView
from django.shortcuts import redirect, get_object_or_404
from django.utils import timezone
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import CreateView, DetailView
from django.utils.timezone import now

from apps.common.models import Notification
from .models import Club, ClubMembership
from .forms import ClubCreateForm
from django.db import models
from django.urls import reverse_lazy
from apps.events.models import Event
from django.contrib.contenttypes.models import ContentType

## CLUB STUFF ##

class JoinClubView(LoginRequiredMixin, View):

    
    def post(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        club.members.add(request.user)
        owners = club.club_membership_set.select_related("profile__user").filter(role="owner")

        for owner_membership in owners:
            Notification.objects.create(
                recipient=owner_membership.profile.user,
                actor=request.user,
                type = "CLUB_JOIN_REQUEST",
                verb=f"has requested to join {club.name}" if club.require_request else f"has joined {club.name}",
                target_ct=ContentType.objects.get_for_model(request.user),
                target_id=request.user.id,
            )

        return redirect(request.META.get("HTTP_REFERER", "/events/"))

class LeaveClubView(LoginRequiredMixin, View):
    def post(self, request, pk, *args, **kwargs):
        club = get_object_or_404(Club, pk=pk)
        club.members.remove(request.user)
        messages.success(request, f"You have left the club '{club.name}'.")
        return redirect(request.META.get("HTTP_REFERER", "/events/"))

class ClubCreateView(LoginRequiredMixin, CreateView):
    model = Club
    form_class = ClubCreateForm
    template_name = "clubs/club_create_user.html"
    success_url = reverse_lazy("clubs:user-clubs")  # or redirect to detail if preferred

    def dispatch(self, request, *args, **kwargs):
        if ClubMembership.objects.filter(
            profile=request.user.profile, role="owner"
        ).count() >= 5:
            messages.warning(request, "You’ve reached your club creation limit (5).")
            return redirect("clubs:user-clubs")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        club = form.save(commit=False)
        if self.request.user.is_authenticated:
            club.creator = self.request.user.profile
        club.save()

        if self.request.user.is_authenticated:
            ClubMembership.objects.create(
                club=club,
                profile=self.request.user.profile,
                role="owner",
                status=ClubMembership.STATUS_MEMBER
            )
        return redirect(club.get_absolute_url())

    
    
class ClubDetailView(DetailView):
    model = Club
    template_name = "clubs/detail.html"
    context_object_name = "club"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        club = self.object
        user = self.request.user

        if user.is_authenticated:
            profile = user.profile
            membership = club.club_membership_set.filter(profile=profile).first()
            context["user_membership"] = membership
        else:
            context["user_membership"] = None

        # context.[""]
        # Get upcoming events that the club owns, sorted by date
        context['upcoming_events'] = (
            club.events_owned.filter(starts_at__gte=now()).order_by('starts_at')
        )
        return context
    

class ToggleFeaturedView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_staff

    def post(self, request, slug, *args, **kwargs):
        club = get_object_or_404(Club, slug=slug)
        club.is_featured = not club.is_featured
        club.save()
        return redirect(club.get_absolute_url())


class ToggleMembershipView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        club = get_object_or_404(Club, slug=slug)
        profile = request.user.profile

        membership, created = ClubMembership.objects.get_or_create(club=club, profile=profile)

        if not created:
            if membership.status == ClubMembership.STATUS_MEMBER:
                membership.delete()
                messages.success(request, "You have left the club.")
            elif membership.status == ClubMembership.STATUS_REQUESTED:
                membership.delete()
                messages.info(request, "Your membership request was cancelled.")
        else:
            # Fetch club owners and optimize query
            owners = club.club_membership_set.select_related("profile__user").filter(role="owner")

            # Use bulk_create for efficient notification creation
            user_ct = ContentType.objects.get_for_model(request.user)


            if club.require_request:
                membership.status = ClubMembership.STATUS_REQUESTED
                messages.info(request, "Membership request sent to club admins.")

                notifications = [
                    Notification(
                        recipient=owner.profile.user,
                        actor=request.user,
                        type = "CLUB_JOIN",
                        verb=f"has joined {club.name}",
                        target_ct=user_ct,
                        target_id=request.user.id,
                    )
                    for owner in owners
                ]
                Notification.objects.bulk_create(notifications)


            else:
                membership.status = ClubMembership.STATUS_MEMBER
                membership.responded_at = timezone.now()

                notifications = [
                    Notification(
                        recipient=owner.profile.user,
                        actor=request.user,
                        type = "CLUB_JOIN_REQUEST",
                        verb=f"has requested to join {club.name}",
                        target_ct=user_ct,
                        target_id=request.user.id,
                    )
                    for owner in owners
                ]
                Notification.objects.bulk_create(notifications)

                messages.success(request, "You are now a member!")

            membership.save()

        return redirect("clubs:club-detail", slug=slug)
    

class UserClubsView(LoginRequiredMixin, TemplateView):
    template_name = "clubs/user_clubs.html"
    context_object_name = "memberships"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = self.request.user.profile

        memberships = ClubMembership.objects.select_related("club").filter(
            profile=profile,
            status=ClubMembership.STATUS_MEMBER
        ).order_by(
            # owner first, then moderator, then member
            models.Case(
                models.When(role='owner', then=0),
                models.When(role='moderator', then=1),
                models.When(role='member', then=2),
                default=3,
                output_field=models.IntegerField()
            ),
            'club__name'
        )

        context["memberships"] = memberships
        return context
    

class ClubSettingsView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Club
    fields = ["who_can_post"]
    template_name = "clubs/club_settings.html"

    def get_queryset(self):
        return Club.objects.filter(club_membership_set__profile=self.request.user.profile, club_membership_set__role="owner")


class DeleteClubView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Club
    # template_name = "clubs/club_confirm_delete.html"
    success_url = reverse_lazy("clubs:user-clubs")

    def test_func(self):
        user = self.request.user

        # Allow if staff or owner
        if user.is_staff:
            return True

        club = self.get_object()
        return club.club_membership_set.filter(profile=self.request.user.profile, role="owner").exists()
    
    def form_valid(self, form):
        club_name = self.get_object().name
        messages.success(self.request, f"The club '{club_name}' was successfully deleted.")
        return super().form_valid(form)