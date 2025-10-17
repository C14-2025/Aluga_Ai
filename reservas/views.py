from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from propriedades.models import Propriedade
from .models import Reserva
from django.utils.dateparse import parse_date
from django.contrib import messages

@login_required
def nova_reserva(request, prop_id):
    prop = get_object_or_404(Propriedade, id=prop_id)
    if request.method == "POST":
        inicio = parse_date(request.POST.get("inicio"))
        fim = parse_date(request.POST.get("fim"))
        if not inicio or not fim or inicio > fim:
            messages.error(request, "Datas inválidas.")
            return redirect("reservas:nova", prop_id=prop_id)

        # checagem de disponibilidade (não permite sobreposição com CONFIRMADA)
        conflitos = Reserva.objects.filter(propriedade=prop, status="CONFIRMADA").filter(
            inicio__lte=fim, fim__gte=inicio
        )
        if conflitos.exists():
            messages.error(request, "Datas indisponíveis.")
            return redirect("propriedades:detalhe", pk=prop.pk)

        Reserva.objects.create(guest=request.user, propriedade=prop, inicio=inicio, fim=fim, status="CONFIRMADA")
        messages.success(request, "Reserva criada com sucesso (confirmada).")
        return redirect("reservas:minhas")

    return render(request, "reservas/nova.html", {"propriedade": prop})

@login_required
def minhas_reservas(request):
    reservas = request.user.reservas_feitas.all()
    return render(request, "reservas/minhas.html", {"reservas": reservas})
