from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.urls import reverse
from django.contrib.auth.models import User
from .forms import RegistrationForm
from .models import UserProfile

class CustomLoginView(LoginView):
    template_name = "registration/login.html"

    def get_success_url(self):
        return reverse("usuarios:perfil", kwargs={"pk": self.request.user.pk})


def cadastro_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data.get("email")
            user.first_name = form.cleaned_data.get("first_name")
            user.save()
            profile = getattr(user, "profile", None)
            if profile is None:
                profile = UserProfile.objects.create(user=user)
            profile.phone_number = form.cleaned_data.get("phone_number", "")
            profile.city = form.cleaned_data.get("city", "")
            profile.state = form.cleaned_data.get("state", "")
            profile.save()
            login(request, user)
            messages.success(request, "Cadastro realizado com sucesso.")
            return redirect("usuarios:perfil", pk=user.pk)
    else:
        form = RegistrationForm()
    return render(request, "usuarios/cadastro.html", {"form": form})

@login_required
def perfil_view(request, pk):

    usuario = get_object_or_404(User, pk=pk)
    if request.user.pk != usuario.pk:
        messages.error(request, "Acesso negado: você só pode ver seu próprio perfil.")
        return redirect("usuarios:perfil", pk=request.user.pk)
    return render(request, "usuarios/perfil.html", {"usuario": usuario})
