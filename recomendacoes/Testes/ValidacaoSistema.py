"""
Job simples de validação do sistema de recomendação
Este job testa se o sistema de recomendação está funcionando corretamente
"""
import os
import sys
import json
import logging
from datetime import datetime
from typing import Dict, Any

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def validate_recommendation_system() -> Dict[str, Any]:
    """
    Valida se o sistema de recomendação está funcionando
    
    Returns:
        Dict com resultados da validação
    """
    results = {
        'success': False,
        'tests_passed': 0,
        'tests_failed': 0,
        'total_tests': 0,
        'errors': [],
        'execution_time': 0,
        'timestamp': datetime.now().isoformat()
    }
    
    start_time = datetime.now()
    
    try:
        logger.info("=== INICIANDO VALIDAÇÃO DO SISTEMA DE RECOMENDAÇÃO ===")
        
        # Teste 1: Verificar se os arquivos necessários existem
        results['total_tests'] += 1
        if test_required_files():
            results['tests_passed'] += 1
            logger.info("OK Teste 1: Arquivos necessarios encontrados")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Arquivos necessarios nao encontrados")
            logger.error("ERRO Teste 1: Arquivos necessarios nao encontrados")
        
        # Teste 2: Verificar se o modelo pode ser carregado
        results['total_tests'] += 1
        if test_model_loading():
            results['tests_passed'] += 1
            logger.info("OK Teste 2: Modelo carregado com sucesso")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Erro ao carregar modelo")
            logger.error("ERRO Teste 2: Erro ao carregar modelo")
        
        # Teste 3: Testar predição de preço
        results['total_tests'] += 1
        if test_price_prediction():
            results['tests_passed'] += 1
            logger.info("OK Teste 3: Predicao de preco funcionando")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Erro na predicao de preco")
            logger.error("ERRO Teste 3: Erro na predicao de preco")
        
        # Teste 4: Testar sistema de recomendação
        results['total_tests'] += 1
        if test_recommendation_system():
            results['tests_passed'] += 1
            logger.info("OK Teste 4: Sistema de recomendacao funcionando")
        else:
            results['tests_failed'] += 1
            results['errors'].append("Erro no sistema de recomendacao")
            logger.error("ERRO Teste 4: Erro no sistema de recomendacao")
        
        # Determinar sucesso geral
        results['success'] = results['tests_failed'] == 0
        
        execution_time = (datetime.now() - start_time).total_seconds()
        results['execution_time'] = execution_time
        
        # Log final
        if results['success']:
            logger.info(f"=== VALIDACAO CONCLUIDA COM SUCESSO ===")
            logger.info(f"Tempo de execucao: {execution_time:.2f}s")
            logger.info(f"Testes passaram: {results['tests_passed']}/{results['total_tests']}")
        else:
            logger.error(f"=== VALIDACAO FALHOU ===")
            logger.error(f"Tempo de execucao: {execution_time:.2f}s")
            logger.error(f"Testes passaram: {results['tests_passed']}/{results['total_tests']}")
            logger.error(f"Erros: {', '.join(results['errors'])}")
        
        return results
        
    except Exception as e:
        execution_time = (datetime.now() - start_time).total_seconds()
        results['execution_time'] = execution_time
        results['errors'].append(f"Erro inesperado: {str(e)}")
        logger.error(f"Erro inesperado durante validação: {str(e)}")
        return results


def test_required_files() -> bool:
    """Testa se os arquivos necessários existem"""
    try:
        required_files = [
            'recomendacoes/services/ml/services/model.py',
            'recomendacoes/services/ml/services/recommender.py',
            'recomendacoes/services/ml/services/data_loader.py',
            'recomendacoes/services/data/sample_properties.csv'
        ]
        
        for file_path in required_files:
            if not os.path.exists(file_path):
                logger.error(f"Arquivo não encontrado: {file_path}")
                return False
        
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar arquivos: {str(e)}")
        return False


