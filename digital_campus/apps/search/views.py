"""
apps/search/views.py

Implements full-text search and autocomplete using fuzzy matching
and simple scoring heuristics.

Features:
- Basic query normalization and spell correction
- Result ranking by relevance
- Multi-model search across Posts, Users, Clubs, and Events
- AJAX autocomplete endpoint for real-time suggestions

Author: Vikram Bhojanala
"""

import re
import logging
from rapidfuzz import process
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse
from django.templatetags.static import static
from django.utils.timezone import localtime

# Models
from django.contrib.auth.models import User
from apps.posts.models import Post
from apps.clubs.models import Club
from apps.events.models import Event

# Forms
from .forms import SearchForm

logger = logging.getLogger(__name__)


# ---------------------
# Utility Functions
# ---------------------

def correct_spelling(input_word, dictionary_words, scorer_threshold=75):
    """
    Use RapidFuzz to correct a single word if there's a close enough match.
    """
    best_match = process.extractOne(input_word, dictionary_words)
    if best_match and best_match[1] >= scorer_threshold:
        return best_match[0]
    return input_word


def compute_post_score(post, query_tokens):
    """
    Score a post based on how many tokens match title/content.
    Weights:
    - title match: +5
    - content match: +2
    """
    score = 0
    title = post.title.lower()
    content = post.content.lower()

    for token in query_tokens:
        if token in title:
            score += 5
        if token in content:
            score += 2
    return score


def get_global_dictionary_of_known_words():
    """
    Return a set of known words from user and post content for spell correction.
    """
    words = set()

    for p in Post.objects.all():
        words.update(re.findall(r"\w+", p.title.lower()))
        words.update(re.findall(r"\w+", p.content.lower()))

    for u in User.objects.all():
        words.update(re.findall(r"\w+", u.username.lower()))
        if u.first_name:
            words.update(re.findall(r"\w+", u.first_name.lower()))
        if u.last_name:
            words.update(re.findall(r"\w+", u.last_name.lower()))

    return list(words)


# ---------------------
# Search View
# ---------------------

def search(request):
    """
    Full search handler with optional spell correction and basic result ranking.
    Supports filter_by (posts, users, clubs, events) and order_by (title, username).
    """
    form = SearchForm(request.GET or None)
    filter_by = request.GET.get('filter_by', 'all')

    posts, users, clubs, events = [], [], [], []
    corrected_query = ""
    order_by = ''
    query = ''

    logger.debug("Incoming search request: %r", request.GET)

    if not form.is_valid():
        logger.debug("Form errors: %r", form.errors)

    if form.is_valid():
        query = form.cleaned_data.get('query', '').strip()
        order_by = form.cleaned_data.get('order_by', '')

        # Tokenize and correct spelling
        tokens = re.findall(r"\w+", query.lower())
        dict_words = get_global_dictionary_of_known_words()
        corrected_tokens = [correct_spelling(t, dict_words) for t in tokens]
        corrected_query = " ".join(corrected_tokens)

        qtoks = corrected_tokens or tokens
        final_query = query

        # ----- POSTS -----
        if filter_by in ('all', 'posts'):
            qs = Post.objects.all()
            if final_query:
                qs = qs.filter(Q(title__icontains=final_query) | Q(content__icontains=final_query))
            scored = [(compute_post_score(p, qtoks), p) for p in qs]
            posts = [p for score, p in sorted(scored, key=lambda x: x[0], reverse=True)]

        # ----- USERS -----
        if filter_by in ('all', 'users'):
            u_qs = User.objects.all()
            if final_query:
                u_qs = u_qs.filter(
                    Q(username__icontains=final_query) |
                    Q(first_name__icontains=final_query) |
                    Q(last_name__icontains=final_query) |
                    Q(profile__bio__icontains=final_query)
                )
            users = list(u_qs.order_by('username') if order_by == 'username' else u_qs)

        # ----- CLUBS -----
        if filter_by in ('all', 'clubs'):
            c_qs = Club.objects.all()
            if final_query:
                c_qs = c_qs.filter(
                    Q(name__icontains=final_query) |
                    Q(description__icontains=final_query) | ## Questionable to add or not
                    Q(slug__icontains=final_query) 
                )
            clubs = list(c_qs.order_by('title') if order_by == 'title' else c_qs)

        # ----- EVENTS -----
        if filter_by in ('all', 'events'):
            e_qs = Event.objects.all()
            if final_query:
                e_qs = e_qs.filter(
                    Q(title__icontains=final_query) |
                    Q(description__icontains=final_query) |
                    Q(location__icontains=final_query) |
                    Q(created_by__username__icontains=final_query) |
                    Q(club__name__icontains=final_query) |
                    Q(requirements__name__icontains=final_query) 
                )
            events = list(e_qs.order_by('title') if order_by == 'title' else e_qs)
        
    return render(request, 'search/search_results.html', {
        'form':            form,
        'query':           query,
        'filter_by':       filter_by,
        'order_by':        order_by,
        'corrected_query': corrected_query,
        'posts':           posts,
        'users':           users,
        'clubs':           clubs,
        'events':          events,
    })


