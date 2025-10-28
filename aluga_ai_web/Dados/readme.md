# Dados do Projeto Aluga_Ai

Esta pasta contém os arquivos de dados utilizados e gerados pelo pipeline do projeto Aluga_Ai.

## Estrutura da pasta

- `raw/` — Dados brutos originais, como arquivos JSON ou CSV gerados/simulados.
- `processed/` — Dados processados e prontos para uso em ETL, EDA e treinamento de modelos.
    - `dataset_final.csv` — Dataset final processado, utilizado para análise e modelagem. Pode ser versionado via DVC.
- `readme.md` — Este arquivo de documentação.

## Modificações recentes

- Adicionada a versão final do dataset (`dataset_final.csv`) na pasta `processed/`.
- Configurado o versionamento do dataset via DVC, garantindo reprodutibilidade e controle de versões dos dados.
- Atualizado o `.gitignore` para ignorar apenas o arquivo CSV, mantendo o controle do arquivo `.dvc` pelo Git.
- Documentada a estrutura das pastas e o fluxo de versionamento de dados.

## Observações

- Para reprocessar ou atualizar os dados, utilize os scripts ETL e EDA presentes na pasta `Dados/`.
- O arquivo `dataset_final.csv` pode ser restaurado a qualquer versão usando DVC.
- Não faça commit manual do arquivo CSV, apenas do `.dvc` e do `.gitignore`.

## Comandos úteis

- Adicionar novo dataset ao DVC:
  ```sh
  dvc add aluga_ai_web/Dados/processed/dataset_final.csv
  git add aluga_ai_web/Dados/processed/dataset_final.csv.dvc .gitignore
  git commit -m "Atualiza dataset_final.csv via DVC"
  ```
- Restaurar versão do dataset:
  ```sh
  dvc checkout
  ```

---

Dúvidas? Consulte a documentação do projeto ou peça ajuda ao responsável pelo pipeline de dados.
