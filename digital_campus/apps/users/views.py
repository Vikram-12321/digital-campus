from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Profile
from apps.posts.models import Post                     # ← add this import
from django.core.paginator import Paginator


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save the user and get the instance
            Profile.objects.get_or_create(user=user)  # Create a profile for the new user
            messages.success(request, 'Your account has been created! You can now login!')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    # ---------- 1. handle the forms exactly as before ----------
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST,
                                   request.FILES,
                                   instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profile")
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    # ---------- 2. gather this user’s posts + paginate ----------
    posts_qs   = Post.objects.filter(author=request.user).order_by("-date_posted")
    paginator  = Paginator(posts_qs, 5)            # 5 posts per page
    page_num   = request.GET.get("page")           # ?page=2 etc.
    page_obj   = paginator.get_page(page_num)

    # ---------- 3. build the template context ----------
    context = {
        "u_form":        u_form,
        "p_form":        p_form,
        "profile_user":  request.user,     # so the template can reuse user_posts.html bits
        "posts":         page_obj.object_list,
        "page_obj":      page_obj,
        "is_paginated":  page_obj.has_other_pages(),
    }
    return render(request, "users/profile.html", context)


@login_required
def profile_settings(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile_settings.html', {'u_form': u_form, 'p_form': p_form})