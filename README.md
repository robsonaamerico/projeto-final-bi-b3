# 📈 B3 Analytics — Dashboard de Business Intelligence e Análise Financeira

![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.32%2B-FF4B4B)
![Plotly](https://img.shields.io/badge/Plotly-5.18%2B-3F4F75)
![Status](https://img.shields.io/badge/Status-Conclu%C3%ADdo-brightgreen)

## 🎯 1. Objetivo do Projeto e Problema de Negócio
Investidores e analistas de mercado frequentemente enfrentam dificuldades para consolidar, comparar e visualizar indicadores técnicos de múltiplos ativos da Bolsa de Valores Brasileira (**B3**) de forma ágil. 

Este **Data App de Business Intelligence**, desenvolvido como Projeto Final do programa **SCTEC (Análise de Dados e Business Intelligence)**, resolve esse problema automatizando a captura de cotações históricas via API (`yfinance`), realizando o tratamento e a engenharia de atributos financeiros e disponibilizando um painel interativo em **Streamlit** para suporte à tomada de decisão baseada em dados.

🔗 **Acesse a aplicação online (Deploy):** [Insira aqui o link do seu app no Streamlit Community Cloud após o deploy]

---

## 🏗️ 2. Arquitetura e Estrutura do Repositório

O projeto segue boas práticas de Engenharia e Ciência de Dados, separando a camada de ingestão/tratamento (ETL), exploração estatística (EDA) e visualização (Data App):

```text
projeto-final-bi-b3/
├── .streamlit/
│   └── secrets.toml.example   # Modelo de configuração de credenciais seguras
├── data/
│   └── b3_acoes_tratadas.csv  # Dataset processado com indicadores calculados
├── notebooks/
│   └── eda.ipynb              # Análise Exploratória de Dados (EDA) e prototipagem
├── src/
│   └── etl.py                 # Pipeline de extração (yfinance), limpeza e feature engineering
├── .gitignore                 # Proteção contra envio de ambientes virtuais e senhas
├── app.py                     # Aplicação principal do Dashboard em Streamlit
├── requirements.txt           # Dependências do ambiente para reprodutibilidade e deploy
└── README.md                  # Documentação técnica e guia de execução
```

---

## ⚙️ 3. Pipeline de Dados (ETL) e Indicadores (KPIs)

O módulo `src/etl.py` extrai os últimos 2 anos de cotações diárias de 8 ativos representativos de diferentes setores da B3 (`PETR4`, `VALE3`, `ITUB4`, `BBDC4`, `BBAS3`, `WEGE3`, `ABEV3`, `RENT3`) e calcula:

* **Retorno Diário (%):** Variação percentual diária do preço de fechamento (`pct_change`).
* **Médias Móveis (MM20 e MM50):** Tendências de curto (20 pregões) e médio prazo (50 pregões).
* **Volatilidade Histórica (20d):** Desvio padrão móvel de 20 dias dos retornos diários para mensuração de risco.
* **Performance Relativa (Base 100):** Normalização das cotações no ponto inicial do filtro para comparação justa entre ações de diferentes faixas de preço.

---

## 📊 4. Funcionalidades do Dashboard (`app.py`)

* **Cache Inteligente (`@st.cache_data`):** Otimização de leitura para carregamento instantâneo nas interações do usuário.
* **Filtros Globais Dinâmicos:** Seleção por Setor Econômico, Múltiplos Ativos (Tickers) e Recorte Temporal.
* **Cartões Executivos (KPIs):** Retorno médio da seleção, ativo destaque de alta, ativo de maior volatilidade e volume financeiro movimentado.
* **Aba 1 — Análise Técnica e Tendência:** Gráfico *Candlestick* (OHLC) sobreposto às Médias Móveis de 20 e 50 dias e gráfico de linha comparativo na Base 100.
* **Aba 2 — Risco, Retorno e Correlação:** Gráfico de dispersão (*Scatter Plot*) cruzando Volatilidade vs. Retorno Médio e Matriz de Correlação (*Heatmap*) para diversificação de carteira.
* **Aba 3 — Auditoria e Exportação:** Tabela interativa dos dados filtrados com botão para download imediato em formato `.csv`.

---

## 🚀 5. Como Executar o Projeto Localmente

### Pré-requisitos
* Python 3.10 ou superior instalado
* Git instalado

### Passo a Passo

```bash
# 1. Clone o repositório
git clone [https://github.com/robsonaamerico/projeto-final-bi-b3.git](https://github.com/robsonaamerico/projeto-final-bi-b3.git)
cd projeto-final-bi-b3

# 2. Crie e ative o ambiente virtual
python -m venv .venv
# No Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# No Linux/macOS/Git Bash:
source .venv/bin/activate

# 3. Instale as dependências
pip install -r requirements.txt

# 4. (Opcional) Atualize a base de dados rodando o pipeline ETL
python src/etl.py

# 5. Inicie o servidor do Streamlit
streamlit run app.py
```

---

## 🌿 6. Fluxo de Versionamento (GitFlow)

O desenvolvimento respeitou a estrutura de branches exigida pela rubrica de avaliação:
* `main`: Versão estável de produção conectada ao Streamlit Community Cloud.
* `develop`: Branch de integração contínua das funcionalidades.
* `feature/estrutura-inicial`: Configuração de diretórios, `.gitignore` e dependências.
* `feature/etl-dados`: Construção do extrator e tratamento com `yfinance` e `pandas`.
* `feature/eda-notebook`: Estudo estatístico e visual em Jupyter Notebook.
* `feature/dashboard-streamlit`: Interface analítica com Streamlit e Plotly.
* `feature/documentacao-readme`: Documentação técnica do projeto.

---
**Autor:** Robson de Almeida Américo