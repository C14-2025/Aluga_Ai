from django.core.management.base import BaseCommand

from recomendacoes.services.ml.monitoring import read_last


class Command(BaseCommand):
    help = 'Mostra as últimas N predições registradas pelo sistema.'

    def add_arguments(self, parser):
        parser.add_argument('--n', type=int, default=20, help='Número de entradas')

    def handle(self, *args, **options):
        n = options.get('n', 20)
        entries = read_last(n)
        if not entries:
            self.stdout.write('Nenhuma predição registrada.')
            return
        for e in entries:
            self.stdout.write(str(e))
