from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Executa ETL e treina o modelo de recomendações.'

    def add_arguments(self, parser):
        parser.add_argument('--grid', action='store_true', help='Usar Grid Search durante o treino')

    def handle(self, *args, **options):
        self.stdout.write('Iniciando ETL...')
        try:
            from dados.etl import ETLPipeline
            pipeline = ETLPipeline()
            out = pipeline.run()
            self.stdout.write(f'ETL finalizado. Arquivo: {out}')
        except Exception as e:
            self.stderr.write(f'Falha no ETL: {e}')
            raise

        self.stdout.write('Iniciando treino do modelo...')
        try:
            from recomendacoes.train_model import ModelTrainer
            trainer = ModelTrainer()
            if options.get('grid'):
                metrics = trainer.train_grid()
            else:
                metrics = trainer.train_simple()
            self.stdout.write('Treino concluído.')
            self.stdout.write(str(metrics))
        except Exception as e:
            self.stderr.write(f'Falha no treino: {e}')
            raise
