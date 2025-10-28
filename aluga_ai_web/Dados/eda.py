import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.preprocessing import StandardScaler
import numpy as np  # Necessário para a transformação de log

# O Path continua igual, assumindo que o JSON está em /raw/
try:
    RAW_PATH = Path(__file__).resolve().parent / 'raw' / 'imoveis_gerados.json'
except NameError:
    # Fallback para caso seja executado em um notebook (onde __file__ não existe)
    RAW_PATH = Path.cwd() / 'raw' / 'imoveis_gerados.json'
    if not RAW_PATH.exists():
         RAW_PATH = Path.cwd() / 'imoveis_gerados.json'


def carregar_dados():
    """Carrega os dados brutos do arquivo JSON."""
    if not RAW_PATH.exists():
        print(f"Erro: Arquivo não encontrado em {RAW_PATH}")
        print("Certifique-se que 'imoveis_gerados.json' está na pasta correta.")
        return pd.DataFrame() # Retorna DF vazio para evitar crash
        
    with open(RAW_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    df = pd.json_normalize(data)
    print(f"Dados carregados de {RAW_PATH}. Shape inicial: {df.shape}")
    return df


class Eda:
    def __init__(self, df: pd.DataFrame):
        """Inicializa a classe com o DataFrame carregado."""
        self.df = df

    def limpar_colunas_features(self):
        """
        Renomeia colunas aninhadas (ex: 'endereco.cidade' -> 'endereco_cidade')
        e cria novas features a partir de listas (comodidades, avaliacoes)
        e objetos (anfitriao).
        """
        print("Iniciando limpeza de colunas e engenharia de features...")
        df = self.df
        
        # 1. Renomear colunas aninhadas
        df.columns = df.columns.str.replace('endereco.', 'endereco_', regex=False)
        df.columns = df.columns.str.replace('anfitriao.', 'anfitriao_', regex=False)

        # 2. Engenharia de Features (a partir de listas)
        if 'comodidades' in df.columns:
            df['num_comodidades'] = df['comodidades'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        else:
            df['num_comodidades'] = 0

        if 'avaliacoes' in df.columns:
            df['num_avaliacoes'] = df['avaliacoes'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        else:
            df['num_avaliacoes'] = 0

        if 'fotos' in df.columns:
            df['num_fotos'] = df['fotos'].apply(lambda x: len(x) if isinstance(x, list) else 0)
        else:
            df['num_fotos'] = 0

        # 3. Feature Anfitrião (Superhost)
        if 'anfitriao_superhost' not in df.columns:
            df['anfitriao_superhost'] = False # Default se não existir
        df['anfitriao_superhost'] = df['anfitriao_superhost'].astype(int)
        
        # 4. Remover colunas originais que não serão mais usadas
        cols_para_remover = ['comodidades', 'avaliacoes', 'fotos', 'regras_casa', 'anfitriao_sobre', 'descricao']
        cols_existentes_para_remover = [col for col in cols_para_remover if col in df.columns]
        df = df.drop(columns=cols_existentes_para_remover)

        self.df = df
        print("Limpeza e features concluídas.")

    def explodir_disponibilidade(self):
        """Expande a coluna 'disponibilidade' para linhas individuais."""
        print("Iniciando 'explode' da coluna disponibilidade...")
        df = self.df
        df = df.explode('disponibilidade').reset_index(drop=True)
        df = df[df['disponibilidade'].notnull()]
        
        # Normaliza a coluna 'disponibilidade' (que agora é um dict)
        disp_df = pd.json_normalize(df['disponibilidade'])
        disp_df.columns = ['disp_' + col for col in disp_df.columns]
        
        # Concatena de volta ao DF principal
        df = pd.concat([df.drop('disponibilidade', axis=1), disp_df], axis=1)
        
        # Remove colunas de listas aninhadas que podem ter sobrado
        if 'disp_precos_diarios' in df.columns:
             df = df.drop(columns=['disp_precos_diarios'])

        self.df = df
        print(f"Explode concluído. Novo shape: {self.df.shape}")

    def preparar_dados(self):
        """Executa os passos iniciais de preparação e transformação."""
        self.limpar_colunas_features()
        self.explodir_disponibilidade()

    def estatisticas_basicas(self):
        """Imprime estatísticas básicas e valores faltantes do DataFrame."""
        print("\n--- Estatísticas Básicas ---")
        df = self.df
        print('Shape:', df.shape)
        
        print('\nInfo:')
        df.info()

        print('\nValores Faltantes (NaN):')
        print(df.isnull().sum().sort_values(ascending=False))

        print('\nValores Únicos (Cardinalidade):')
        cols_cardinalidade = ['endereco_cidade', 'endereco_bairro', 'tipo', 'politica_cancelamento']
        for col in cols_cardinalidade:
            if col in df.columns:
                print(f"- {col}: {df[col].nunique()} valores únicos")

        print('\nDescribe (Estatísticas Descritivas):')
        print(df.describe(include='all'))
        print("------------------------------\n")

    def visualizacoes(self):
        """Gera as visualizações da EDA."""
        print("Gerando visualizações... (As janelas podem abrir separadamente)")
        df = self.df

        # 1. Histograma (Original)
        plt.figure(figsize=(10, 5))
        sns.histplot(df['disp_preco_aluguel'], bins=50, kde=True)
        plt.title('Distribuição do Preço do Aluguel (Original)')
        plt.xlabel('Preço do Aluguel')
        plt.ylabel('Frequência')
        plt.tight_layout()
        plt.show()

        # 2. Histograma (Log-Transformado)
        df_temp = df.copy()
        df_temp['disp_preco_aluguel_log'] = np.log1p(df_temp['disp_preco_aluguel'])
        plt.figure(figsize=(10, 5))
        sns.histplot(df_temp['disp_preco_aluguel_log'], bins=50, kde=True, color='green')
        plt.title('Distribuição do Preço do Aluguel (Log-Transformado)')
        plt.xlabel('Log(Preço do Aluguel + 1)')
        plt.ylabel('Frequência')
        plt.tight_layout()
        plt.show()

        # 3. Boxplot (Preço por Tipo)
        plt.figure(figsize=(10, 5))
        sns.boxplot(x='tipo', y='disp_preco_aluguel', data=df)
        plt.title('Preço do Aluguel por Tipo de Imóvel')
        plt.tight_layout()
        plt.show()

        # 4. Countplot (Imóveis por Cidade)
        plt.figure(figsize=(10, 5))
        # Limitar às 10 cidades mais frequentes para legibilidade
        top_10_cidades = df['endereco_cidade'].value_counts().index[:10]
        sns.countplot(x='endereco_cidade', data=df, order=top_10_cidades)
        plt.title('Quantidade de Imóveis por Cidade (Top 10)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        # 5. Geolocalização
        if 'latitude' in df.columns and 'longitude' in df.columns:
            plt.figure(figsize=(10, 8))
            sns.scatterplot(data=df, x='longitude', y='latitude', hue='disp_preco_aluguel', 
                            size='disp_preco_aluguel', palette='viridis', alpha=0.5, sizes=(20, 500))
            plt.title('Preço do Aluguel por Localização Geográfica')
            plt.tight_layout()
            plt.show()

        # 6. Heatmap (Matriz de Correlação)
        num_cols = [
            'quartos', 'banheiros', 'vagas_garagem', 'area_m2', 'nota_media', 'camas', 
            'condominio', 'iptu', 'max_hospedes',
            'num_comodidades', 'num_avaliacoes', 'num_fotos', 'anfitriao_superhost'
        ]
        num_cols_existentes = [col for col in num_cols if col in df.columns]
        
        plt.figure(figsize=(12, 10))
        sns.heatmap(df[num_cols_existentes + ['disp_preco_aluguel']].corr(), 
                    annot=True, cmap='coolwarm', fmt='.2f', annot_kws={"size": 8})
        plt.title('Matriz de Correlação')
        plt.tight_layout()
        plt.show()
        
        print("Visualizações concluídas.")

    def analisar(self):
        """Executa a análise exploratória (estatísticas e gráficos)."""
        self.estatisticas_basicas()
        self.visualizacoes()

    def processar_para_modelagem(self, salvar_csv=True):
        """Prepara o DataFrame final para modelagem, com imputação e scaling."""
        print("Iniciando preparação para modelagem...")
        # Usar uma cópia para não alterar o self.df da classe
        df_model = self.df.copy()

        # 1. Definir features e target
        features = [
            'quartos', 'banheiros', 'vagas_garagem', 'area_m2', 'nota_media', 'camas', 'condominio', 'iptu',
            'max_hospedes', 'tempo_anuncio_meses', 'latitude', 'longitude', 'endereco_cidade', 'endereco_bairro',
            'tipo', 'politica_cancelamento', 'tipo_cama', 'status', 'disp_alta_demanda',
            'num_comodidades', 'num_avaliacoes', 'num_fotos', 'anfitriao_superhost'
        ]
        target = 'disp_preco_aluguel'
        target_log = 'disp_preco_aluguel_log'
        
        # 2. Criar target log-transformado
        df_model[target_log] = np.log1p(df_model[target])

        # 3. Filtrar apenas colunas existentes
        features_existentes = [col for col in features if col in df_model.columns]
        df_model = df_model[features_existentes + [target_log, target]].copy()

        # 4. Tratamento de Missing Values (Imputação Inteligente)
        print("Aplicando imputação de dados faltantes...")
        num_cols_impute = ['quartos', 'banheiros', 'area_m2', 'nota_media', 'camas', 'max_hospedes', 'latitude', 'longitude']
        for col in num_cols_impute:
            if col in df_model.columns:
                median = df_model[col].median()
                df_model[col] = df_model[col].fillna(median)
        
        zero_cols_impute = ['vagas_garagem', 'condominio', 'iptu']
        for col in zero_cols_impute:
            if col in df_model.columns:
                df_model[col] = df_model[col].fillna(0)
        
        cat_cols_impute = ['endereco_cidade', 'endereco_bairro', 'tipo', 'politica_cancelamento', 'tipo_cama', 'status']
        for col in cat_cols_impute:
            if col in df_model.columns:
                mode = df_model[col].mode()[0]
                df_model[col] = df_model[col].fillna(mode)
        
        # Captura geral final para qualquer outra coluna (ex: tempo_anuncio_meses)
        df_model = df_model.fillna(0)
        
        # 5. One-Hot Encoding para categóricas
        print("Aplicando One-Hot Encoding...")
        cat_cols = ['endereco_cidade', 'endereco_bairro', 'tipo', 'politica_cancelamento', 'tipo_cama', 'status']
        cat_cols_existentes = [col for col in cat_cols if col in df_model.columns]
        df_model = pd.get_dummies(df_model, columns=cat_cols_existentes, drop_first=True)

        # 6. Scaling de colunas numéricas
        print("Aplicando StandardScaler...")
        scaler = StandardScaler()
        num_cols_scale = [col for col in df_model.columns if 
                          col not in [target, target_log] and 
                          df_model[col].dtype not in ['uint8', 'bool', 'object']]
        
        if num_cols_scale:
            df_model[num_cols_scale] = scaler.fit_transform(df_model[num_cols_scale])

        if salvar_csv:
            out_dir = Path('processed')
            out_dir.mkdir(parents=True, exist_ok=True)
            df_model.to_csv(out_dir / 'dataset_final.csv', index=False)
            
        
        print("Processamento para modelagem concluído.")
        return df_model


if __name__ == '__main__':
    # 1. Carregar os dados
    df_raw = carregar_dados()
    
    if not df_raw.empty:
        # 2. Iniciar a classe de EDA
        eda = Eda(df_raw)
        
        # 3. Executar a preparação (limpeza, features, explode)
        eda.preparar_dados()
        
        # 4. Executar a análise (estatísticas, gráficos)
        eda.analisar()
        
        # 5. Processar e salvar o dataset final
        df_model_ready = eda.processar_para_modelagem(salvar_csv=True)
        
        print("\n--- Processo de EDA e Pré-processamento Concluído ---")
        print("Dataset final para modelagem (head):")
        print(df_model_ready.head())
    else:
        print("Processo interrompido pois o arquivo de dados não foi carregado.")