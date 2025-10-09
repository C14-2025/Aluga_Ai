# API Documentation - Sistema de Reservas Aluga_Ai

## Visão Geral

Esta documentação descreve a API REST do sistema de reservas de imóveis Aluga_Ai, construída com Django REST Framework.

## Autenticação

A API utiliza JWT (JSON Web Tokens) para autenticação. Para acessar endpoints protegidos, inclua o token no header:

```
Authorization: Bearer <seu_token>
```

### Endpoints de Autenticação

- `POST /api/register/` - Registrar novo usuário
- `POST /api/token/` - Obter token de acesso
- `POST /api/token/refresh/` - Renovar token

## Endpoints da API

### 1. Imóveis

#### Listar Imóveis
```
GET /api/imoveis/
```

**Parâmetros de Query:**
- `tipo` - Tipo do imóvel (apartamento, casa, studio, loft)
- `cidade` - Cidade do imóvel
- `bairro` - Bairro do imóvel
- `quartos` - Número de quartos
- `banheiros` - Número de banheiros
- `aceita_pets` - Aceita animais (true/false)
- `mobiliado` - Mobiliado (true/false)
- `preco_min` - Preço mínimo
- `preco_max` - Preço máximo
- `hospedes` - Número de hóspedes
- `checkin` - Data de check-in (YYYY-MM-DD)
- `checkout` - Data de checkout (YYYY-MM-DD)
- `search` - Busca por texto
- `ordering` - Ordenação (preco_aluguel, nota_media, criado_em)

**Exemplo:**
```
GET /api/imoveis/?cidade=São Paulo&preco_min=1000&preco_max=2000&hospedes=2
```

#### Detalhes do Imóvel
```
GET /api/imoveis/{id}/
```

#### Verificar Disponibilidade
```
GET /api/imoveis/{id}/disponibilidade/?checkin=2024-01-15&checkout=2024-01-20
```

#### Avaliações do Imóvel
```
GET /api/imoveis/{id}/avaliacoes/
```

### 2. Reservas

#### Listar Reservas
```
GET /api/reservas/
```

**Parâmetros de Query:**
- `status` - Status da reserva (pendente, confirmada, cancelada, concluida, rejeitada)
- `imovel` - ID do imóvel
- `data_checkin` - Data de check-in
- `data_checkout` - Data de checkout
- `anfitriao` - Ver reservas como anfitrião (true/false)

#### Criar Reserva
```
POST /api/reservas/
```

**Body:**
```json
{
    "imovel": "uuid-do-imovel",
    "data_checkin": "2024-01-15",
    "data_checkout": "2024-01-20",
    "numero_hospedes": 2,
    "observacoes": "Observações opcionais"
}
```

#### Detalhes da Reserva
```
GET /api/reservas/{id}/
```

#### Confirmar Reserva (Anfitrião)
```
POST /api/reservas/{id}/confirmar/
```

#### Cancelar Reserva
```
POST /api/reservas/{id}/cancelar/
```

**Body:**
```json
{
    "motivo": "Motivo do cancelamento"
}
```

#### Concluir Reserva (Anfitrião)
```
POST /api/reservas/{id}/concluir/
```

#### Minhas Reservas
```
GET /api/reservas/minhas/
```

#### Reservas como Anfitrião
```
GET /api/reservas/como-anfitriao/
```

### 3. Avaliações

#### Listar Avaliações
```
GET /api/avaliacoes/
```

#### Criar Avaliação
```
POST /api/avaliacoes/
```

**Body:**
```json
{
    "reserva": "uuid-da-reserva",
    "nota": 5,
    "comentario": "Excelente estadia!",
    "limpeza": 5,
    "comunicacao": 5,
    "localizacao": 4,
    "valor": 5
}
```

#### Avaliações por Imóvel
```
GET /api/avaliacoes/por-imovel/?imovel_id=uuid-do-imovel
```

## Modelos de Dados

### Imóvel
```json
{
    "id": "uuid",
    "tipo": "apartamento",
    "cidade": "São Paulo",
    "bairro": "Centro",
    "rua": "Rua das Flores",
    "numero": "123",
    "cep": "01234-567",
    "complemento": "Apto 101",
    "latitude": -23.5505,
    "longitude": -46.6333,
    "quartos": 2,
    "banheiros": 1,
    "vagas_garagem": 1,
    "area_m2": 60,
    "andar": 5,
    "ano_construcao": 2020,
    "preco_aluguel": "1500.00",
    "condominio": "200.00",
    "iptu": "100.00",
    "descricao": "Apartamento aconchegante",
    "comodidades": ["Wi-Fi", "Ar-condicionado", "Cozinha"],
    "regras_casa": ["Proibido fumar", "Não permite festas"],
    "tags": ["Pet friendly", "Próximo ao metrô"],
    "status": "ativo",
    "mobiliado": true,
    "aceita_pets": true,
    "wifi": true,
    "max_hospedes": 4,
    "camas": 2,
    "tipo_cama": "Casal",
    "politica_cancelamento": "moderada",
    "checkin_hora": "14:00",
    "checkout_hora": "11:00",
    "nota_media": "4.50",
    "total_avaliacoes": 10,
    "anfitriao": "uuid-do-usuario",
    "anfitriao_nome": "João Silva",
    "anfitriao_superhost": true,
    "tempo_anuncio_meses": 6,
    "criado_em": "2024-01-01T10:00:00Z",
    "atualizado_em": "2024-01-15T15:30:00Z",
    "endereco_completo": "Rua das Flores, 123 - Centro, São Paulo",
    "preco_total_mensal": "1800.00"
}
```

