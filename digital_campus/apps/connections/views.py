"""
apps/connections/views.py

Follow system:
- Send / cancel follow requests
- Accept / decline requests
- Unfollow users
- View pending requests

Author: Vikram Bhojanala
Last updated: 2025-05-09
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect, render

from apps.users.models import Profile
from apps.notifications.models import Notification, NotificationType


# ───────────────────────────────────────────────────────────
# Helper: upsert a notification (1 DB hit, idempotent)
# ───────────────────────────────────────────────────────────
def _notify(recipient: User, actor: User, notif_type: str) -> None:
    Notification.create_notification(
        recipient=recipient,
        actor=actor,
        notification_type=notif_type,
        target = actor
    )

# ───────────────────────────────────────────────────────────
# Follow / Request
# ───────────────────────────────────────────────────────────
@login_required
def follow_user(request, username: str):
    actor       = request.user
    target_user = get_object_or_404(
        User.objects.select_related("profile"), username=username
    )

    if actor == target_user:
        messages.warning(request, "You cannot follow yourself.")
        return redirect("common:user-posts", username=username)

    me   = actor.profile
    them = target_user.profile

    with transaction.atomic():
        # ── 1. Cancel existing pending request ────────────────────
        if me.following_requests.filter(pk=them.pk).exists():
            me.following_requests.remove(them)     # reverse link auto-removed
            _notify(recipient=target_user, actor=actor,
                    notif_type=NotificationType.FOLLOW_REQUEST)
            # delete old FOLLOW_REQUEST notice
            Notification.objects.filter(
                notification_type=NotificationType.FOLLOW_REQUEST,
                recipient=target_user,
                actor=actor,
            ).delete()
            messages.info(request, f"Follow request to @{username} cancelled.")
            return redirect("common:user-posts", username=username)

        # ── 2. Private account → send request ─────────────────────
        if them.is_private:
            me.following_requests.add(them)
            _notify(recipient=target_user, actor=actor,
                    notif_type=NotificationType.FOLLOW_REQUEST)
            messages.success(request, f"Follow request sent to @{username}.")
        # ── 3. Public account → follow immediately ────────────────
        else:
            me.following.add(them)                 # single write; reverse = followers
            _notify(recipient=target_user, actor=actor,
                    notif_type=NotificationType.FOLLOW)
            messages.success(request, f"You are now following @{username}.")

    return redirect("common:user-posts", username=username)


# ───────────────────────────────────────────────────────────
# Unfollow
# ───────────────────────────────────────────────────────────
@login_required
def unfollow_user(request, username: str):
    actor       = request.user
    target_user = get_object_or_404(
        User.objects.select_related("profile"), username=username
    )

    if actor == target_user:
        messages.warning(request, "You cannot unfollow yourself.")
        return redirect("common:user-posts", username=username)

    me   = actor.profile
    them = target_user.profile

    with transaction.atomic():
        if me.following.filter(pk=them.pk).exists():
            me.following.remove(them)               # also removes reverse link
            me.following_requests.remove(them)      # clean up stray pending
            them.follow_requests.remove(me)

            Notification.objects.filter(
                recipient=target_user,
                actor=actor,
                notification_type=NotificationType.FOLLOW,
            ).delete()

            messages.success(request, f"You have unfollowed @{username}.")
        else:
            messages.info(request, f"You are not following @{username}.")

    return redirect("common:user-posts", username=username)


# ───────────────────────────────────────────────────────────
# Accept follow request
# ───────────────────────────────────────────────────────────
@login_required
def accept_follow_request(request, request_profile_id: int):
    me        = request.user.profile
    requester = get_object_or_404(Profile.objects.select_related("user"),
                                  pk=request_profile_id)

    with transaction.atomic():
        if me.follow_requests.filter(pk=requester.pk).exists():
            me.follow_requests.remove(requester)
            requester.following_requests.remove(me)

            requester.following.add(me)             # single write

            _notify(recipient=requester.user,
                    actor=request.user,
                    notif_type=NotificationType.ACCEPT_FOLLOW_REQ)

            Notification.objects.filter(
                notification_type=NotificationType.ACCEPT_FOLLOW_REQ,
                recipient=request.user,
                actor=requester.user,
            ).delete()

            messages.success(request,
                             f"You accepted @{requester.user.username}'s request.")
        else:
            messages.warning(request, "No such follow request found.")

    return redirect("connections:view-follow-requests")


# ───────────────────────────────────────────────────────────
# Decline follow request
# ───────────────────────────────────────────────────────────
@login_required
def decline_follow_request(request, request_profile_id: int):
    me        = request.user.profile
    requester = get_object_or_404(Profile.objects.select_related("user"),
                                  pk=request_profile_id)

    with transaction.atomic():
        if me.follow_requests.filter(pk=requester.pk).exists():
            me.follow_requests.remove(requester)
            requester.following_requests.remove(me)

            Notification.objects.filter(
                notification_type=NotificationType.FOLLOW_REQUEST,
                recipient=request.user,
                actor=requester.user,
            ).delete()

            messages.info(request,
                          f"You declined @{requester.user.username}'s request.")
        else:
            messages.warning(request, "No such follow request found.")

    return redirect("connections:view-follow-requests")


# ───────────────────────────────────────────────────────────
# View pending follow requests
# ───────────────────────────────────────────────────────────
@login_required
def view_follow_requests(request):
    requests_qs = (
        request.user.profile.follow_requests
            .select_related("user")      # avoids N+1 in template
    )
    return render(
        request,
        "digital_campus/follow_requests.html",
        {"requests_list": requests_qs},
    )
