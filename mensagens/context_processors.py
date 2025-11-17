from .models import Message


def unread_count(request):
    if not request.user.is_authenticated:
        return {}
    # messages not read by the user and not sent by the user
    count = Message.objects.exclude(read_by=request.user).exclude(sender=request.user).filter(conversation__participants=request.user).count()
    return {'unread_messages_count': count}
