from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin # Login and Current User Conditions
from django.contrib.auth.models import User
from django.views.generic import (
    DetailView, 
    CreateView,
    UpdateView,
    DeleteView
)   
from .models import Post
from .forms import PostForm

class PostDetailView(DetailView):
    model = Post

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm        # Use our custom form instead of fields = [...]
    template_name = 'posts/post_form.html'
    # success_url = reverse_lazy('digital-campus-app-home')

    def form_valid(self, form):
        # Assign the current user as the author
        form.instance.author = self.request.user
        return super().form_valid(form)

class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['title', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)
    
    def test_func(self):
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    success_url = '/'

    def test_func(self): # Test if Current Post has the Author of the current logged in user
        post = self.get_object()
        if self.request.user == post.author:
            return True
        return False