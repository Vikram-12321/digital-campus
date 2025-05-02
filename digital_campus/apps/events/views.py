from django.shortcuts import render
from .models import Event, EventAttachment, AttendanceRecord
from .forms import EventWithFilesForm, EventForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView
from django.views.generic import ListView
from django.utils import timezone
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required


# class EventCreateView(LoginRequiredMixin, CreateView):
#     model         = Event
#     form_class    = EventWithFilesForm
#     template_name = "events/event_form.html"

#     def form_valid(self, form):
#         event = form.save(commit=False)
#         event.created_by = self.request.user
#         event.save()

#         for f in self.request.FILES.getlist("files"):
#             EventAttachment.objects.create(event=event, file=f)

#         return redirect(event.get_absolute_url())

@login_required
def create_or_edit_event(request, event_id=None):
    if event_id:
        event = get_object_or_404(Event, pk=event_id, host=request.user)
    else:
        event = Event(created_by=request.user)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, "Event saved.")
            return redirect("events:event-detail", pk=event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, "events/event_form.html", {"form": form})


# class EventUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
#     model         = Event
#     form_class    = EventWithFilesForm
#     template_name = "events/event_form.html"

#     def form_valid(self, form):
#         response = super().form_valid(form)
#         for f in self.request.FILES.getlist("files"):
#             EventAttachment.objects.create(event=self.object, file=f)
#         return response

#     def test_func(self):
#         return self.get_object().created_by == self.request.user


class EventDetailView(DetailView):
    model = Event
    template_name = "events/event_detail.html"


class EventDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model       = Event
    success_url = "/events/"        # back to feed

    def test_func(self):
        return self.get_object().created_by == self.request.user
    

class EventFeed(ListView):
    model               = Event
    template_name       = "events/event_feed.html"
    context_object_name = "events"
    paginate_by         = 10

    # ——— central definition of every pill ———
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
            "query": lambda qs, u: qs.filter(club__in=u.clubs.all())
            if u.is_authenticated
            else qs.none(),
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

    # -------- queryset -------------
    def get_queryset(self):
        base_qs = Event.objects.select_related("club")
        key     = self.request.GET.get("filter", "all")
        func    = self.FILTERS.get(key, self.FILTERS["all"])["query"]
        return func(base_qs, self.request.user).order_by("-starts_at")

    # -------- extra context --------
    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        chosen = self.request.GET.get("filter", "all")
        ctx["filter_selected"] = chosen
        ctx["filter_label"]    = self.FILTERS[chosen]["label"]
        ctx["filters"]         = [
            (k, spec["label"]) for k, spec in self.FILTERS.items()
        ]

        ctx["featured"] = (
            Event.objects.filter(is_featured=True, starts_at__gte=timezone.now())[:5]
        )
        return ctx

def get_context_data(self, **kwargs):
    ctx = super().get_context_data(**kwargs)
    ctx["filter"] = self.request.GET.get("filter", "all")
    ctx["featured"] = Event.objects.filter(
        is_featured=True, starts_at__gte=timezone.now()
    )[:5]

    # NEW: list of (query_key, label) pairs for the pill bar
    ctx["filters"] = [
        ("all", "All"),
        ("following", "Following"),
        ("events", "Events"),
        ("clubs", "Clubs"),
    ]
    return ctx


@staff_member_required
def toggle_feature(request, pk):
    ev = get_object_or_404(Event, pk=pk)
    ev.is_featured = not ev.is_featured
    ev.save(update_fields=["is_featured"])
    return redirect(ev.get_absolute_url())

@login_required
def attend_event(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    # if there are requirement tags, force request even if require_request==False
    needs_approval = event.require_request or event.requirements.exists()

    record, created = AttendanceRecord.objects.get_or_create(
        event=event, user=request.user,
        defaults={"status": AttendanceRecord.STATUS_REQUESTED}
    )

    if not created:
        messages.info(request, "You have already requested or joined.")
        return redirect("events:event-detail", pk=event_id)

    if not needs_approval:
        record.status = AttendanceRecord.STATUS_ATTENDING
        record.responded_at = timezone.now()
        record.save()
        messages.success(request, "You're now attending!")
    else:
        messages.success(request, "Request sent to host for approval.")
    return redirect("events:event-detail", pk=event_id)