### Reserva
```json
{
    "id": "uuid",
    "imovel": "uuid-do-imovel",
    "imovel_info": { /* dados do imóvel */ },
    "hospede": "uuid-do-usuario",
    "hospede_nome": "Maria Silva",
    "data_checkin": "2024-01-15",
    "data_checkout": "2024-01-20",
    "numero_hospedes": 2,
    "status": "confirmada",
    "preco_total": "4500.00",
    "preco_por_noite": "1500.00",
    "numero_noites": 3,
    "taxa_limpeza": "50.00",
    "taxa_servico": "450.00",
    "desconto": "0.00",
    "observacoes": "Observações da reserva",
    "motivo_cancelamento": null,
    "criado_em": "2024-01-10T10:00:00Z",
    "atualizado_em": "2024-01-12T15:30:00Z",
    "confirmado_em": "2024-01-12T15:30:00Z",
    "cancelado_em": null,
    "pode_cancelar": true,
    "esta_ativa": false
}
```

### Avaliação
```json
{
    "id": "uuid",
    "reserva": "uuid-da-reserva",
    "reserva_info": { /* dados da reserva */ },
    "nota": 5,
    "comentario": "Excelente estadia!",
    "limpeza": 5,
    "comunicacao": 5,
    "localizacao": 4,
    "valor": 5,
    "criado_em": "2024-01-25T10:00:00Z"
}
```

## Códigos de Status HTTP

- `200 OK` - Sucesso
- `201 Created` - Recurso criado com sucesso
- `400 Bad Request` - Dados inválidos
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro interno do servidor

## Exemplos de Uso

### 1. Buscar Imóveis Disponíveis

```bash
curl -X GET "http://localhost:8000/api/imoveis/?cidade=São Paulo&preco_max=2000&hospedes=2&checkin=2024-01-15&checkout=2024-01-20"
```

### 2. Criar Reserva

```bash
curl -X POST "http://localhost:8000/api/reservas/" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "imovel": "uuid-do-imovel",
    "data_checkin": "2024-01-15",
    "data_checkout": "2024-01-20",
    "numero_hospedes": 2,
    "observacoes": "Primeira estadia"
  }'
```

### 3. Confirmar Reserva

```bash
curl -X POST "http://localhost:8000/api/reservas/uuid-da-reserva/confirmar/" \
  -H "Authorization: Bearer <token_anfitriao>"
```

### 4. Avaliar Reserva

```bash
curl -X POST "http://localhost:8000/api/avaliacoes/" \
  -H "Authorization: Bearer <seu_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "reserva": "uuid-da-reserva",
    "nota": 5,
    "comentario": "Excelente estadia!",
    "limpeza": 5,
    "comunicacao": 5,
    "localizacao": 4,
    "valor": 5
  }'
```

## Validações e Regras de Negócio

### Reservas
- Não é possível criar reservas para datas no passado
- Não é possível criar reservas com checkout anterior ao check-in
- Período máximo de estadia: 30 dias
- Número de hóspedes não pode exceder a capacidade do imóvel
- Não é possível criar reservas conflitantes para o mesmo imóvel

### Cancelamentos
- Reservas só podem ser canceladas até 1 dia antes do check-in
- Reservas canceladas ou concluídas não podem ser alteradas

### Avaliações
- Só é possível avaliar reservas concluídas
- Cada reserva só pode ter uma avaliação
- A nota média do imóvel é atualizada automaticamente

## Filtros e Busca

### Filtros Disponíveis
- **Imóveis**: tipo, cidade, bairro, quartos, banheiros, aceita_pets, mobiliado
- **Reservas**: status, imovel, data_checkin, data_checkout
- **Avaliações**: por imóvel

### Busca por Texto
- **Imóveis**: cidade, bairro, descrição, comodidades, tags

### Ordenação
- **Imóveis**: preco_aluguel, nota_media, criado_em
- **Reservas**: criado_em, data_checkin, preco_total

## Limitações e Considerações

1. **Autenticação**: Todos os endpoints de reservas e avaliações requerem autenticação
2. **Permissões**: Apenas anfitriões podem confirmar/concluir reservas
3. **Validações**: Datas devem estar no formato ISO (YYYY-MM-DD)
4. **Preços**: Valores são armazenados como Decimal com 2 casas decimais
5. **UUIDs**: Todos os IDs são UUIDs para maior segurança

## Suporte

Para dúvidas ou problemas com a API, consulte os logs do servidor ou entre em contato com a equipe de desenvolvimento.
