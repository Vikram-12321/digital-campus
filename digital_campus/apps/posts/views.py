# views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView
from django.shortcuts import redirect
from .models import Post, Attachment
from .forms import PostWithFilesForm           # ← use the form that has the “files” field
from django.urls import reverse


class AttachmentDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Attachment
    template_name = "posts/attachment_confirm_delete.html"  # optional, shown below

    def get_success_url(self):
        # bounce back to the post-edit form so the user stays in context
        return reverse("posts:post-update", kwargs={"pk": self.object.post.pk})

    def test_func(self):
        # only the post’s author can delete its attachments
        return self.request.user == self.get_object().post.author
    
class PostCreateView(LoginRequiredMixin, CreateView):
    model         = Post
    form_class    = PostWithFilesForm
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        # save the post first
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        # then save every uploaded file
        for f in self.request.FILES.getlist("files"):      # ← **same name as the form field**
            Attachment.objects.create(post=post, file=f)

        return redirect(post.get_absolute_url())


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model         = Post
    form_class    = PostWithFilesForm
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        response = super().form_valid(form)               # saves and sets self.object
        for f in self.request.FILES.getlist("files"):
            Attachment.objects.create(post=self.object, file=f)
        return response

    def test_func(self):
        return self.get_object().author == self.request.user


class PostDetailView(DetailView):
    model = Post


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model       = Post
    success_url = "/"

    def test_func(self):
        return self.get_object().author == self.request.user
