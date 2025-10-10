from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Reserva
from propriedades.models import Propriedade
from django.utils.dateparse import parse_date

@login_required
def nova_reserva(request, prop_id):
    prop = get_object_or_404(Propriedade, id=prop_id)
    if request.method == "POST":
        inicio = parse_date(request.POST.get("inicio"))
        fim = parse_date(request.POST.get("fim"))
        # TODO: checar disponibilidade
        Reserva.objects.create(guest=request.user, propriedade=prop, inicio=inicio, fim=fim)
        return redirect("reservas:minhas")
    return render(request, "reservas/nova.html", {"propriedade": prop})

@login_required
def minhas_reservas(request):
    reservas = request.user.reservas_feitas.all()
    return render(request, "reservas/minhas.html", {"reservas": reservas})
