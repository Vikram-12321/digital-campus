from django.views.generic import (
    ListView
)   
from django.shortcuts import render, get_object_or_404, redirect

#Models
from django.contrib.auth.models import User
from apps.posts.models import Post
from django.db.models import Q

from django.views.generic import ListView
from django.http import JsonResponse, Http404
from django.template.loader import render_to_string

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
        # Redirect to profile page if the logged-in user is viewing their own posts
        username = self.kwargs.get('username')
        if request.user.is_authenticated and request.user.username == username:
            return redirect('profile')  # Replace 'profile' with your actual profile URL name
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        # Get the user whose profile is being viewed
        self.profile_user = get_object_or_404(User, username=self.kwargs.get('username'))
        # Return the posts belonging to that user
        return Post.objects.filter(author=self.profile_user).order_by('-date_posted')

    def get_context_data(self, **kwargs):
        # Add extra context for the template
        context = super().get_context_data(**kwargs)
        context['profile_user'] = self.profile_user
        return context
    
    