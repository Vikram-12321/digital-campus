"""
apps/common/additional_views/follow_views.py

Implements the follow system for users:
- Sending/canceling follow requests
- Accepting/declining follow requests
- Viewing pending requests
- Unfollowing users

Author: Vikram Bhojanala
Last updated: 2025-05-02
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from apps.users.models import Profile
from apps.common.models import Notification


@login_required
def follow_user(request, username):
    """
    Follow or request to follow a user.
    - If the target is private: send a follow request.
    - If the target is public: immediately follow.
    - If already requested: cancel the request.
    """
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect("common:user-posts", username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    if current_profile.following_requests.filter(id=target_profile.id).exists():
        # Cancel pending follow request
        current_profile.following_requests.remove(target_profile)
        target_profile.follow_requests.remove(current_profile)

        Notification.objects.filter(
            type = "FOLLOW_REQUEST",
            recipient=target_user,
            actor=request.user,
        ).delete()

        messages.info(request, f"Follow request to @{username} canceled.")
        return redirect("common:user-posts", username=username)

    if target_profile.is_private:
        # Send follow request
        target_profile.follow_requests.add(current_profile)
        current_profile.following_requests.add(target_profile)

        Notification.objects.create(
            recipient=target_user,
            actor=request.user,
            type = "FOLLOW_REQUEST",
            target_ct=ContentType.objects.get_for_model(request.user),
            target_id=request.user.id,
        )
        messages.success(request, f"Follow request sent to @{username}.")
    else:
        # Public account: follow immediately
        target_profile.followers.add(current_profile)
        current_profile.following.add(target_profile)

        Notification.objects.create(
            recipient=target_user,
            actor=request.user,
            type = "FOLLOW",
            target_ct=ContentType.objects.get_for_model(request.user),
            target_id=request.user.id,
        )
        messages.success(request, f"You are now following @{username}.")

    return redirect("common:user-posts", username=username)


@login_required
def unfollow_user(request, username):
    """
    Unfollow a user and remove all associated relationship/request links.
    """
    target_user = get_object_or_404(User, username=username)

    if target_user == request.user:
        messages.warning(request, "You cannot unfollow yourself.")
        return redirect("common:user-posts", username=username)

    current_profile = request.user.profile
    target_profile = target_user.profile

    if current_profile.following.filter(id=target_profile.id).exists():
        current_profile.following.remove(target_profile)
        target_profile.followers.remove(current_profile)

        # Clean up in case there were requests
        current_profile.following_requests.remove(target_profile)
        messages.success(request, f"You have unfollowed @{username}.")
    else:
        messages.info(request, f"You are not following @{username}.")

    return redirect("common:user-posts", username=username)


@login_required
def accept_follow_request(request, request_profile_id):
    """
    Accept a follow request from another profile.
    Establish mutual follow relationship and notify requester.
    """
    current_profile = request.user.profile
    requesting_profile = get_object_or_404(Profile, id=request_profile_id)

    if current_profile.follow_requests.filter(id=requesting_profile.id).exists():
        current_profile.follow_requests.remove(requesting_profile)
        requesting_profile.following_requests.remove(current_profile)

        current_profile.followers.add(requesting_profile)
        requesting_profile.following.add(current_profile)

        Notification.objects.create(
            recipient=requesting_profile.user,
            actor=request.user,
            type = "ACCEPT_FOLLOW_REQUEST",
            target_ct=ContentType.objects.get_for_model(request.user),
            target_id=request.user.id,
        )

        Notification.objects.filter(
            type = "ACCEPT_FOLLOW_REQUEST",
            recipient=request.user,
            actor=requesting_profile.user,
        ).delete()

        messages.success(request, f"You accepted @{requesting_profile.user.username}'s follow request.")
    else:
        messages.warning(request, "No such follow request found.")

    return redirect("common:view-follow-requests")


@login_required
def decline_follow_request(request, request_profile_id):
    """
    Decline a follow request from another profile.
    Removes from requests and deletes notification.
    """
    current_profile = request.user.profile
    requesting_profile = get_object_or_404(Profile, id=request_profile_id)

    if current_profile.follow_requests.filter(id=requesting_profile.id).exists():
        current_profile.follow_requests.remove(requesting_profile)
        requesting_profile.following_requests.remove(current_profile)

        Notification.objects.filter(
            type = "ACCEPT_FOLLOW_REQUEST",
            recipient=request.user,
            actor=requesting_profile.user,
        ).delete()

        messages.info(request, f"You declined @{requesting_profile.user.username}'s follow request.")
    else:
        messages.warning(request, "No such follow request found.")

    return redirect("common:view-follow-requests")


@login_required
def view_follow_requests(request):
    """
    Show all incoming follow requests to the current user (if their profile is private).
    """
    requests_list = request.user.profile.follow_requests.all()
    return render(request, "digital_campus/follow_requests.html", {"requests_list": requests_list})
