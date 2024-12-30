from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.models import User
from django.views.generic import (
    ListView
)   
from posts.models import Post
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Course
from dal import autocomplete
from users.models import Profile
import re
from django.db.models import Q

from .forms import SearchForm


def home(request):
    context = { 
        'posts': Post.objects.all() 
    }
    return render(request, 'uoftsocial/home.html', context)

def about(request):
    return render(request, 'uoftsocial/about.html')

def account(request):
    return render(request, 'uoftsocial/account.html')

class PostListView(ListView):
    model = Post
    template_name = 'uoftsocial/home.html' # <app>/<model>_<viewtype>.html
    context_object_name = 'posts'
    ordering = ['-date_posted'] # Algorithim Implementation for Post Ordering HERE
    paginate_by = 5 # Pagination


class UserPostListView(ListView):
    model = Post
    template_name = 'uoftsocial/user_posts.html'  # Where we'll render the user profile
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


    
@login_required
def follow_user(request, username):
    """
    1) If target is private -> add the current user's profile to target's follow_requests.
    2) If target is public  -> immediately follow (add to each other's followers/following).
    """
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect('user-posts', username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    # Already following or requesting check:
    if current_profile.following.filter(id=target_profile.id).exists():
        messages.info(request, f"You already follow {target_user.username}.")
        return redirect('user-posts', username=username)

    if target_profile.follow_requests.filter(id=current_profile.id).exists():
        messages.info(request, f"You have already requested to follow {target_user.username}.")
        return redirect('user-posts', username=username)

    # Private vs. Public
    if target_profile.is_private:
        target_profile.follow_requests.add(current_profile)
        messages.success(request, f"Follow request sent to {target_user.username}.")
    else:
        target_profile.followers.add(current_profile)
        current_profile.following.add(target_profile)
        messages.success(request, f"You are now following {target_user.username}.")

    return redirect('user-posts', username=username)


@login_required
def unfollow_user(request, username):
    """
    Unfollows the target user (remove each from the other's followers/following).
    """
    target_user = get_object_or_404(User, username=username)
    if target_user == request.user:
        messages.warning(request, "You cannot unfollow yourself.")
        return redirect('user-posts', username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    # Check if we actually follow them:
    if current_profile.following.filter(id=target_profile.id).exists():
        # Remove from each other's relationships
        current_profile.following.remove(target_profile)
        target_profile.followers.remove(current_profile)
        messages.success(request, f"You have unfollowed {target_user.username}.")
    else:
        messages.info(request, f"You are not following {target_user.username}.")

    return redirect('user-posts', username=username)


@login_required
def accept_follow_request(request, request_profile_id):
    """
    Accept a follow request from profile with ID=request_profile_id.
    1) Remove from follow_requests
    2) Add each other to followers/following
    """
    # Current user = the private account who received requests
    current_profile = request.user.profile
    # The user who requested to follow me
    requesting_profile = get_object_or_404(Profile, id=request_profile_id)

    # Verify that requesting_profile is actually in current_profile's follow_requests
    if current_profile.follow_requests.filter(id=requesting_profile.id).exists():
        # Remove from requests
        current_profile.follow_requests.remove(requesting_profile)
        # Add each other to followers/following
        current_profile.followers.add(requesting_profile)
        requesting_profile.following.add(current_profile)

        messages.success(request, f"You have accepted {requesting_profile.user.username}'s follow request.")
    else:
        messages.warning(request, "No such follow request exists.")

    return redirect('view-follow-requests')  # Adjust to wherever you want to go after acceptance


@login_required
def decline_follow_request(request, request_profile_id):
    """
    Decline a follow request from profile with ID=request_profile_id.
    Just remove from follow_requests without adding them to followers/following.
    """
    current_profile = request.user.profile
    requesting_profile = get_object_or_404(Profile, id=request_profile_id)

    if current_profile.follow_requests.filter(id=requesting_profile.id).exists():
        current_profile.follow_requests.remove(requesting_profile)
        messages.info(request, f"You have declined {requesting_profile.user.username}'s follow request.")
    else:
        messages.warning(request, "No such follow request exists.")

    return redirect('view-follow-requests')  # Adjust to wherever you want to go after declining

@login_required
def view_follow_requests(request):
    """
    Show all profiles that have requested to follow the current user (if user is private).
    """
    current_profile = request.user.profile
    # These are the profiles that want to follow me
    requests_list = current_profile.follow_requests.all()

    return render(request, 'uoftsocial/follow_requests.html', {
        'requests_list': requests_list
    })

class CourseAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        # If user not logged in or has no permission, return empty
        if not self.request.user.is_authenticated:
            return Course.objects.none()
        
        qs = Course.objects.all()

        if self.q:  # typed text from user
            qs = qs.filter(name__icontains=self.q)
        return qs
    


# If you want fuzzy matching, install: pip install rapidfuzz
# from rapidfuzz import fuzz

def compute_post_score(post, query_tokens):
    """
    Compute a relevance score for a post relative to the query tokens.
    """
    score = 0
    title = post.title.lower()
    content = post.content.lower()
    
    for token in query_tokens:
        # For a simple approach, let's do direct substring checks
        # Increase score if token is in title
        if token in title:
            score += 5  # weight for title match
        # Increase score if token is in content
        if token in content:
            score += 2  # weight for content match

        # If you want fuzzy matching, you could do something like:
        # title_ratio = fuzz.partial_ratio(token, title)
        # content_ratio = fuzz.partial_ratio(token, content)
        # Then scale them. E.g.:
        # score += title_ratio * 0.05
        # score += content_ratio * 0.02

    return score


def get_global_dictionary_of_known_words():
    """
    Gathers all unique words from your Post titles/contents
    and User usernames/first/last names.
    In a real app, tailor this to your data or load an English dictionary file.
    """
    all_words = []
    for p in Post.objects.all():
        all_words.extend(re.findall(r"\w+", p.title.lower()))
        all_words.extend(re.findall(r"\w+", p.content.lower()))
    for u in User.objects.all():
        all_words.extend(re.findall(r"\w+", u.username.lower()))
        if u.first_name:
            all_words.extend(re.findall(r"\w+", u.first_name.lower()))
        if u.last_name:
            all_words.extend(re.findall(r"\w+", u.last_name.lower()))

    return list(set(all_words))  # Return unique words


from .spelling import correct_spelling

def search(request):
    form = SearchForm(request.GET or None)
    posts = []
    users = []
    corrected_query = ""

    if form.is_valid():
        # 1. Get form fields
        query = form.cleaned_data.get('query', '').strip()
        filter_by = form.cleaned_data.get('filter_by', '')
        order_by = form.cleaned_data.get('order_by', '')

        # 2. Spelling Correction
        query_tokens = query.lower().split()
        dictionary_words = get_global_dictionary_of_known_words()

        corrected_tokens = []
        for token in query_tokens:
            corrected_tokens.append(correct_spelling(token, dictionary_words, scorer_threshold=75))
        corrected_query = " ".join(corrected_tokens)

        # Decide whether to automatically use corrected_query or not:
        # Here, we'll do a "Did you mean...?" approach, so we actually search with corrected_query:
        # final_query = corrected_query if corrected_query else query
        final_query = query

        # For scoring, we still need the tokens:
        final_query_tokens = re.findall(r"\w+", final_query.lower())

        # 3. Search in Posts
        if filter_by in ['', 'posts']:
            all_posts = Post.objects.all()
            if final_query:
                # Basic substring filter to reduce the dataset
                all_posts = all_posts.filter(
                    Q(title__icontains=final_query) | Q(content__icontains=final_query)
                )

            # Convert to list to iterate
            all_posts_list = list(all_posts)

            # Compute scores
            scored_posts = []
            for post in all_posts_list:
                post_score = compute_post_score(post, final_query_tokens)
                scored_posts.append((post_score, post))

            # Sort primarily by score (descending)
            # Then optionally by user choice
            if order_by == 'title':
                # Sort by (score DESC, title ASC)
                scored_posts.sort(key=lambda x: (x[0], x[1].title), reverse=False)
                # That puts the smallest at top; we need to invert the score. 
                # Easiest to do two sorts or a custom key:
                scored_posts.sort(key=lambda x: x[0], reverse=True)
            elif order_by == 'date_posted':
                # Sort by (score DESC, date_posted DESC)
                scored_posts.sort(key=lambda x: (x[0], x[1].date_posted), reverse=True)
            else:
                # By score only (descending)
                scored_posts.sort(key=lambda x: x[0], reverse=True)

            # Extract the posts in final order
            posts = [item[1] for item in scored_posts]

        # 4. Search in Users
        if filter_by in ['', 'users']:
            all_users = User.objects.all()
            if final_query:
                all_users = all_users.filter(
                    Q(username__icontains=final_query)
                    | Q(first_name__icontains=final_query)
                    | Q(last_name__icontains=final_query)
                )

            # If you wanted user-specific scoring, you'd do something similar
            # to compute_post_score. For simplicity, we'll just do an order_by if needed:
            if order_by == 'username':
                users = all_users.order_by('username')
            else:
                users = all_users

    # Render results
    context = {
        'form': form,
        'posts': posts,
        'users': users,
        # So the template can show "Did you mean...?" if corrected_query != user’s original
        'corrected_query': corrected_query,
    }
    return render(request, 'uoftsocial/search_results.html', context)


from django.http import JsonResponse

def autocomplete(request):
    """compute_post_score
    Return JSON suggestions for the query string.
    E.g., searching in post titles + user usernames.
    """
    query = request.GET.get('term', '')  # "term" is the parameter jQuery UI uses by default
    suggestions = []

    if query:
        # Let's assume we want to suggest up to 5 post titles
        matching_posts = Post.objects.filter(title__icontains=query)[:5]
        for post in matching_posts:
            suggestions.append(post.title)

        # Also suggest up to 5 user usernames
        matching_users = User.objects.filter(username__icontains=query)[:5]
        for user in matching_users:
            suggestions.append(user.username)

    # Return distinct suggestions
    suggestions = list(set(suggestions))  # remove duplicates
    return JsonResponse(suggestions, safe=False)

