"""
events/views.py

Handles all event-related views including creation, editing, deletion, detail,
and listing (feed). Also includes event ownership management, attendance logic,
and staff feature toggling.

Author: Your Name or Team
Last updated: 2025-05-02
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import DetailView, DeleteView, CreateView, ListView, TemplateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.conf import settings
from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from apps.notifications.models import Notification

from .models import Event, EventAttachment, AttendanceRecord, EventOwnership
from .forms import EventWithFilesForm, EventForm
from apps.clubs.models import Club

# ————————————————————————————
# Event Creation / Update View
# ————————————————————————————
class EventCreateUpdateView(LoginRequiredMixin, CreateView):
    """
    Handles both creation and editing of events by users.
    If editing, restricts access to only those events the user owns.
    """
    model = Event
    form_class = EventWithFilesForm
    template_name = "events/event_form.html"
    pk_url_kwarg = "event_id"

    def dispatch(self, request, *args, **kwargs):
        # If editing an existing event, retrieve it and check ownership
        self.object = self.get_object_if_exists()
        if self.object:
            return super(UpdateView, self).dispatch(request, *args, **kwargs)
        return super().dispatch(request, *args, **kwargs)

    def get_object_if_exists(self):
        event_id = self.kwargs.get("event_id")
        if event_id:
            return get_object_or_404(Event, pk=event_id, ownership__user=self.request.user)
        return None

    def get_form_kwargs(self):
        # Inject the object if editing
        kwargs = super().get_form_kwargs()
        if self.object:
            kwargs["instance"] = self.object
        return kwargs

    def form_valid(self, form):
        is_new = self.object is None
        event = form.save(commit=False)

        if is_new:
            event.created_by = self.request.user

            # Extract club from query param
            club_id = self.request.GET.get("club")
            if club_id:
                try:
                    club = Club.objects.get(pk=club_id)
                    event.club = club
                except Club.DoesNotExist:
                    messages.error(self.request, "Invalid club specified.")
                    return redirect("clubs:user-clubs")  # fallback redirect

        event.save()
        form.save_m2m()

        if is_new:
            if event.club:
                EventOwnership.objects.create(event=event, club=event.club)
            else:
                EventOwnership.objects.create(event=event, user=self.request.user)

        messages.success(self.request, "Event saved.")
        return redirect("events:event-detail", pk=event.pk)



# ————————————————————————————
# Event Detail View
# ————————————————————————————
class EventDetailView(DetailView):
    """
    Displays the details of a single event.
    """
    model = Event
    template_name = "events/event_detail.html"
    context_object_name = "event"  # <--- this is important

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        event = self.get_object()
        user = self.request.user
        if user.is_authenticated:
            record = event.attendancerecord_set.filter(user=user).first()
            context['attendance_status'] = record.status if record else None
            context['attendance_record_id'] = record.id if record else None
        return context


# ————————————————————————————
# Event Deletion View
# ————————————————————————————
class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    """
    Allows users to delete events they created.
    """
    model = Event
    success_url = "/events/"

    def test_func(self):
        return self.get_object().created_by == self.request.user


# ————————————————————————————
# Event Feed / Listing
# ————————————————————————————
class EventFeed(ListView):
    """
    Displays a list of events with filters (all, upcoming, following, etc.).
    """
    model = Event
    template_name = "events/event_feed.html"
    context_object_name = "events"
    paginate_by = 10

    FILTERS = {
        "all": {
            "label": "All",
            "query": lambda qs, u: qs,
        },
        "upcoming": {
            "label": "Upcoming",
            "query": lambda qs, u: qs.filter(starts_at__gte=timezone.now()),
        },
        "following": {
            "label": "Following",
            "query": lambda qs, u: qs.filter(club__in=u.clubs.all()) if u.is_authenticated else qs.none(),
        },
        "clubs": {
            "label": "Clubs",
            "query": lambda qs, u: qs.filter(club__isnull=False),
        },
        "events": {
            "label": "Events",
            "query": lambda qs, u: qs.filter(club__isnull=True),
        },
    }

    def get_queryset(self):
        base_qs = Event.objects.select_related("ownership__club")
        key = self.request.GET.get("filter", "all")
        func = self.FILTERS.get(key, self.FILTERS["all"])["query"]
        return func(base_qs, self.request.user).order_by("-starts_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        key = self.request.GET.get("filter", "all")
        ctx["filter_selected"] = key
        ctx["filter_label"] = self.FILTERS[key]["label"]
        ctx["filters"] = [(k, v["label"]) for k, v in self.FILTERS.items()]
        ctx["featured"] = Event.objects.filter(is_featured=True, starts_at__gte=timezone.now())[:5]
        return ctx


# ————————————————————————————
# Feature Toggle (Admin Only)
# ————————————————————————————
@staff_member_required
def toggle_feature(request, pk):
    """
    Admin-only toggle for marking an event as featured.
    """
    ev = get_object_or_404(Event, pk=pk)
    ev.is_featured = not ev.is_featured
    ev.save(update_fields=["is_featured"])
    return redirect(ev.get_absolute_url())


# ————————————————————————————
# Attend Event View
# ————————————————————————————
@login_required
def attend_event(request, event_id):
    """
    Allows users to attend or request attendance for an event.
    If the event requires approval or has requirements, marks the request as 'requested'.
    Otherwise, confirms attendance immediately.
    """
        
    event = get_object_or_404(Event, pk=event_id)
    record = AttendanceRecord.objects.filter(event=event, user=request.user).first()
    status = "None"
    responded_at = None
    notification_type_set = "None"

    if record:
        record.delete()
        messages.info(request, "You've stopped attending this event.")

    else: 
        if event.require_request:
            notification_type_set = "EVENT_REQUEST"
            status = AttendanceRecord.STATUS_REQUESTED
            responded_at=timezone.now()
            messages.success(request, "Request sent to host for approval.")

        else:
            notification_type_set = "EVENT_ATTEND"
            status = AttendanceRecord.STATUS_ATTENDING
            messages.success(request, "You're now attending!")


        Notification.create_notification(
            recipient=event.created_by,
            actor=request.user,
            notification_type = notification_type_set,
            target=request.user,
        )

        AttendanceRecord.objects.create(
            event=event,
            user=request.user,
            status=status,
            responded_at=responded_at 
        )

    return redirect("events:event-detail", pk=event_id)

class UserEventsView(LoginRequiredMixin, TemplateView):
    template_name = "events/user_events.html"
    context_object_name = "event_memberships"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        memberships = EventOwnership.objects.select_related("event").filter(
            user=self.request.user,
        ).order_by(
            "event__starts_at"
        )

        context["memberships"] = memberships
        return context
    