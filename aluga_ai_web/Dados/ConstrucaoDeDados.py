import random
import json
from datetime import datetime, timedelta

# Tabela de preços médios por m² para bairros em cidades
precos_m2 = {
    "São Paulo": {
        "Centro": 45, "Jardim América": 80, "Moema": 70, "Pinheiros": 65
    },
    "Rio de Janeiro": {
        "Copacabana": 65, "Ipanema": 90, "Barra": 55
    },
    "Belo Horizonte": {
        "Savassi": 50, "Centro": 35
    },
    "Curitiba": {
        "Centro": 30, "Trindade": 28
    },
    "Porto Alegre": {
        "Centro": 28
    },
    "Salvador": {
        "Barra": 40, "Boa Viagem": 38
    },
    "Brasília": {
        "Centro": 50
    },
    "Fortaleza": {
        "Centro": 25
    },
    "Recife": {
        "Boa Viagem": 42
    },
    "Florianópolis": {
        "Trindade": 35
    }
}

def preco_m2_por_bairro(cidade, bairro):
    cidade_precos = precos_m2.get(cidade, {})
    return cidade_precos.get(bairro, random.randint(20, 60))

# Listas de exemplos de cidades, bairros, nomes de ruas, etc.
cidades = [
    "São Paulo", "Rio de Janeiro", "Belo Horizonte", "Curitiba", "Porto Alegre",
    "Salvador", "Brasília", "Fortaleza", "Recife", "Florianópolis"
]
bairros = [
    "Centro", "Jardim América", "Copacabana", "Savassi", "Boa Viagem",
    "Moema", "Pinheiros", "Ipanema", "Barra", "Trindade"
]
nomes_ruas = [
    "Rua das Flores", "Avenida Paulista", "Rua XV de Novembro", "Rua Augusta",
    "Rua das Palmeiras", "Avenida Atlântica", "Rua do Sol", "Rua das Acácias"
]

tipos = ["Apartamento", "Casa"]

# Novas listas de dados para enriquecer os imóveis
comodidades_possiveis = [
    "Wi-Fi", "Ar-condicionado", "Cozinha", "Estacionamento gratuito", "Piscina",
    "Máquina de lavar", "Secadora", "Aquecimento", "TV", "Academia", "Churrasqueira",
    "Varanda", "Elevador", "Aceita pets", "Vista para o mar", "Jacuzzi"
]
tipos_cama = ["Solteiro", "Casal", "Queen", "King", "Beliche", "Sofá-cama"]
politicas_cancelamento = ["Flexível", "Moderada", "Rigorosa"]
regras_possiveis = [
    "Proibido fumar", "Não permite festas/eventos", "Animais permitidos", "Silêncio após as 22h",
    "Check-in após 14h", "Check-out até 11h"
]
anfitrioes = [
    {"nome": "Ana Souza", "superhost": True, "foto": "https://randomuser.me/api/portraits/women/1.jpg"},
    {"nome": "Carlos Lima", "superhost": False, "foto": "https://randomuser.me/api/portraits/men/2.jpg"},
    {"nome": "Fernanda Alves", "superhost": True, "foto": "https://randomuser.me/api/portraits/women/3.jpg"},
    {"nome": "João Pedro", "superhost": False, "foto": "https://randomuser.me/api/portraits/men/4.jpg"},
    {"nome": "Marina Dias", "superhost": True, "foto": "https://randomuser.me/api/portraits/women/5.jpg"},
]
fotos_exemplo = [
    "https://images.unsplash.com/photo-1506744038136-46273834b3fb",
    "https://images.unsplash.com/photo-1460518451285-97b6aa326961",
    "https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd",
    "https://images.unsplash.com/photo-1522708323590-d24dbb6b0267",
    "https://images.unsplash.com/photo-1507089947368-19c1da9775ae"
]
descricoes = [
    "Apartamento aconchegante no coração da cidade, próximo a restaurantes e pontos turísticos.",
    "Casa espaçosa com piscina e área gourmet, perfeita para famílias.",
    "Estúdio moderno com vista incrível, ideal para viagens de negócios.",
    "Cobertura luxuosa com jacuzzi e vista panorâmica.",
    "Quarto privativo em casa compartilhada, ambiente tranquilo e seguro."
]

tags_possiveis = [
    "Pet friendly", "Ideal para famílias", "Próximo ao metrô", "Vista panorâmica",
    "Acessível para cadeirantes", "Bairro nobre", "Recém-reformado", "Ótima localização",
    "Silencioso", "Com varanda", "Próximo à praia", "Com escritório"
]

def gerar_comodidades():
    return random.sample(comodidades_possiveis, random.randint(4, 8))

def gerar_fotos():
    return random.sample(fotos_exemplo, random.randint(2, 5))

def gerar_regras():
    return random.sample(regras_possiveis, random.randint(2, 4))

def gerar_avaliacoes():
    avaliacoes = []
    for _ in range(random.randint(2, 10)):
        nota = round(random.uniform(3.5, 5.0), 1)
        comentario = random.choice([
            "Ótima estadia, recomendo!",
            "Anfitrião muito atencioso.",
            "Localização excelente, voltaria com certeza.",
            "Apartamento limpo e confortável.",
            "Tive alguns problemas, mas foram resolvidos rapidamente."
        ])
        data = (datetime.now() - timedelta(days=random.randint(1, 365))).strftime("%Y-%m-%d")
        hospede = random.choice(["Lucas", "Mariana", "Pedro", "Juliana", "Rafael", "Camila"])
        avaliacoes.append({"nota": nota, "comentario": comentario, "data": data, "hospede": hospede})
    return avaliacoes

