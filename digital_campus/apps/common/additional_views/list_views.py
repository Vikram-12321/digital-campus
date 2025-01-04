from django.views.generic import (
    ListView
)   
from django.shortcuts import render, get_object_or_404, redirect

#Models
from django.contrib.auth.models import User
from apps.posts.models import Post
from django.db.models import Q

class PostListView(ListView):
    model = Post
    template_name = 'digital_campus/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted'] # Algorithim Implementation for Post Ordering HERE
    paginate_by = 5 # Pagination


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
    
    