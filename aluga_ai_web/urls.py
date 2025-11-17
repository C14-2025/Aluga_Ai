from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("propriedades.urls")),
    path("usuarios/", include("usuarios.urls")),
    path("reservas/", include("reservas.urls")),
    path("avaliacoes/", include("avaliacoes.urls")),
    path("mensagens/", include("mensagens.urls")),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)