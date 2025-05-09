# views.py
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import DetailView, DeleteView, UpdateView, CreateView
from django.shortcuts import get_object_or_404, redirect
from .models import Post, Attachment, PostLike, PostOwnership
from .forms import PostWithFilesForm           
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from .forms import CommentForm
from apps.clubs.models import Club


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
    model = Post
    form_class = PostWithFilesForm
    template_name = "posts/post_form.html"

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        post.save()

        # Save attachments
        for f in self.request.FILES.getlist("files"):
            Attachment.objects.create(post=post, file=f)

        # Handle ownership: ?club=...
        club_id = self.request.GET.get("club")
        if club_id:
            try:
                club = Club.objects.get(pk=club_id)
                # ✅ SAFETY CHECK: is the user a member of this club?
                if club.club_membership_set.filter(profile=self.request.user.profile, status="member").exists():
                    PostOwnership.objects.create(post=post, club=club)
                else:
                    return HttpResponseForbidden("You're not a member of this club.")
                
            except Club.DoesNotExist:
                PostOwnership.objects.create(post=post, user=self.request.user)
        else:
            PostOwnership.objects.create(post=post, user=self.request.user)

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
    template_name = 'posts/post_detail.html'  # or whatever your template is

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        return context


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model       = Post
    success_url = "/profile/"

    def test_func(self):
        return self.get_object().author == self.request.user


## Post Like View
@login_required
def like_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    like, created = PostLike.objects.get_or_create(post=post, user=request.user.profile)
    if not created:
        like.delete()
        liked = False
    else:
        liked = True
    return JsonResponse({'liked': liked, 'like_count': post.likes.count()})


## Post Comment View
@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user.profile
            comment.post = post
            comment.save()
    return redirect('posts:post-detail', pk=post.id)