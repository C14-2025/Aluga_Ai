from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from django.utils import timezone
from datetime import date, timedelta
from .models import Imovel, Reserva, Avaliacao
from .serializers import (
    ImovelSerializer, ImovelListSerializer, ReservaSerializer, 
    ReservaCreateSerializer, ReservaUpdateSerializer, AvaliacaoSerializer,
    RegisterSerializer
)
from django.contrib.auth.models import User

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer

class ImovelViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de imóveis"""
    queryset = Imovel.objects.filter(status='ativo')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['tipo', 'cidade', 'bairro', 'quartos', 'banheiros', 'aceita_pets', 'mobiliado']
    search_fields = ['cidade', 'bairro', 'descricao', 'comodidades', 'tags']
    ordering_fields = ['preco_aluguel', 'nota_media', 'criado_em']
    ordering = ['-nota_media', '-criado_em']
    
    def get_serializer_class(self):
        if self.action == 'list':
            return ImovelListSerializer
        return ImovelSerializer
    
    def get_queryset(self):
        """Filtrar imóveis por disponibilidade e localização"""
        queryset = super().get_queryset()
        
        # Filtro por data de disponibilidade
        checkin = self.request.query_params.get('checkin')
        checkout = self.request.query_params.get('checkout')
        
        if checkin and checkout:
            # Excluir imóveis com reservas conflitantes
            reservas_conflitantes = Reserva.objects.filter(
                status__in=['pendente', 'confirmada'],
                data_checkin__lt=checkout,
                data_checkout__gt=checkin
            ).values_list('imovel_id', flat=True)
            
            queryset = queryset.exclude(id__in=reservas_conflitantes)
        
        # Filtro por faixa de preço
        preco_min = self.request.query_params.get('preco_min')
        preco_max = self.request.query_params.get('preco_max')
        
        if preco_min:
            queryset = queryset.filter(preco_aluguel__gte=preco_min)
        if preco_max:
            queryset = queryset.filter(preco_aluguel__lte=preco_max)
        
        # Filtro por número de hóspedes
        hospedes = self.request.query_params.get('hospedes')
        if hospedes:
            queryset = queryset.filter(max_hospedes__gte=hospedes)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def disponibilidade(self, request, pk=None):
        """Verificar disponibilidade de um imóvel para um período"""
        imovel = self.get_object()
        checkin = request.query_params.get('checkin')
        checkout = request.query_params.get('checkout')
        
        if not checkin or not checkout:
            return Response(
                {'error': 'Parâmetros checkin e checkout são obrigatórios'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            checkin_date = date.fromisoformat(checkin)
            checkout_date = date.fromisoformat(checkout)
        except ValueError:
            return Response(
                {'error': 'Formato de data inválido. Use YYYY-MM-DD'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar conflitos
        conflitos = Reserva.objects.filter(
            imovel=imovel,
            status__in=['pendente', 'confirmada'],
            data_checkin__lt=checkout_date,
            data_checkout__gt=checkin_date
        )
        
        disponivel = not conflitos.exists()
        
        return Response({
            'disponivel': disponivel,
            'periodo': {
                'checkin': checkin,
                'checkout': checkout,
                'noites': (checkout_date - checkin_date).days
            },
            'conflitos': conflitos.count() if not disponivel else 0
        })
    
    @action(detail=True, methods=['get'])
    def avaliacoes(self, request, pk=None):
        """Listar avaliações de um imóvel"""
        imovel = self.get_object()
        avaliacoes = Avaliacao.objects.filter(reserva__imovel=imovel).order_by('-criado_em')
        
        serializer = AvaliacaoSerializer(avaliacoes, many=True)
        return Response(serializer.data)

class ReservaViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de reservas"""
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'imovel', 'data_checkin', 'data_checkout']
    ordering_fields = ['criado_em', 'data_checkin', 'preco_total']
    ordering = ['-criado_em']
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ReservaCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ReservaUpdateSerializer
        return ReservaSerializer
    
    def get_queryset(self):
        """Filtrar reservas do usuário autenticado"""
        user = self.request.user
        
        # Se for anfitrião, mostrar reservas dos seus imóveis
        if self.action == 'list' and 'anfitriao' in self.request.query_params:
            return Reserva.objects.filter(imovel__anfitriao=user)
        
        # Por padrão, mostrar reservas do usuário como hóspede
        return Reserva.objects.filter(hospede=user)
    
    def perform_create(self, serializer):
        """Criar reserva para o usuário autenticado"""
        serializer.save(hospede=self.request.user)
    
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """Confirmar uma reserva (apenas anfitrião)"""
        reserva = self.get_object()
        
        # Verificar se o usuário é o anfitrião
        if reserva.imovel.anfitriao != request.user:
            return Response(
                {'error': 'Apenas o anfitrião pode confirmar reservas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if reserva.status != 'pendente':
            return Response(
                {'error': 'Apenas reservas pendentes podem ser confirmadas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.status = 'confirmada'
        reserva.confirmado_em = timezone.now()
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """Cancelar uma reserva"""
        reserva = self.get_object()
        motivo = request.data.get('motivo', '')
        
        # Verificar se pode cancelar
        if not reserva.pode_cancelar:
            return Response(
                {'error': 'Esta reserva não pode ser cancelada'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.status = 'cancelada'
        reserva.motivo_cancelamento = motivo
        reserva.cancelado_em = timezone.now()
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        """Marcar reserva como concluída (apenas anfitrião)"""
        reserva = self.get_object()
        
        # Verificar se o usuário é o anfitrião
        if reserva.imovel.anfitriao != request.user:
            return Response(
                {'error': 'Apenas o anfitrião pode concluir reservas'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if reserva.status != 'confirmada':
            return Response(
                {'error': 'Apenas reservas confirmadas podem ser concluídas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verificar se a data de checkout já passou
        if reserva.data_checkout > date.today():
            return Response(
                {'error': 'Apenas reservas com checkout no passado podem ser concluídas'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reserva.status = 'concluida'
        reserva.save()
        
        serializer = self.get_serializer(reserva)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def minhas_reservas(self, request):
        """Listar todas as reservas do usuário"""
        reservas = self.get_queryset()
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def como_anfitriao(self, request):
        """Listar reservas dos imóveis do usuário como anfitrião"""
        reservas = Reserva.objects.filter(imovel__anfitriao=request.user)
        serializer = self.get_serializer(reservas, many=True)
        return Response(serializer.data)

class AvaliacaoViewSet(viewsets.ModelViewSet):
    """ViewSet para gerenciamento de avaliações"""
    serializer_class = AvaliacaoSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Filtrar avaliações do usuário"""
        return Avaliacao.objects.filter(reserva__hospede=self.request.user)
    
    def perform_create(self, serializer):
        """Criar avaliação para o usuário autenticado"""
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def por_imovel(self, request):
        """Listar avaliações de um imóvel específico"""
        imovel_id = request.query_params.get('imovel_id')
        if not imovel_id:
            return Response(
                {'error': 'Parâmetro imovel_id é obrigatório'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            avaliacoes = Avaliacao.objects.filter(reserva__imovel_id=imovel_id)
            serializer = self.get_serializer(avaliacoes, many=True)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)}, 
                status=status.HTTP_400_BAD_REQUEST
            )
