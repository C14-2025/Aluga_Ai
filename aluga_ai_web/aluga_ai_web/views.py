from django.http import JsonResponse
from BancoDeDados.Integracao import obter_dados_tabela

def listar_imoveis(request):
    dados = obter_dados_tabela("ImoveisDisponiveis", "*", 20)
    return JsonResponse(dados, safe=False)