# ---------------------
# Autocomplete View
# ---------------------

def autocomplete(request):
    """
    Lightweight endpoint for real-time search suggestions.
    Returns JSON with `label`, `value`, `type`, and `url`.
    """
    term = request.GET.get('term', '')
    results = []

    if term:
        # Posts
        for post in Post.objects.filter(title__icontains=term)[:5]:
            if (post.author.profile and post.author.profile.image):
                image= post.author.profile.image.url
            elif (post.author.club and post.author.club.avatar):
                image= post.author.club.avatar.url
            else:
                static('images/default.png')

            snippet = (post.content[:50] + '…') if len(post.content) > 50 else post.content
            subtitle = post.author.username

            results.append({
                'label': post.title,
                'value': post.title,
                'type':  'Post',
                'url':   reverse('posts:post-detail', args=[post.pk]),
                'image': image,
                'subtitle': f"Posted By: {subtitle}",
                'snippet':  snippet,

            })

        for post in Post.objects.filter(content__icontains=term)[:5]:
            if (post.author.profile and post.author.profile.image):
                image= post.author.profile.image.url
            elif (post.author.club and post.author.club.avatar):
                image= post.author.club.avatar.url
            else:
                static('images/default.png')

            snippet = (post.content[:50] + '…') if len(post.content) > 50 else post.content
            subtitle = post.author.username
            # subtitle = f"{event.location or '—'} · {localtime(event.starts_at).strftime('%b %d, %I:%M %p')}"
            results.append({
                'label': post.title,
                'value': post.title,
                'type':  'Post',
                'url':   reverse('posts:post-detail', args=[post.pk]),
                'image': image,
                'subtitle': f"Posted By: {subtitle}",
                'snippet':  snippet,
            })
        

        # Users
        for user in User.objects.filter(username__icontains=term)[:5]:
            url = reverse('profile') if request.user.is_authenticated and user.pk == request.user.pk \
                  else reverse('common:user-posts', args=[user.username])
            profile = getattr(user, "profile", None)
            results.append({
                'label': user.username,
                'value': user.username,
                'type':  'User',
                'url':   url,
                'image': profile.image.url if (profile and profile.image) else static('images/default.png')
            })

        # Clubs
        for club in Club.objects.filter(name__icontains=term)[:5]:
            snippet = (club.description[:50] + '…') if len(club.description) > 50 else club.description
            try:
                image_url = club.avatar.url
            except ValueError:
                image_url = static('images/default.png')

            results.append({
                'label': club.name,
                'value': club.name,
                'type':  'Club',
                'url':   reverse('clubs:club-detail', args=[club.slug]),
                'image': image_url,
                'snippet':  snippet,

            })

        # Events
        for event in Event.objects.filter(title__icontains=term)[:5]:
            snippet = (event.description[:50] + '…') if len(event.description) > 50 else event.description
            if event.club: 
                subtitle = f"{event.location or '—'} · {localtime(event.starts_at).strftime('%b %d, %I:%M %p')}  · {event.club}"
            else: 
                subtitle = f"{event.location or '—'} · {localtime(event.starts_at).strftime('%b %d, %I:%M %p')}  · {event.created_by}"
            results.append({
                'label': event.title,
                'value': event.title,
                'type':  'Event',
                'url':   reverse('events:event-detail', args=[event.pk]),
                'image': event.club.avatar.url if event.club else (event.created_by.profile.image.url if event.created_by.profile and event.created_by.profile.image else static('images/default.png')),
                'subtitle': subtitle,
                'snippet':  snippet,

            })

    return JsonResponse(results, safe=False)
