from django.shortcuts import render
from .models import Topic, Entry
from .forms import TopicForm, EntryForm
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    """The home page for Aluga_ai."""
    return render(request, 'aluga_ais/index.html')

def cadastro(request):
    """Cadastro de usuario."""
    return render(request, 'aluga_ais/cadastro.html', context)
