from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from propriedades.models import Propriedade
from .models import Reserva
from django.utils.dateparse import parse_date
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse

@login_required
def nova_reserva(request, prop_id):
    prop = get_object_or_404(Propriedade, id=prop_id)
    # não permitir que o dono reserve o próprio imóvel
    if prop.owner == request.user:
        messages.error(request, "Você não pode solicitar reserva do seu próprio imóvel.")
        return redirect("propriedades:detalhe", pk=prop.pk)

    # não permitir reserva em imóvel inativo
    if not prop.ativo:
        messages.error(request, "Este imóvel não está disponível para reservas no momento.")
        return redirect("propriedades:detalhe", pk=prop.pk)
    if request.method == "POST":
        inicio = parse_date(request.POST.get("inicio"))
        fim = parse_date(request.POST.get("fim"))
        if not inicio or not fim or inicio > fim:
            messages.error(request, "Datas inválidas.")
            return redirect("reservas:nova", prop_id=prop_id)

        # checagem de disponibilidade (não permite sobreposição com CONFIRMADA)
        conflitos = Reserva.objects.filter(propriedade=prop, status=Reserva.STATUS_CONFIRMED).filter(
            inicio__lte=fim, fim__gte=inicio
        )
        if conflitos.exists():
            messages.error(request, "Datas indisponíveis.")
            return redirect("propriedades:detalhe", pk=prop.pk)

        reserva = Reserva.objects.create(guest=request.user, propriedade=prop, inicio=inicio, fim=fim)
        messages.success(request, "Solicitação de reserva enviada. Aguarde a confirmação do anfitrião.")
        return redirect("reservas:minhas")

    return render(request, "reservas/nova.html", {"propriedade": prop})

@login_required
def minhas_reservas(request):
    reservas = request.user.reservas_feitas.all()
    return render(request, "reservas/minhas.html", {"reservas": reservas})


@login_required
def solicitacoes_recebidas(request):
    # solicitações para propriedades cujo owner é o usuário
    reservas = Reserva.objects.filter(propriedade__owner=request.user).exclude(status=Reserva.STATUS_CANCELLED)
    return render(request, "reservas/recebidas.html", {"reservas": reservas})


@login_required
def reserva_acao(request, reserva_id, acao):
    reserva = get_object_or_404(Reserva, id=reserva_id)
    # apenas o dono da propriedade pode agir
    if reserva.propriedade.owner != request.user:
        return HttpResponseForbidden("Você não pode executar essa ação.")

    if acao == "confirmar":
        # checar conflitos antes de confirmar
        conflitos = Reserva.objects.filter(propriedade=reserva.propriedade, status=Reserva.STATUS_CONFIRMED).filter(
            inicio__lte=reserva.fim, fim__gte=reserva.inicio
        ).exclude(pk=reserva.pk)
        if conflitos.exists():
            messages.error(request, "Não é possível confirmar: existe conflito de datas com outra reserva confirmada.")
        else:
            reserva.confirm()
            messages.success(request, "Reserva confirmada.")
    elif acao == "recusar":
        reserva.cancel()
        messages.info(request, "Reserva recusada/cancelada.")
    else:
        messages.error(request, "Ação desconhecida.")

    return redirect(reverse("reservas:recebidas"))
