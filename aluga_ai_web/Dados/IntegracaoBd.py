
import os
import sys
import pandas as pd

# Corrigir o sys.path para garantir que o pacote aluga_ai_web seja encontrado
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BASE_DIR not in sys.path:
	sys.path.insert(0, BASE_DIR)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aluga_ai_web.settings")

import django
django.setup()


# Importar modelos
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "aluga_ai_web.settings")

from propriedades.models import Propriedade
from reservas.models import Reserva
from avaliacoes.models import Avaliacao
from django.contrib.auth.models import User
import json

def get_or_create_user(nome, is_host=False):
	username = nome.lower().replace(' ', '_')[:30]
	user, created = User.objects.get_or_create(username=username, defaults={
		'first_name': nome.split(' ')[0],
		'last_name': ' '.join(nome.split(' ')[1:]) if len(nome.split(' ')) > 1 else '',
		'email': f'{username}@fake.com',
	})
	if created:
		user.set_password('123456')
		user.save()
	return user

def importar_propriedades_json(json_path):
	print(f"Importando propriedades do JSON: {json_path}")
	with open(json_path, 'r', encoding='utf-8') as f:
		dados = json.load(f)
	for item in dados:
		if not item or 'anfitriao' not in item:
			continue
		anfitriao = item['anfitriao']
		user = get_or_create_user(anfitriao['nome'], is_host=True)
		endereco = item.get('endereco', {})
		prop, _ = Propriedade.objects.get_or_create(
			owner=user,
			titulo=item.get('tipo', 'Propriedade'),
			defaults={
				'descricao': item.get('descricao', ''),
				'endereco': f"{endereco.get('rua', '')}, {endereco.get('numero', '')}",
				'city': endereco.get('cidade', ''),
				'state': '',
				'preco_por_noite': item.get('preco_aluguel', 0),
				'ativo': True,
			}
		)
		# Reservas
		for reserva in item.get('reservas', []):
			guest = get_or_create_user(reserva.get('hospede', 'Hospede'))
			Reserva.objects.get_or_create(
				guest=guest,
				propriedade=prop,
				inicio=reserva.get('inicio'),
				fim=reserva.get('fim'),
				status=Reserva.STATUS_CONFIRMED
			)
		# Avaliacoes
		for avaliacao in item.get('avaliacoes', []):
			autor = get_or_create_user(avaliacao.get('autor', 'Autor'))
			Avaliacao.objects.get_or_create(
				autor=autor,
				propriedade=prop,
				nota=avaliacao.get('nota', 5),
				comentario=avaliacao.get('comentario', '')
			)
	print("Importação do JSON finalizada.")

def importar_propriedades_csv(csv_path):
	print(f"Importando propriedades do CSV: {csv_path}")
	df = pd.read_csv(csv_path)
	user = get_or_create_user('Dono CSV', is_host=True)
	for _, row in df.iterrows():
		Propriedade.objects.get_or_create(
			owner=user,
			titulo='Propriedade CSV',
			defaults={
				'descricao': '',
				'endereco': '',
				'city': '',
				'state': '',
				'preco_por_noite': 100.0,
				'ativo': True,
			}
		)
	print("Importação do CSV finalizada.")

if __name__ == "__main__":
	# Ajuste os caminhos conforme necessário
	importar_propriedades_json(os.path.join(BASE_DIR, "aluga_ai_web", "Dados", "raw", "imoveis_gerados.json"))
	importar_propriedades_csv(os.path.join(BASE_DIR, "aluga_ai_web", "Dados", "processed", "dataset_final.csv"))