def test_model_loading() -> bool:
    """Testa se o modelo pode ser carregado"""
    try:
        # Tentar importar e instanciar o modelo
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Configurar variável de ambiente para dados
        os.environ['ALUGAAI_DADOS_JSON'] = 'aluga_ai_web/Dados/raw/imoveis_gerados.json'
        
        from recomendacoes.services.ml.services.model import PriceModel
        
        # Tentar carregar o modelo
        model = PriceModel.instance()
        
        if model is None:
            return False
        
        logger.info(f"Modelo carregado com metodo: {model.method}")
        return True
        
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {str(e)}")
        return False


def test_price_prediction() -> bool:
    """Testa se a predição de preço funciona"""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Configurar variável de ambiente para dados
        os.environ['ALUGAAI_DADOS_JSON'] = 'aluga_ai_web/Dados/raw/imoveis_gerados.json'
        
        from recomendacoes.services.ml.services.model import PriceModel
        
        model = PriceModel.instance()
        
        # Dados de teste
        test_features = {
            'tipo': 'apartment',
            'cidade': 'Sao Paulo',
            'area_m2': 60.0,
            'quartos': 2,
            'banheiros': 1,
            'vagas_garagem': 1,
            'condominio': 300.0,
            'iptu': 200.0
        }
        
        # Fazer predição
        price, method, details = model.predict(test_features, return_details=True)
        
        if price <= 0:
            logger.error(f"Preco predito invalido: {price}")
            return False
        
        logger.info(f"Preco predito: R$ {price:.2f} (metodo: {method})")
        return True
        
    except Exception as e:
        logger.error(f"Erro na predicao de preco: {str(e)}")
        return False


def test_recommendation_system() -> bool:
    """Testa se o sistema de recomendação funciona"""
    try:
        sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Configurar variável de ambiente para dados
        os.environ['ALUGAAI_DADOS_JSON'] = 'aluga_ai_web/Dados/raw/imoveis_gerados.json'
        
        from recomendacoes.services.ml.services.model import PriceModel
        from recomendacoes.services.ml.services.recommender import recommend
        
        model = PriceModel.instance()
        
        # Dados de teste para recomendação
        test_candidates = [
            {
                "id": 1,
                "title": "Apartamento Teste",
                "city": "Sao Paulo",
                "neighborhood": "Centro",
                "area": 60.0,
                "bedrooms": 2,
                "bathrooms": 1,
                "parking": 1,
                "property_type": "apartment"
            }
        ]
        
        # Testar recomendação
        recommendations = recommend(
            model=model,
            candidates=test_candidates,
            budget=3000.0,
            city="Sao Paulo",
            limit=5
        )
        
        if not recommendations:
            logger.error("Nenhuma recomendacao retornada")
            return False
        
        if len(recommendations) == 0:
            logger.error("Lista de recomendacoes vazia")
            return False
        
        logger.info(f"Recomendacoes geradas: {len(recommendations)}")
        for rec in recommendations:
            logger.info(f"- {rec['title']}: R$ {rec['predicted_price']:.2f} (score: {rec['score']})")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro no sistema de recomendacao: {str(e)}")
        return False


def main():
    """Função principal para execução do job"""
    print("=== JOB DE VALIDAÇÃO DO SISTEMA DE RECOMENDAÇÃO ===")
    print(f"Iniciado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print()
    
    # Executar validação
    results = validate_recommendation_system()
    
    # Exibir resultados
    print("\n=== RESULTADOS ===")
    print(f"Sucesso: {'SIM' if results['success'] else 'NÃO'}")
    print(f"Testes passaram: {results['tests_passed']}/{results['total_tests']}")
    print(f"Tempo de execução: {results['execution_time']:.2f}s")
    
    if results['errors']:
        print(f"Erros encontrados: {len(results['errors'])}")
        for error in results['errors']:
            print(f"- {error}")
    
    # Salvar resultados em arquivo JSON
    output_file = 'validation_results.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em: {output_file}")
    
    # Retornar código de saída apropriado
    if results['success']:
        print("\nOK VALIDACAO CONCLUIDA COM SUCESSO")
        sys.exit(0)
    else:
        print("\nERRO VALIDACAO FALHOU")
        sys.exit(1)


if __name__ == "__main__":
    main()
