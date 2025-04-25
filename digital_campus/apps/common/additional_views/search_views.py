from rapidfuzz import process  # pip install rapidfuzz
from django.shortcuts import render
from django.http import JsonResponse

#Models
from django.contrib.auth.models import User
from apps.posts.models import Post
from django.db.models import Q

#Forms
from ..forms import SearchForm

#Additional 
import re

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
    return render(request, 'digital_campus/search_results.html', context)



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

