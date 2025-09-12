# Aluga_Ai - Consulta de API de estabelecimentos


Este projeto realiza chamadas à API [Realtor API Data](https://rapidapi.com/) para obter detalhes de escolas utilizando Python. Ele também inclui testes automatizados com pytest para garantir que a requisição está funcionando corretamente.

## Estrutura dos Arquivos
```bash
aluga_ai_web/
│
├── aluga_ai_web/ # Configuração principal do Django
│ ├── settings.py
│ ├── urls.py
│ └── wsgi.py
│
├── reservas/ # App responsável pelas reservas
│ ├── views.py
│ ├── models.py
│ └── urls.py
│
├── API/ # Integrações externas
│ ├── ChamadaApi.py
│ ├── TesteApi.py
│ └── init.py
│
├── manage.py
```
- `API/ChamadaApi.py`: Funções para realizar a chamada à API e retornar o status HTTP.
- `API/TesteApi.py`: Teste automatizado usando pytest.

## Como usar

### 1. Instale as dependências

Certifique-se de ter o Python instalado. Para rodar o servidor e os testes, instale o pytest e o django:

```bash
pip install pytest django
```

### 2. Realize a chamada à API

Você pode importar e usar a função `chamada_api()` para obter os dados da escola em formato JSON (string).

### 3. Rode o servidor

```bash
cd aluga_ai_web
python manage.py runserver
```
127.0.0.1:8000/consulta/ vai ser exibido os dados da API

### 4. Execute os testes

Para rodar o teste automatizado e verificar se a API está respondendo corretamente:

```bash
pytest aluga_ai_web/API/TesteApi.py
```

## Observações

- O projeto utiliza uma chave de API do RapidAPI. Certifique-se de não expor sua chave em ambientes públicos.
- O endpoint utilizado consulta detalhes de uma escola específica (`id=0717323601`).

---
