from django.views.generic import (
    ListView
)   
from django.shortcuts import render, get_object_or_404, redirect

#Models
from django.contrib.auth.models import User
from apps.posts.models import Post

from django.views.generic import ListView
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string
from apps.events.models import Event
from django.utils import timezone


class PostListView(ListView):
    model = Post
    template_name = 'digital_campus/home.html'         # your home page
    context_object_name = 'posts'
    paginate_by = 5                            # still page under the hood
    ordering = ['-date_posted']

    def get_queryset(self):
        # grab all posts, newest first, and prefetch attachments in one go
        return Post.objects.all()\
                .order_by('-date_posted')\
                .prefetch_related('attachments')

    def get_context_data(self, **kwargs):
        # 1) get the default context (includes `posts`, pagination, etc.)
        context = super().get_context_data(**kwargs)

        # 2) load upcoming events
        events = (
            Event.objects
                 .filter(starts_at__gte=timezone.now())
                 .order_by('starts_at')[:20]
        )

        # 3) merge posts + events into items
        items = []
        for p in context['posts']:
            p.kind = 'post'
            p.timestamp = p.date_posted
            items.append(p)
        for e in events:
            e.kind = 'event'
            e.timestamp = e.starts_at
            items.append(e)

        # 4) sort by that timestamp desc
        items.sort(key=lambda x: x.timestamp, reverse=True)

        # 5) put it in the context
        context['items'] = items

        return context
    
    def get(self, request, *args, **kwargs):
        # standard setup
        self.object_list = self.get_queryset()
        try:
            context = self.get_context_data()
        except Http404:
            # page number out of range
            if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
                # return empty so JS knows to stop
                return JsonResponse({'posts_html': ''})
            # for non-AJAX, re-raise so you get the normal 404 page
            raise

        # AJAX scroll request? return only the partial
        if request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
            posts_html = render_to_string(
                'digital_campus/post_list.html',
                {'posts': context['posts']},
                request=request
            )
            return JsonResponse({'posts_html': posts_html})

        # normal full-page load
        return self.render_to_response(context)

class UserPostListView(ListView):
    model = Post
    template_name = 'digital_campus/user_posts.html'  # Where we'll render the user profile
    context_object_name = 'posts'
    paginate_by = 5  # 5 posts per page

    def dispatch(self, request, *args, **kwargs):
        username = self.kwargs.get('username')
        if request.user.is_authenticated and request.user.username == username:
            return redirect('profile')    # your own profile URL name
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # fetch the user whose page we’re viewing
        self.profile_user = get_object_or_404(User, username=self.kwargs['username'])
        return (
            Post.objects
                .filter(author=self.profile_user)
                .order_by('-date_posted')
                .prefetch_related('attachments')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 1) the user whose profile this is
        context['profile_user'] = self.profile_user

        # 2) upcoming events hosted by this user
        context['upcoming_events'] = (
            Event.objects
                 .filter(created_by=self.profile_user, starts_at__gte=timezone.now())
                 .order_by('starts_at')[:5]
        )

        # 3) “academics” — you can hook this up to real data later
        # for now, dummy two courses
        context['current_courses'] = [
            {'code': 'MAT244', 'name': 'Linear & Nonlinear Systems'},
            {'code': 'CSC263', 'name': 'Data Structures'},
        ]

        # 4) clubs — stub with two sample clubs (replace with real query)
        context['clubs'] = [
            type('C', (), {'pk':1,'name':'UofT Math Society'})(),
            type('C', (), {'pk':2,'name':'AI & ML Club'})(),
        ]

        # 5) recent activity — dummy strings
        context['activities'] = [
            "Commented on 'Quantum Mechanics Study Group'",
            "Joined event 'Chess Club Hangout'",
            "Liked a post in AI & ML Club",
        ]

        # 6) badges — dummy list
        context['badges'] = [
            "Top Contributor",
            "Event Host (5 events)",
            "Rising Star",
        ]

        return context
    
    