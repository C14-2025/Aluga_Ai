from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from .forms import RegistrationForm
from django.contrib.auth.models import User

def cadastro_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.first_name = form.cleaned_data.get("first_name")
            user.save()
            profile = getattr(user, "profile", None)
            if profile:
                profile.phone_number = form.cleaned_data.get("phone_number", "")
                profile.city = form.cleaned_data.get("city", "")
                profile.state = form.cleaned_data.get("state", "")
                profile.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("propriedades:lista")
    else:
        form = RegistrationForm()
    return render(request, "usuarios/cadastro.html", {"form": form})

@login_required
def perfil_view(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    return render(request, "usuarios/perfil.html", {"usuario": usuario})
