# channels/views.py
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from .models import ChatRoom, ChatMessage, ChatAttachment
from django.views.decorators.csrf import csrf_exempt

@login_required
def chat_room(request, room_name):
    """
    Render the chat page for a given room and ensure
    the current user is a participant in that room.
    """
    room, created = ChatRoom.objects.get_or_create(name=room_name)
    
    # Make sure the user is a participant
    if request.user not in room.participants.all():
        room.participants.add(request.user)
    
    # Load previous messages to display
    messages = room.messages.select_related('user').order_by('timestamp')
    
    return render(request, 'channels/chat_room.html', {
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
