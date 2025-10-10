from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.conf import settings

@receiver(post_migrate)
def criar_dados_iniciais(sender, **kwargs):
    """
    Cria dados iniciais (usuários e algumas propriedades) após migrate,
    somente se não houver usuários na base (apenas dev).
    """
    if settings.DEBUG is False:
        return

    User = get_user_model()
    if User.objects.exists():
        return 

    u1 = User.objects.create_user(username="alice@example.com", email="alice@example.com", password="12345678", first_name="Alice")
    u2 = User.objects.create_user(username="bob@example.com", email="bob@example.com", password="12345678", first_name="Bob")

    try:
        from usuarios.models import UserProfile
        UserProfile.objects.filter(user=u1).update(phone_number="(11) 99999-0001", is_host=True, city="Campinas", state="SP")
        UserProfile.objects.filter(user=u2).update(phone_number="(11) 99999-0002", is_host=False, city="Piracicaba", state="SP")
    except Exception:
        pass

    try:
        from propriedades.models import Propriedade, PropriedadeImagem
        p1 = Propriedade.objects.create(owner=u1, titulo="Apartamento central - 1 quarto", descricao="Ótimo para casal", city="Campinas", state="SP", endereco="Rua A, 123", preco_por_noite=120.00, ativo=True)
        p2 = Propriedade.objects.create(owner=u1, titulo="Casa com quintal", descricao="Espaçosa e confortável", city="Campinas", state="SP", endereco="Rua B, 45", preco_por_noite=250.00, ativo=True)
    except Exception:
        pass
