from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Imovel, Reserva, Avaliacao
from datetime import date, timedelta

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email')

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )
        return user

class ImovelSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Imovel"""
    endereco_completo = serializers.ReadOnlyField()
    preco_total_mensal = serializers.ReadOnlyField()
    anfitriao_nome = serializers.CharField(source='anfitriao.first_name', read_only=True)
    
    class Meta:
        model = Imovel
        fields = [
            'id', 'tipo', 'cidade', 'bairro', 'rua', 'numero', 'cep', 'complemento',
            'latitude', 'longitude', 'quartos', 'banheiros', 'vagas_garagem',
            'area_m2', 'andar', 'ano_construcao', 'preco_aluguel', 'condominio',
            'iptu', 'descricao', 'comodidades', 'regras_casa', 'tags', 'status',
            'mobiliado', 'aceita_pets', 'wifi', 'max_hospedes', 'camas',
            'tipo_cama', 'politica_cancelamento', 'checkin_hora', 'checkout_hora',
            'nota_media', 'total_avaliacoes', 'anfitriao', 'anfitriao_nome',
            'anfitriao_superhost', 'tempo_anuncio_meses', 'criado_em', 'atualizado_em',
            'endereco_completo', 'preco_total_mensal'
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'nota_media', 'total_avaliacoes']

class ImovelListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listagem de imóveis"""
    endereco_completo = serializers.ReadOnlyField()
    anfitriao_nome = serializers.CharField(source='anfitriao.first_name', read_only=True)
    
    class Meta:
        model = Imovel
        fields = [
            'id', 'tipo', 'cidade', 'bairro', 'endereco_completo', 'quartos',
            'banheiros', 'area_m2', 'preco_aluguel', 'nota_media', 'total_avaliacoes',
            'comodidades', 'tags', 'anfitriao_nome', 'anfitriao_superhost'
        ]

class ReservaSerializer(serializers.ModelSerializer):
    """Serializer para o modelo Reserva"""
    imovel_info = ImovelListSerializer(source='imovel', read_only=True)
    hospede_nome = serializers.CharField(source='hospede.first_name', read_only=True)
    pode_cancelar = serializers.ReadOnlyField()
    esta_ativa = serializers.ReadOnlyField()
    
    class Meta:
        model = Reserva
        fields = [
            'id', 'imovel', 'imovel_info', 'hospede', 'hospede_nome',
            'data_checkin', 'data_checkout', 'numero_hospedes', 'status',
            'preco_total', 'preco_por_noite', 'numero_noites', 'taxa_limpeza',
            'taxa_servico', 'desconto', 'observacoes', 'motivo_cancelamento',
            'criado_em', 'atualizado_em', 'confirmado_em', 'cancelado_em',
            'pode_cancelar', 'esta_ativa'
        ]
        read_only_fields = [
            'id', 'preco_total', 'preco_por_noite', 'numero_noites',
            'criado_em', 'atualizado_em', 'confirmado_em', 'cancelado_em'
        ]

