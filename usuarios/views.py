from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib import messages

def cadastro_view(request):
    if request.method == "POST":
        nome = request.POST.get("nome", "").strip()
        email = request.POST.get("email", "").strip()
        telefone = request.POST.get("telefone", "").strip()

        if not email:
            messages.error(request, "Email é obrigatório.")
            return redirect("usuarios:cadastro")

        username = email  # simplificação: username = email
        # se já existe, apenas atualiza nome/telefone (ou avisa)
        user, created = User.objects.get_or_create(username=username, defaults={
            "first_name": nome,
            "email": email,
        })
        if not created:
            # atualiza nome/email
            user.first_name = nome or user.first_name
            user.email = email or user.email
            user.save()

        # opcional: armazenar telefone em profile se existir profile model
        try:
            profile = user.profile
            profile.phone_number = telefone
            profile.save()
        except Exception:
            # se não existir profile, ignore — não é crítico para agora
            pass

        messages.success(request, "Cadastro realizado com sucesso.")
        return redirect("usuarios:lista")

    return render(request, "usuarios/cadastro.html")


def lista_usuarios(request):
    users = User.objects.all().order_by("id")
    return render(request, "usuarios/lista.html", {"users": users})
