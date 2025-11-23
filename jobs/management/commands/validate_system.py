"""
Comando Django para executar o job de validação do sistema
Uso: python manage.py validate_system
"""
from django.core.management.base import BaseCommand
from jobs.tests.validate_recommendation_system import validate_recommendation_system


class Command(BaseCommand):
    help = 'Executa o job de validação do sistema de recomendação'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('Iniciando validação do sistema de recomendação...')
        )
        
        try:
            # Executar validação
            results = validate_recommendation_system()
            
            if results['success']:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Validação concluída com sucesso!\n'
                        f'Testes passaram: {results["tests_passed"]}/{results["total_tests"]}\n'
                        f'Tempo de execução: {results["execution_time"]:.2f}s'
                    )
                )
            else:
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Validação falhou!\n'
                        f'Testes passaram: {results["tests_passed"]}/{results["total_tests"]}\n'
                        f'Tempo de execução: {results["execution_time"]:.2f}s\n'
                        f'Erros: {", ".join(results["errors"])}'
                    )
                )
                raise Exception('Validação falhou')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erro durante validação: {str(e)}')
            )
            raise
