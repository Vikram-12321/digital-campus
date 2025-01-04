from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

#Models
from django.contrib.auth.models import User
from apps.users.models import Profile

class Follow():
    
    @login_required
    def follow_user(self, request, username):
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
    def unfollow_user(self, request, username):
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
    def accept_follow_request(self, request, request_profile_id):
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
    def decline_follow_request(self, request, request_profile_id):
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
    def view_follow_requests(self, request):
        """
        Show all profiles that have requested to follow the current user (if user is private).
        """
        current_profile = request.user.profile
        # These are the profiles that want to follow me
        requests_list = current_profile.follow_requests.all()

        return render(request, 'digital_campus/follow_requests.html', {
            'requests_list': requests_list
        })