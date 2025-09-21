import pytest
from unittest.mock import Mock, patch
from BancoDeDados.Integracao import (
    obter_dados_tabela, 
    inserir_em_lotes, 
    testar_tabela
)

class TestIntegracaoBancoDados:
    
    @patch('BancoDeDados.Integracao.supabase')
    def test_obter_dados_tabela_sucesso(self, mock_supabase):
        """Teste 1: Verificar se obter_dados_tabela retorna dados corretamente"""
        # Arrange
        mock_response = Mock()
        mock_response.data = [
            {"id": 1, "tipo": "Apartamento", "preco_aluguel": 1500},
            {"id": 2, "tipo": "Casa", "preco_aluguel": 2000}
        ]
        
        mock_table = Mock()
        mock_table.select.return_value.range.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_table
        
        # Act
        resultado = obter_dados_tabela("ImoveisDisponiveis", "*", 1000)
        
        # Assert
        assert len(resultado) == 2
        assert resultado[0]["tipo"] == "Apartamento"
        assert resultado[1]["preco_aluguel"] == 2000
        mock_supabase.table.assert_called_with("ImoveisDisponiveis")
    
    @patch('BancoDeDados.Integracao.supabase')
    def test_inserir_em_lotes_falha_conexao(self, mock_supabase):
        """Teste 2: Verificar tratamento de erro na inserção em lotes"""
        # Arrange
        mock_response = Mock()
        mock_response.data = None  # Simula falha na inserção
        
        mock_table = Mock()
        mock_table.insert.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_table
        
        dados_teste = [
            {"tipo": "Apartamento", "preco_aluguel": 1500},
            {"tipo": "Casa", "preco_aluguel": 2000}
        ]
        
        # Act & Assert
        with pytest.raises(RuntimeError, match="Inserção interrompida"):
            inserir_em_lotes("ImoveisDisponiveis", dados_teste, 500)
    
    @patch('BancoDeDados.Integracao.supabase')
    def test_testar_tabela_tabela_vazia(self, mock_supabase, capsys):
        """Teste 3: Verificar comportamento quando tabela está vazia"""
        # Arrange
        mock_response = Mock()
        mock_response.data = []  # Tabela vazia
        
        mock_table = Mock()
        mock_table.select.return_value.limit.return_value.execute.return_value = mock_response
        mock_supabase.table.return_value = mock_table
        
        # Act
        testar_tabela("TabelaVazia")
        
        # Assert
        captured = capsys.readouterr()
        assert "Tabela acessível (vazia)." in captured.out
        mock_supabase.table.assert_called_with("TabelaVazia")
        mock_table.select.assert_called_with("*")
        mock_table.select.return_value.limit.assert_called_with(1)

    @patch('BancoDeDados.Integracao.supabase')
    def test_obter_dados_tabela_multiplos_lotes(self, mock_supabase):
        """Teste Bônus: Verificar paginação com múltiplos lotes"""
        # Arrange
        # Primeiro lote
        mock_response1 = Mock()
        mock_response1.data = [{"id": i} for i in range(1, 6)]  # 5 registros
        
        # Segundo lote (menor que batch, indica fim)
        mock_response2 = Mock()
        mock_response2.data = [{"id": 6}, {"id": 7}]  # 2 registros
        
        mock_table = Mock()
        mock_table.select.return_value.range.return_value.execute.side_effect = [
            mock_response1, mock_response2
        ]
        mock_supabase.table.return_value = mock_table
        
        # Act
        resultado = obter_dados_tabela("ImoveisDisponiveis", "*", 5)
        
        # Assert
        assert len(resultado) == 7
        assert resultado[0]["id"] == 1
        assert resultado[6]["id"] == 7
        # Verifica se foi chamado com os ranges corretos
        calls = mock_table.select.return_value.range.call_args_list
        assert calls[0].args == (0, 4)  # primeiro lote: 0-4
        assert calls[1].args == (5, 9)  # segundo lote: 5-9