def gerar_endereco():
    cidade = random.choice(cidades)
    bairro = random.choice([b for b in bairros if b in precos_m2.get(cidade, {})] or bairros)
    rua = random.choice(nomes_ruas)
    numero = random.randint(1, 9999)
    cep = f"{random.randint(10000,99999)}-{random.randint(100,999)}"
    complemento = random.choice(["Apto 101", "Casa", "Cobertura", "Fundos", "Bloco B", ""]).strip()
    return {
        "cidade": cidade,
        "bairro": bairro,
        "rua": rua,
        "numero": numero,
        "cep": cep,
        "complemento": complemento
    }

def gerar_lat_lon(cidade):
    bases = {
        "São Paulo": (-23.5505, -46.6333),
        "Rio de Janeiro": (-22.9068, -43.1729),
        "Belo Horizonte": (-19.9167, -43.9345),
        "Curitiba": (-25.4284, -49.2733),
        "Porto Alegre": (-30.0346, -51.2177),
        "Salvador": (-12.9777, -38.5016),
        "Brasília": (-15.7939, -47.8828),
        "Fortaleza": (-3.7172, -38.5433),
        "Recife": (-8.0476, -34.8770),
        "Florianópolis": (-27.5954, -48.5480)
    }
    base = bases.get(cidade, (-23.0, -46.0))
    lat = base[0] + random.uniform(-0.02, 0.02)
    lon = base[1] + random.uniform(-0.02, 0.02)
    return round(lat, 6), round(lon, 6)

def gerar_disponibilidade():
    hoje = datetime.now()
    blocos = []
    for _ in range(random.randint(3, 8)):
        inicio = hoje + timedelta(days=random.randint(7, 90))
        fim = inicio + timedelta(days=random.randint(2, 14))
        blocos.append({"inicio": inicio.strftime("%Y-%m-%d"), "fim": fim.strftime("%Y-%m-%d")})
    return blocos

def gerar_imovel():
    tipo = random.choice(tipos)
    endereco = gerar_endereco()
    cidade = endereco["cidade"]
    quartos = random.randint(1, 5)
    banheiros = random.randint(1, 4)
    vagas = random.randint(0, 3)
    area = random.randint(30, 300) if tipo == "Apartamento" else random.randint(50, 500)
    preco_m2 = preco_m2_por_bairro(cidade, endereco["bairro"])
    preco = int(area * preco_m2 * random.uniform(0.9, 1.2))
    anfitriao = random.choice(anfitrioes)
    camas = random.randint(1, quartos + 2)
    tipo_cama = random.choice(tipos_cama)
    ano_construcao = random.randint(1970, 2023)
    andar = random.randint(0, 20) if tipo == "Apartamento" else 0
    condominio = random.randint(200, 2000) if tipo == "Apartamento" else 0
    iptu = random.randint(50, 600)
    mobiliado = random.choice([True, False])
    dist_metro = round(random.uniform(0.1, 5.0), 2)
    dist_onibus = round(random.uniform(0.05, 2.0), 2)
    max_hospedes = random.randint(quartos, quartos * 2 + 2)
    tempo_anuncio = random.randint(1, 48)
    status = random.choice(["ativo", "inativo"])
    tags = random.sample(tags_possiveis, random.randint(1, 4))
    disponibilidade = gerar_disponibilidade()
    lat, lon = gerar_lat_lon(cidade)
    return {
        "tipo": tipo,
        "endereco": endereco,
        "quartos": quartos,
        "banheiros": banheiros,
        "vagas_garagem": vagas,
        "area_m2": area,
        "preco_aluguel": preco,
        "descricao": random.choice(descricoes),
        "comodidades": gerar_comodidades(),
        "fotos": gerar_fotos(),
        "avaliacoes": gerar_avaliacoes(),
        "nota_media": round(random.uniform(3.5, 5.0), 2),
        "regras_casa": gerar_regras(),
        "camas": camas,
        "tipo_cama": tipo_cama,
        "politica_cancelamento": random.choice(politicas_cancelamento),
        "anfitriao": anfitriao,
        "wifi": True,
        "checkin": f"{random.randint(13,16)}:00",
        "checkout": f"{random.randint(10,12)}:00",
        "ano_construcao": ano_construcao,
        "andar": andar,
        "condominio": condominio,
        "iptu": iptu,
        "mobiliado": mobiliado,
        "distancia_metro_km": dist_metro,
        "distancia_onibus_km": dist_onibus,
        "max_hospedes": max_hospedes,
        "tempo_anuncio_meses": tempo_anuncio,
        "status": status,
        "latitude": lat,
        "longitude": lon,
        "tags": tags,
        "disponibilidade": disponibilidade
    }

def gerar_lista_imoveis(qtd=20):
    return [gerar_imovel() for _ in range(qtd)]

if __name__ == "__main__":
    dados = gerar_lista_imoveis(10)
    with open("imoveis_gerados.json", "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)
    print(json.dumps(dados[0], ensure_ascii=False, indent=2))