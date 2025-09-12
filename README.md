# Aluga_Ai - Consulta de API de Escolas

Este projeto realiza chamadas à API [Realtor API Data](https://rapidapi.com/) para obter detalhes de escolas utilizando Python. Ele também inclui testes automatizados com pytest para garantir que a requisição está funcionando corretamente.

## Estrutura dos Arquivos

- `API/ChamadaApi.py`: Funções para realizar a chamada à API e retornar o status HTTP.
- `API/TesteApi.py`: Teste automatizado usando pytest para verificar se a resposta da API é bem-sucedida (status 200).

## Como usar

### 1. Instale as dependências

Certifique-se de ter o Python instalado. Para rodar os testes, instale o pytest:

```bash
pip install pytest
```

### 2. Realize a chamada à API

Você pode importar e usar a função `chamada_api()` para obter os dados da escola em formato JSON (string).

### 3. Execute os testes

Para rodar o teste automatizado e verificar se a API está respondendo corretamente:

```bash
pytest API/TesteApi.py
```

O teste irá passar se o status HTTP retornado for 200.

## Observações

- O projeto utiliza uma chave de API do RapidAPI. Certifique-se de não expor sua chave em ambientes públicos.
- O endpoint utilizado consulta detalhes de uma escola específica (`id=0717323601`).

---
