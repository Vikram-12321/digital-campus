"""
apps/common/additional_views/list_views.py

Feed and profile views:
- PostListView: Main feed combining posts and upcoming events.
- UserPostListView: Profile page showing user posts, events, and metadata.

Author: Vikram Bhojanala
Last updated: 2025-05-02
"""

from django.views.generic import ListView
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.utils import timezone

from django.contrib.auth.models import User
from apps.posts.models import Post
from apps.events.models import Event
from itertools import chain



from django.utils import timezone
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from django.views.generic import ListView
from itertools import chain

from apps.events.models import Event
from apps.posts.models import Post


from itertools import chain

class PostListView(ListView):
    """Home feed = mixed posts + events with filter pills and infinite scroll."""
    model               = Post
    template_name       = "digital_campus/home.html"
    context_object_name = "posts"
    paginate_by         = 5

    # ---------- helpers ----------
    def _tag(self, qs, kind, ts_attr):
        """stamp .kind  and .timestamp onto every row"""
        for o in qs:
            o.kind = kind
            o.timestamp = getattr(o, ts_attr)
        return qs

    def get_filter_by(self):
        return self.request.GET.get("filter_by", "all")

    # ---------- queryset ----------
    def get_queryset(self):
        f = self.get_filter_by()

        posts  = Post.objects.select_related("author")\
                             .prefetch_related("attachments")\
                             .order_by("-date_posted")
        events = Event.objects.select_related("created_by")\
                              .filter(starts_at__gte=timezone.now())\
                              .order_by("starts_at")

        if f == "posts":
            return self._tag(list(posts),  "post",  "date_posted")
        if f == "events":
            return self._tag(list(events), "event", "starts_at")
        
        if f == "new":
            # newest across posts *and* events
            mixed = chain(
                self._tag(list(posts),  "post",  "date_posted"),
                self._tag(list(events), "event", "starts_at"),
            )
            return sorted(mixed, key=lambda x: x.timestamp, reverse=True) 

        # mixed - Not Optimized 
        mixed = chain(
            self._tag(list(posts),  "post",  "date_posted"),
            self._tag(list(events), "event", "starts_at"),
        )


        return sorted(mixed, key=lambda x: x.timestamp, reverse=True)

    # ---------- context ----------
    def get_context_data(self, **kw):
        ctx = super().get_context_data(**kw)   # handles pagination here
        ctx["items"]      = ctx["object_list"]
        ctx["filter_by"]  = self.get_filter_by()
        ctx["hide_params"] = True              # for _filter_pills.html
        return ctx

    # ---------- GET (handles Ajax) ----------
    def get(self, request, *args, **kw):
        try:
            self.object_list = self.get_queryset()
            context = self.get_context_data()
        except Http404:
            # paginator ran out – return empty slice for AJAX
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"posts_html": ""})
            raise

        # Ajax branch
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            html = render_to_string(
                "digital_campus/home_list.html",   # needs filter_by in ctx
                context,
                request=request,
            )
            return JsonResponse({"posts_html": html})

        # full page
        return self.render_to_response(context)


class UserPostListView(ListView):
    """
    View for a user’s profile page:
    - Lists their posts
    - Includes recent events and profile metadata
    """
    model = Post
    template_name = 'digital_campus/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def dispatch(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        if request.user.is_authenticated and request.user.username == username:
            return redirect('profile')  # update this with your profile route name
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return (
            Post.objects
                .filter(author=self.profile_user)
                .order_by('-date_posted')
                .prefetch_related('attachments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user

        # Actual upcoming events by this user
        context['upcoming_events'] = (
            Event.objects
                .filter(created_by=self.profile_user, starts_at__gte=timezone.now())
                .order_by('starts_at')[:5]
        )

        # Stubbed data for demonstration — replace with real queries later
        context['current_courses'] = [
            {'code': 'MAT244', 'name': 'Linear & Nonlinear Systems'},
            {'code': 'CSC263', 'name': 'Data Structures'},
        ]
        context['clubs'] = [
            type('C', (), {'pk': 1, 'name': 'UofT Math Society'})(),
            type('C', (), {'pk': 2, 'name': 'AI & ML Club'})(),
        ]
        context['activities'] = [
            "Commented on 'Quantum Mechanics Study Group'",
            "Joined event 'Chess Club Hangout'",
            "Liked a post in AI & ML Club",
        ]
        context['badges'] = [
            "Top Contributor",
            "Event Host (5 events)",
            "Rising Star",
        ]

        return context
