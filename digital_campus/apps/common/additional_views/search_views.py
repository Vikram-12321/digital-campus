from rapidfuzz import process  # pip install rapidfuzz
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse

# Models
from django.contrib.auth.models import User
from apps.posts.models import Post
from apps.clubs.models import Club
from apps.events.models import Event

# Forms
from ..forms import SearchForm

# Additional 
import re

# Debugging
import logging
logger = logging.getLogger(__name__)


def correct_spelling(input_word, dictionary_words, scorer_threshold=75):
    """
    Use rapidfuzz to find the closest match in dictionary_words to input_word.
    Only return a suggestion if it meets the scorer_threshold.
    """
    # process.extractOne returns a tuple: (best_match, score, index)
    best_match = process.extractOne(input_word, dictionary_words)
    if best_match and best_match[1] >= scorer_threshold:
        return best_match[0]  # The best matching word
    return input_word  # Return original if no decent match found


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


def search(request):
    form = SearchForm(request.GET or None)

    # Single-select filter_by, default to 'all'
    filter_by = request.GET.get('filter_by', 'all')

    # Containers
    posts = []; users = []; clubs = []; events = []
    corrected_query = ""
    order_by = ''
    query    = ''

    # DEBUG: log what came in
    logger.debug("Incoming GET params: %r", request.GET)

    if not form.is_valid():
        logger.debug("Form errors: %r", form.errors)

    if form.is_valid():
        query    = form.cleaned_data.get('query','').strip()
        order_by = form.cleaned_data.get('order_by','')

        # Spelling correction (optional “Did you mean?”)
        tokens = re.findall(r"\w+", query.lower())
        dict_words = get_global_dictionary_of_known_words()
        corrected_tokens = [correct_spelling(t, dict_words) for t in tokens]
        corrected_query = " ".join(corrected_tokens)

        final_query = query
        qtoks = re.findall(r"\w+", final_query.lower())

        # POSTS
        if filter_by in ('all','posts'):
            qs = Post.objects.all()
            if final_query:
                qs = qs.filter(
                  Q(title__icontains=final_query) |
                  Q(content__icontains=final_query)
                )
            scored = [(compute_post_score(p, qtoks), p) for p in qs]
            scored.sort(key=lambda x: x[0], reverse=True)
            posts = [p for _, p in scored]

        # USERS
        if filter_by in ('all','users'):
            u_qs = User.objects.all()
            if final_query:
                u_qs = u_qs.filter(
                  Q(username__icontains=final_query) |
                  Q(first_name__icontains=final_query) |
                  Q(last_name__icontains=final_query)
                )
            users = list(u_qs.order_by('username') if order_by=='username' else u_qs)

        # CLUBS
        if filter_by in ('all','clubs'):
            clubs = list(
              (Club.objects.filter(name__icontains=final_query)
               if final_query else Club.objects.all())
            )

        # EVENTS
        if filter_by in ('all','events'):
            events = list(
              (Event.objects.filter(title__icontains=final_query)
               if final_query else Event.objects.all())
            )

    return render(request, 'digital_campus/search_results.html', {
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


def autocomplete(request):
    term = request.GET.get('term', '')
    out  = []

    if term:
        # — Posts (if you want) —
        for post in Post.objects.filter(title__icontains=term)[:5]:
            out.append({
                'label': post.title,
                'value': post.title,
                'type':  'post',
                'url':   reverse('posts:post-detail', args=[post.pk]),
            })

        # — Users —
        for user in User.objects.filter(username__icontains=term)[:5]:
            if request.user.is_authenticated and user.pk == request.user.pk:
                # current user → /profile/
                url = reverse('profile')
            else:
                # other users → /user/{username}/
                url = reverse('common:user-posts', args=[user.username])

            out.append({
                'label': user.username,
                'value': user.username,
                'type':  'user',
                'url':   url,
            })

        # — Clubs —
        for club in Club.objects.filter(name__icontains=term)[:5]:
            out.append({
                'label': club.name,
                'value': club.name,
                'type':  'club',
                'url':   reverse('clubs:club-detail', args=[club.slug]),
            })

        # — Events —
        for ev in Event.objects.filter(title__icontains=term)[:5]:
            out.append({
                'label': ev.title,
                'value': ev.title,
                'type':  'event',
                'url':   reverse('events:event-detail', args=[ev.pk]),
            })

    return JsonResponse(out, safe=False)
