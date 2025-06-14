# chat/views.py
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage, ChatAttachment
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from .forms import GroupChatForm

@login_required
def chat_room(request, room_name):
    """
    Render the chat page for a given room and ensure
    the current user is a participant in that room.
    """
    room = get_object_or_404(ChatRoom, name=room_name)

    
    # Make sure the user is a participant
    if request.user not in room.participants.all():
        room.participants.add(request.user)
    
    # Load previous messages to display
    messages = room.messages.select_related('user').prefetch_related('attachments').order_by('timestamp')
    
    return render(request, 'chat/chat_room.html', {
        'room_name': room_name,
        'messages': messages,  # pass these to the template
    })


@csrf_exempt
@login_required
def file_upload(request):
    """
    Handle file uploads for chat via HTTP POST.
    """
    if request.method == 'POST':
        file_obj = request.FILES.get('file')
        room_name = request.POST.get('room_name', '')
        if not file_obj or not room_name:
            return JsonResponse({'error': 'No file or room_name provided'}, status=400)

        # Save the message with no text content, but an attachment
        room, _ = ChatRoom.objects.get_or_create(name=room_name)
        chat_message = ChatMessage.objects.create(
            room=room,
            user=request.user,
            content=''  # or maybe 'Photo/Video uploaded'
        )
        ChatAttachment.objects.create(
            chat_message=chat_message,
            file=file_obj
        )

        # Optionally, broadcast a WebSocket message about the new file
        # (You can do a channel_layer send from here if needed.)
        return JsonResponse({'message': 'File uploaded successfully'})
    return JsonResponse({'error': 'Invalid request'}, status=400)

@login_required
def get_or_create_private_chat(user_a, user_b):
    room_name = get_private_room_name(user_a, user_b)
    room, created = ChatRoom.objects.get_or_create(name=room_name, is_private=True)
    if user_a not in room.participants.all():
        room.participants.add(user_a)
    if user_b not in room.participants.all():
        room.participants.add(user_b)
    return room

@login_required
def get_private_room_name(user_a, user_b):
    # Sort by id to keep consistent naming
    sorted_users = sorted([user_a.id, user_b.id])
    return f"private_{sorted_users[0]}_{sorted_users[1]}"

@login_required
def start_private_chat(request, username):
    try:
        other_user = User.objects.get(username=username)
    except User.DoesNotExist:
        # handle error
        return redirect('some_error_page')

    room = get_or_create_private_chat(request.user, other_user)
    return redirect('chat-room', room_name=room.name)

@login_required
def create_group_chat(request):
    if request.method == 'POST':
        form = GroupChatForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            participants = form.cleaned_data['participants']
            icon = form.cleaned_data.get('room_icon')
            # Create the group chat
            room = ChatRoom.objects.create(name=name, is_private=False)
            if icon:
                room.room_icon = icon
                room.save()
            
            # Add the creator and participants
            room.participants.add(request.user)
            for p in participants:
                room.participants.add(p)
            
            return redirect('chat-room', room_name=room.name)
    else:
        form = GroupChatForm()

    return render(request, 'chat/create_group_chat.html', {'form': form})

@login_required
def add_user_to_group(request, room_name):
    if request.method == 'POST':
        username_to_add = request.POST.get('username')
        try:
            user_to_add = User.objects.get(username=username_to_add)
            room = ChatRoom.objects.get(name=room_name, is_private=False)
            # Optionally check if request.user is authorized to add (owner, admin, etc.)
            room.participants.add(user_to_add)
        except (User.DoesNotExist, ChatRoom.DoesNotExist):
            pass
        return redirect('chat-room', room_name=room_name)