class ReservaCreateSerializer(serializers.ModelSerializer):
    """Serializer para criação de reservas com validações"""
    
    class Meta:
        model = Reserva
        fields = [
            'imovel', 'data_checkin', 'data_checkout', 'numero_hospedes',
            'observacoes'
        ]
    
    def validate(self, data):
        """Validações customizadas para criação de reserva"""
        data_checkin = data.get('data_checkin')
        data_checkout = data.get('data_checkout')
        numero_hospedes = data.get('numero_hospedes')
        imovel = data.get('imovel')
        
        # Validar datas
        if data_checkin and data_checkout:
            if data_checkin < date.today():
                raise serializers.ValidationError("Data de check-in não pode ser no passado")
            
            if data_checkout <= data_checkin:
                raise serializers.ValidationError("Data de checkout deve ser posterior ao check-in")
            
            # Verificar se o período não é muito longo (máximo 30 dias)
            if (data_checkout - data_checkin).days > 30:
                raise serializers.ValidationError("Período de estadia não pode ser superior a 30 dias")
        
        # Validar número de hóspedes
        if imovel and numero_hospedes:
            if numero_hospedes > imovel.max_hospedes:
                raise serializers.ValidationError(
                    f"O imóvel suporta no máximo {imovel.max_hospedes} hóspedes"
                )
        
        # Verificar disponibilidade
        if imovel and data_checkin and data_checkout:
            reservas_conflitantes = Reserva.objects.filter(
                imovel=imovel,
                status__in=['pendente', 'confirmada'],
                data_checkin__lt=data_checkout,
                data_checkout__gt=data_checkin
            )
            if reservas_conflitantes.exists():
                raise serializers.ValidationError("O imóvel não está disponível para este período")
        
        return data
    
    def create(self, validated_data):
        """Criar reserva com cálculo automático de preços"""
        imovel = validated_data['imovel']
        data_checkin = validated_data['data_checkin']
        data_checkout = validated_data['data_checkout']
        
        # Calcular número de noites
        numero_noites = (data_checkout - data_checkin).days
        
        # Calcular preços
        preco_por_noite = imovel.preco_aluguel
        preco_base = preco_por_noite * numero_noites
        
        # Calcular taxas (exemplo: 10% do preço base)
        taxa_servico = preco_base * 0.10
        taxa_limpeza = 50.00  # Taxa fixa
        
        # Calcular desconto (exemplo: 5% para estadias longas)
        desconto = 0
        if numero_noites >= 7:
            desconto = preco_base * 0.05
        
        preco_total = preco_base + taxa_servico + taxa_limpeza - desconto
        
        # Criar reserva
        reserva = Reserva.objects.create(
            imovel=imovel,
            hospede=self.context['request'].user,
            data_checkin=data_checkin,
            data_checkout=data_checkout,
            numero_hospedes=validated_data['numero_hospedes'],
            preco_total=preco_total,
            preco_por_noite=preco_por_noite,
            numero_noites=numero_noites,
            taxa_limpeza=taxa_limpeza,
            taxa_servico=taxa_servico,
            desconto=desconto,
            observacoes=validated_data.get('observacoes', '')
        )
        
        return reserva

class ReservaUpdateSerializer(serializers.ModelSerializer):
    """Serializer para atualização de reservas"""
    
    class Meta:
        model = Reserva
        fields = ['status', 'motivo_cancelamento']
    
    def validate_status(self, value):
        """Validar mudança de status"""
        instance = self.instance
        
        # Não permitir mudanças em reservas já canceladas ou concluídas
        if instance.status in ['cancelada', 'concluida']:
            raise serializers.ValidationError("Não é possível alterar reservas canceladas ou concluídas")
        
        # Validar cancelamento
        if value == 'cancelada':
            if not instance.pode_cancelar:
                raise serializers.ValidationError("Esta reserva não pode ser cancelada")
        
        return value
    
    def update(self, instance, validated_data):
        """Atualizar reserva com timestamps"""
        from django.utils import timezone
        
        if validated_data.get('status') == 'confirmada' and instance.status != 'confirmada':
            instance.confirmado_em = timezone.now()
        elif validated_data.get('status') == 'cancelada' and instance.status != 'cancelada':
            instance.cancelado_em = timezone.now()
        
        return super().update(instance, validated_data)

class AvaliacaoSerializer(serializers.ModelSerializer):
    """Serializer para avaliações"""
    reserva_info = ReservaSerializer(source='reserva', read_only=True)
    
    class Meta:
        model = Avaliacao
        fields = [
            'id', 'reserva', 'reserva_info', 'nota', 'comentario',
            'limpeza', 'comunicacao', 'localizacao', 'valor', 'criado_em'
        ]
        read_only_fields = ['id', 'criado_em']
    
    def validate(self, data):
        """Validar se a reserva pode ser avaliada"""
        reserva = data.get('reserva')
        
        if reserva:
            # Só pode avaliar reservas concluídas
            if reserva.status != 'concluida':
                raise serializers.ValidationError("Só é possível avaliar reservas concluídas")
            
            # Verificar se já existe avaliação
            if Avaliacao.objects.filter(reserva=reserva).exists():
                raise serializers.ValidationError("Esta reserva já foi avaliada")
        
        return data
    
    def create(self, validated_data):
        """Criar avaliação e atualizar nota média do imóvel"""
        avaliacao = super().create(validated_data)
        
        # Atualizar nota média do imóvel
        imovel = avaliacao.reserva.imovel
        avaliacoes = Avaliacao.objects.filter(reserva__imovel=imovel)
        
        if avaliacoes.exists():
            nota_media = sum(a.nota for a in avaliacoes) / avaliacoes.count()
            imovel.nota_media = round(nota_media, 2)
            imovel.total_avaliacoes = avaliacoes.count()
            imovel.save()
        
        return avaliacao
