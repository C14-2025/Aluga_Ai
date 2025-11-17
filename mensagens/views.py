from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from .models import Conversation, Message
from django.contrib.auth.models import User
from django.views.decorators.http import require_POST
from django.shortcuts import resolve_url
from propriedades.models import Propriedade


@login_required
def conversations_list(request):
    convs = request.user.conversations.all().prefetch_related('participants')
    # build list of (conversation, unread_count)
    convs_info = []
    for c in convs:
        cnt = c.messages.exclude(read_by=request.user).exclude(sender=request.user).count()
        convs_info.append({'conversation': c, 'unread': cnt})
    return render(request, 'mensagens/list.html', {'conversations_info': convs_info})


@login_required
def conversation_detail(request, pk):
    conv = get_object_or_404(Conversation, pk=pk)
    if not conv.participants.filter(pk=request.user.pk).exists():
        return HttpResponseForbidden()
    messages = conv.messages.select_related('sender').all()
    # mark messages as read for this user
    for m in messages.exclude(read_by=request.user):
        m.read_by.add(request.user)
    return render(request, 'mensagens/detail.html', {'conversation': conv, 'messages': messages})


@login_required
def ajax_get_messages(request, pk):
    conv = get_object_or_404(Conversation, pk=pk)
    if not conv.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'forbidden'}, status=403)
    msgs = list(conv.messages.select_related('sender').values('id', 'sender__id', 'sender__username', 'content', 'created_at'))
    return JsonResponse({'messages': msgs})


@login_required
@require_POST
def ajax_send_message(request, pk):
    conv = get_object_or_404(Conversation, pk=pk)
    if not conv.participants.filter(pk=request.user.pk).exists():
        return JsonResponse({'error': 'forbidden'}, status=403)
    content = request.POST.get('content', '').strip()
    if not content:
        return JsonResponse({'error': 'empty'}, status=400)
    msg = Message.objects.create(conversation=conv, sender=request.user, content=content)
    return JsonResponse({'id': msg.pk, 'content': msg.content, 'sender': request.user.username, 'created_at': msg.created_at})


@login_required
def start_conversation(request, user_id, prop_id=None):
    other = get_object_or_404(User, pk=user_id)
    if other == request.user:
        return redirect('mensagens:list')
    # find existing conversation with exactly these two participants
    conv = Conversation.objects.filter(participants=request.user).filter(participants=other).first()
    if not conv:
        conv = Conversation.objects.create()
        conv.participants.add(request.user, other)
    # optional: attach property reference via querystring or messages
    return redirect('mensagens:detail', pk=conv.pk)
